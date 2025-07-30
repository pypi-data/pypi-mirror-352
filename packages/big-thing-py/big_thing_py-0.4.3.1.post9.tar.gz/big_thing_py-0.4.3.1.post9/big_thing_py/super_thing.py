from big_thing_py.big_thing import *
from big_thing_py.super import *
from big_thing_py.common.helper.const import *
from big_thing_py.super.helper.const import *
from big_thing_py.super.helper.util import *

import textwrap


class MXSuperThing(MXBigThing):
    DEFAULT_NAME = 'default_super_thing'
    REFRESH_CYCLE_SCALER = 2.1

    # Super Service Execution 요청이 들어왔을때 mapping_table에 있는 super_request를 찾기 위한 super_service_request_key 리스트
    # Super Service는 자신의 이름으로 super_request_key를 찾을 수 있다.
    # {
    #     'super_service_request_key1': ['subservice_request_key1', 'subservice_request_key2', ...]},
    #     'super_service_request_key2': ['subservice_request_key3', 'subservice_request_key4', ...]},
    #      ...
    # }
    _SUPER_SERVICE_REQUEST_KEY_TABLE: Dict[str, List[str]] = dict()

    def __init__(
        self,
        name: str = MXThing.DEFAULT_NAME,
        nick_name: str = MXThing.DEFAULT_NAME,
        category: DeviceCategory = DeviceCategory.SuperThing,
        device_type: MXDeviceType = MXDeviceType.NORMAL,
        desc: str = '',
        version: str = sdk_version(),
        service_list: List[MXService] = list(),
        alive_cycle: int = 60,
        is_super: bool = True,
        is_ble_wifi: bool = False,
        is_parallel: bool = True,
        is_builtin: bool = False,
        is_manager: bool = False,
        is_staff: bool = False,
        is_matter: bool = False,
        ip: str = '127.0.0.1',
        port: int = 1883,
        ssl_ca_path: str = '',
        ssl_cert_path: str = '',
        ssl_key_path: str = '',
        log_path: str = '',
        log_enable: bool = True,
        log_mode: MXPrintMode = MXPrintMode.ABBR,
        async_log: bool = False,
        append_mac_address: bool = True,
        no_wait_request_register: bool = False,
        kvs_storage_path: str = DEFAULT_KVS_STORAGE_PATH,
        reset_kvs: bool = False,
        refresh_cycle: float = 30,
    ):

        self._hierarchical_service_table: Dict[str, HierarchicalServiceTable] = {}
        self._SUPER_SERVICE_REQUEST_KEY_TABLE = {}

        super().__init__(
            name=name,
            nick_name=nick_name,
            category=category,
            device_type=device_type,
            desc=desc,
            version=version,
            service_list=service_list,
            alive_cycle=alive_cycle,
            is_super=is_super,
            is_ble_wifi=is_ble_wifi,
            is_parallel=is_parallel,
            is_builtin=is_builtin,
            is_manager=is_manager,
            is_staff=is_staff,
            is_matter=is_matter,
            ip=ip,
            port=port,
            ssl_ca_path=ssl_ca_path,
            ssl_cert_path=ssl_cert_path,
            ssl_key_path=ssl_key_path,
            log_path=log_path,
            log_enable=log_enable,
            log_mode=log_mode,
            async_log=async_log,
            append_mac_address=append_mac_address,
            no_wait_request_register=no_wait_request_register,
            kvs_storage_path=kvs_storage_path,
            reset_kvs=reset_kvs,
        )

        self._refresh_cycle = refresh_cycle
        self._last_refresh_time: float = 0.0

        self._receive_queue: Dict[MXProtocolType, asyncio.Queue] = {
            k: asyncio.Queue()
            for k in [
                MXProtocolType.Base.MT_REQUEST_REGISTER_INFO,
                MXProtocolType.Base.MT_REQUEST_UNREGISTER,
                MXProtocolType.Base.MT_RESULT_REGISTER,
                MXProtocolType.Base.MT_RESULT_UNREGISTER,
                MXProtocolType.Base.MT_RESULT_BINARY_VALUE,
                MXProtocolType.Base.MT_EXECUTE,
                MXProtocolType.Super.MS_RESULT_SCHEDULE,
                MXProtocolType.Super.MS_RESULT_EXECUTE,
                MXProtocolType.Super.MS_RESULT_SERVICE_LIST,
                MXProtocolType.Super.MS_SCHEDULE,
                MXProtocolType.Super.MS_EXECUTE,
                MXProtocolType.WebClient.ME_NOTIFY_CHANGE,
                MXProtocolType.WebClient.ME_RESULT_HOME,
            ]
        }

        self._super_task_list: List[Dict[str, asyncio.Task]] = []

    def __eq__(self, o: 'MXSuperThing'):
        instance_check = isinstance(o, MXSuperThing)
        refresh_cycle_check = self._refresh_cycle == o._refresh_cycle

        return super().__eq__(o) and instance_check and refresh_cycle_check

    def __getstate__(self):
        state = super().__getstate__()

        state['_refresh_cycle'] = self._refresh_cycle

        del state['_last_refresh_time']

        return state

    def __setstate__(self, state):
        super().__setstate__(state)

        self._refresh_cycle = state['_refresh_cycle']

        self._last_refresh_time = 0

    @override
    async def _setup(self) -> 'MXSuperThing':
        await self._dry_run_super_functions()
        return await super()._setup()

    # ===========================================================================================
    #  _    _                             _    __                      _    _
    # | |  | |                           | |  / _|                    | |  (_)
    # | |_ | |__   _ __   ___   __ _   __| | | |_  _   _  _ __    ___ | |_  _   ___   _ __   ___
    # | __|| '_ \ | '__| / _ \ / _` | / _` | |  _|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
    # | |_ | | | || |   |  __/| (_| || (_| | | |  | |_| || | | || (__ | |_ | || (_) || | | |\__ \
    #  \__||_| |_||_|    \___| \__,_| \__,_| |_|   \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
    # ===========================================================================================

    @override
    async def _RUNNING_state_process(self):
        # MQTT receive handling
        if not self._receive_queue_empty():
            recv_msg = await self._receive_queue_get()
            error = await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data)
            if not error in MXBigThing.HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST:
                MXLOG_CRITICAL(f'[{get_current_function_name()}] MQTT Message handling failed, error: {error}')

        # Value publish handling
        current_time = get_current_datetime()
        for value in self.value_list:
            # NOTE (thsvkd): If Thing is not Manager of Staff, I think event-based value feature is not needed...
            # elif current_time - value.last_update_time > value.cycle and value.cycle != 0:
            if not value.is_initialized or current_time - value.last_update_time > value.cycle:
                new_value = await value.async_update()
                if new_value is None:
                    continue

                self._send_TM_VALUE_PUBLISH(value)

        # Alive handling
        if current_time - self.last_alive_time > self.alive_cycle / MXBigThing.ALIVE_CYCLE_SCALER:
            self._send_TM_ALIVE(self._thing_data)

        # Refresh hierarchy service list handling
        if current_time - self._last_refresh_time > self._refresh_cycle / MXSuperThing.REFRESH_CYCLE_SCALER:
            self._send_SM_REFRESH()

    # ======================================================================================================================= #
    #  _    _                    _  _         __  __   ____  _______  _______   __  __                                        #
    # | |  | |                  | || |       |  \/  | / __ \|__   __||__   __| |  \/  |                                       #
    # | |__| |  __ _  _ __    __| || |  ___  | \  / || |  | |  | |      | |    | \  / |  ___  ___  ___   __ _   __ _   ___    #
    # |  __  | / _` || '_ \  / _` || | / _ \ | |\/| || |  | |  | |      | |    | |\/| | / _ \/ __|/ __| / _` | / _` | / _ \   #
    # | |  | || (_| || | | || (_| || ||  __/ | |  | || |__| |  | |      | |    | |  | ||  __/\__ \\__ \| (_| || (_| ||  __/   #
    # |_|  |_| \__,_||_| |_| \__,_||_| \___| |_|  |_| \___\_\  |_|      |_|    |_|  |_| \___||___/|___/ \__,_| \__, | \___|   #
    #                                                                                                         __/ |           #
    #                                                                                                         |___/           #
    # ======================================================================================================================= #

    @override
    async def _handle_mqtt_message(self, msg: MQTTMessage, target_thing: MXThing, state_change: bool = True) -> bool:
        topic_string = decode_MQTT_message(msg)[0]
        protocol = MXProtocolType.get(topic_string)

        # Super Schedule
        if protocol == MXProtocolType.Super.MS_SCHEDULE:
            error = await self._handle_MS_SCHEDULE(msg)
        elif protocol == MXProtocolType.Super.MS_RESULT_SCHEDULE:
            error = self._handle_MS_RESULT_SCHEDULE(msg)
        # Super Execute
        elif protocol == MXProtocolType.Super.MS_EXECUTE:
            error = self._handle_MS_EXECUTE(msg)
        elif protocol == MXProtocolType.Super.MS_RESULT_EXECUTE:
            error = self._handle_MS_RESULT_EXECUTE(msg)
        # Sync
        elif protocol == MXProtocolType.Super.MS_RESULT_SERVICE_LIST:
            error = self._handle_MS_RESULT_SERVICE_LIST(msg)
        elif protocol == MXProtocolType.WebClient.ME_NOTIFY_CHANGE:
            error = self._handle_ME_NOTIFY(msg)
        # Exception
        elif protocol == MXProtocolType.Base.MT_EXECUTE:
            MXLOG_WARN(f'[{get_current_function_name()}] Not permitted topic! topic: {topic_string}')
            return False
        else:
            error = await super()._handle_mqtt_message(msg, target_thing=target_thing, state_change=state_change)

        return error

    # ================
    # ___  ___ _____
    # |  \/  |/  ___|
    # | .  . |\ `--.
    # | |\/| | `--. \
    # | |  | |/\__/ /
    # \_|  |_/\____/
    # ================

    # MS/SCHEDULE/[Ss]/[Ths]/[MWs]/[MWr]
    async def _handle_MS_SCHEDULE(self, msg: MQTTMessage) -> MXErrorCode:
        super_schedule_msg = MXSuperScheduleMessage(msg)
        target_super_service = self._get_function(super_schedule_msg.super_service_name)

        if not target_super_service:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Target super function not found! - topic: {decode_MQTT_message(msg)[0]}')
            return MXErrorCode.TARGET_NOT_FOUND
        if self.name != super_schedule_msg.super_thing_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong payload arrive... {self.name} should be arrive, not {super_schedule_msg.super_thing_name}'
            )
            return MXErrorCode.INVALID_REQUEST
        if self.middleware_name != super_schedule_msg.super_middleware_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong super middleware name... {self.middleware_name} should be arrive, not {super_schedule_msg.super_middleware_name}'
            )
            return MXErrorCode.INVALID_REQUEST
        if super_schedule_msg.topic_error or super_schedule_msg.payload_error:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] super schedule msg error! - topic: {decode_MQTT_message(msg)[0]}{super_schedule_msg.topic_error}'
            )
            return MXErrorCode.INVALID_REQUEST

        super_schedule_request = MXSuperScheduleRequest(
            trigger_msg=super_schedule_msg,
            result_msg=MXSuperScheduleResultMessage(
                super_service_name=target_super_service.name,
                super_thing_name=self.name,
                super_middleware_name=self.middleware_name,
                requester_middleware_name=super_schedule_msg.requester_middleware_name,
                scenario=super_schedule_msg.scenario,
            ),
        )

        # 중복된 시나리오로부터 온 스케쥴링 요청이면 -4 에러코드를 보낸다.
        if super_schedule_request.trigger_msg.scenario in target_super_service.running_scenario_list:
            super_schedule_request.result_msg.error = MXErrorCode.DUPLICATE
            self._send_SM_RESULT_SCHEDULE(
                super_service_name=super_schedule_msg.super_service_name,
                super_thing_name=super_schedule_msg.super_thing_name,
                super_middleware_name=super_schedule_msg.super_middleware_name,
                requester_middleware_name=super_schedule_msg.requester_middleware_name,
                scenario=super_schedule_msg.scenario,
                error=super_schedule_request.result_msg.error,
            )
            return super_schedule_request.result_msg.error

        # 병렬스케쥴링이 가능하거나 현재 함수가 스케쥴링 중이지 않으면 함수를 스케쥴링한다.
        if not target_super_service.schedule_running:
            curr_time = get_current_datetime(TimeFormat.DATETIME2)
            MXLOG_INFO(
                f'[SUPER_SCHEDULE REQUEST] Request schedule {target_super_service.name} by {super_schedule_msg.call_requester} at [{curr_time}]',
                success=True,
            )

            self._create_super_schedule_task(target_super_service, super_schedule_request, self._hierarchical_service_table)
        else:
            super_schedule_request.result_msg.error = MXErrorCode.FAIL
            self._send_SM_RESULT_SCHEDULE(
                super_service_name=super_schedule_msg.super_service_name,
                super_thing_name=super_schedule_msg.super_thing_name,
                super_middleware_name=super_schedule_msg.super_middleware_name,
                requester_middleware_name=super_schedule_msg.requester_middleware_name,
                scenario=super_schedule_msg.scenario,
                error=super_schedule_request.result_msg.error,
            )
            return super_schedule_request.result_msg.error

        return MXErrorCode.NO_ERROR

    # MS/RESULT/SCHEDULE/[St]/SUPER/[MWt]/[Rq(MWr@Ths@Ss)]
    def _handle_MS_RESULT_SCHEDULE(self, msg: MQTTMessage) -> MXErrorCode:
        subschedule_result_msg = MXSubScheduleResultMessage(msg)

        call_requester = subschedule_result_msg.call_requester

        target_super_service = self._get_function(subschedule_result_msg.super_service_name)
        if not target_super_service:
            MXLOG_WARN(f'[{get_current_function_name()}] Super Service {subschedule_result_msg.super_service_name} does not exist...')
            return MXErrorCode.TARGET_NOT_FOUND

        if call_requester not in target_super_service.super_schedule_future_table:
            MXLOG_WARN(f'[{get_current_function_name()}] Call requester {call_requester} does not exist in future table...')
            return MXErrorCode.TARGET_NOT_FOUND

        future = target_super_service.super_schedule_future_table[call_requester][subschedule_result_msg.line_num]
        future.set_result(subschedule_result_msg)

        return MXErrorCode.NO_ERROR

    # MS/EXECUTE/[Ss]/[Ths]/[MWs]/[MWr]
    def _handle_MS_EXECUTE(self, msg: MQTTMessage) -> MXErrorCode:
        super_execute_msg = MXSuperExecuteMessage(msg)
        target_super_service = self._get_function(super_execute_msg.super_service_name)

        if not target_super_service:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Target super function not found! - topic: {decode_MQTT_message(msg)[0]}')
            return MXErrorCode.TARGET_NOT_FOUND
        if self.name != super_execute_msg.super_thing_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong payload arrive... {self.name} should be arrive, not {super_execute_msg.super_thing_name}'
            )
            return MXErrorCode.INVALID_REQUEST
        if self.middleware_name != super_execute_msg.super_middleware_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong super middleware name... {self.middleware_name} should be arrive, not {super_execute_msg.super_middleware_name}'
            )
            return MXErrorCode.INVALID_REQUEST
        if super_execute_msg.topic_error or super_execute_msg.payload_error:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] super execute msg error! - topic: {decode_MQTT_message(msg)[0]}{super_execute_msg.topic_error}'
            )
            return MXErrorCode.INVALID_REQUEST

        super_execute_request = MXSuperExecuteRequest(
            trigger_msg=super_execute_msg,
            result_msg=MXSuperExecuteResultMessage(
                super_service_name=target_super_service.name,
                super_thing_name=self.name,
                super_middleware_name=self.middleware_name,
                requester_middleware_name=super_execute_msg.requester_middleware_name,
                scenario=super_execute_msg.scenario,
                return_type=target_super_service.return_type,
                return_value=None,
                error=MXErrorCode.NO_ERROR,
            ),
        )

        # 서로의 arg_list가 일치하는 지 확인한다.
        if not compare_arg_list(target_super_service.arg_list, list(super_execute_request.trigger_msg.tuple_arguments())):
            super_execute_request.result_msg.error = MXErrorCode.EXECUTE_ARG_FAIL
            self._send_SM_RESULT_EXECUTE(
                super_service_name=super_execute_msg.super_service_name,
                super_thing_name=super_execute_msg.super_thing_name,
                super_middleware_name=super_execute_msg.super_middleware_name,
                requester_middleware_name=super_execute_msg.requester_middleware_name,
                scenario=super_execute_msg.scenario,
                return_type=target_super_service.return_type,
                return_value=None,
                error=super_execute_request.result_msg.error,
            )
            return super_execute_request.result_msg.error

        # 중복된 시나리오로부터 온 실행 요청이면 -4 에러코드를 보낸다.
        if super_execute_msg.scenario in target_super_service.running_scenario_list:
            super_execute_request.result_msg.error = MXErrorCode.DUPLICATE
            self._send_SM_RESULT_EXECUTE(
                super_service_name=super_execute_msg.super_service_name,
                super_thing_name=super_execute_msg.super_thing_name,
                super_middleware_name=super_execute_msg.super_middleware_name,
                requester_middleware_name=super_execute_msg.requester_middleware_name,
                scenario=super_execute_msg.scenario,
                return_type=target_super_service.return_type,
                return_value=None,
                error=super_execute_request.result_msg.error,
            )
            return MXErrorCode.NO_ERROR

        if not target_super_service.running:
            curr_time = get_current_datetime(TimeFormat.DATETIME2)
            MXLOG_INFO(
                f'[SUPER_EXECUTE REQUEST] Request execute {target_super_service.name} by {super_execute_msg.call_requester} at [{curr_time}]',
                success=True,
            )

            self._create_super_execute_task(target_super_service, super_execute_request)
        else:
            delattr(target_super_service.func, LINE_NUM_ATTRIBUTE)
            super_execute_request.result_msg.error = MXErrorCode.FAIL
            self._send_SM_RESULT_EXECUTE(
                super_service_name=super_execute_msg.super_service_name,
                super_thing_name=super_execute_msg.super_thing_name,
                super_middleware_name=super_execute_msg.super_middleware_name,
                requester_middleware_name=super_execute_msg.requester_middleware_name,
                scenario=super_execute_msg.scenario,
                return_type=target_super_service.return_type,
                return_value=None,
                error=super_execute_request.result_msg.error,
            )
            return super_execute_request.result_msg.error

        return MXErrorCode.NO_ERROR

    # MS/RESULT/EXECUTE/[St]/SUPER/[MWt]/[Rq(MWr@Ths@Ss@Ln-Eo)]
    def _handle_MS_RESULT_EXECUTE(self, msg: MQTTMessage) -> MXErrorCode:
        subexecute_result_msg = MXSubExecuteResultMessage(msg)

        call_requester = subexecute_result_msg.call_requester
        line_num = subexecute_result_msg.line_num
        execute_order = subexecute_result_msg.execute_order

        target_super_service = self._get_function(subexecute_result_msg.super_service_name)
        if not target_super_service:
            MXLOG_WARN(f'[{get_current_function_name()}] Super Service {subexecute_result_msg.super_service_name} does not exist...')
            return MXErrorCode.TARGET_NOT_FOUND

        if call_requester not in target_super_service.super_execute_future_table:
            MXLOG_WARN(f'[{get_current_function_name()}] Call requester {call_requester} does not exist in future table...')
            return MXErrorCode.TARGET_NOT_FOUND

        future = target_super_service.super_execute_future_table[call_requester][line_num][execute_order]
        future.set_result(subexecute_result_msg)

        return MXErrorCode.NO_ERROR

    def _handle_MS_RESULT_SERVICE_LIST(self, msg: MQTTMessage) -> MXErrorCode:
        try:
            hierarchy_service_table_msg = MXHierarchyServiceTableResultMessage(msg)

            for middleware in hierarchy_service_table_msg.service_list:
                hierarchy_type = middleware['hierarchy']
                if not hierarchy_type in ['local', 'child']:
                    MXLOG_ERROR(f'[{get_current_function_name()}] Parent middleware is not supported')
                    return MXErrorCode.FAIL

                middleware_name = middleware.get('middleware', None)
                if not middleware_name:
                    MXLOG_ERROR(f'[{get_current_function_name()}] Middleware name {middleware_name} does not exist')
                    return MXErrorCode.FAIL

                self._hierarchical_service_table[middleware_name] = {
                    'hierarchy': hierarchy_type,
                    'values': [],
                    'functions': [],
                }

                thing_list = middleware['things']
                for thing in thing_list:
                    is_alive = thing['is_alive']
                    if is_alive != 1:
                        continue

                    # value 정보를 추출
                    value_service_list = self._extract_value_info(thing=thing, middleware_name=middleware_name)
                    self._hierarchical_service_table[middleware_name]['values'].extend(value_service_list)

                    # function 정보를 추출
                    function_service_list = self._extract_function_info(thing_info=thing, middleware_name=middleware_name)
                    self._hierarchical_service_table[middleware_name]['functions'].extend(function_service_list)

            self._last_refresh_time = get_current_datetime()
            return MXErrorCode.NO_ERROR
        except KeyError as e:
            print_error(e)
            MXLOG_ERROR(f'[{get_current_function_name()}] KeyError')
            return MXErrorCode.FAIL
        except ValueError as e:
            print_error(e)
            MXLOG_ERROR(f'[{get_current_function_name()}] ValueError')
            return MXErrorCode.FAIL
        except Exception as e:
            print_error(e)
            MXLOG_ERROR(f'[{get_current_function_name()}] Unknown Exception')
            return MXErrorCode.FAIL

    # ===================
    #   __  __   ______
    #  |  \/  | |  ____|
    #  | \  / | | |__
    #  | |\/| | |  __|
    #  | |  | | | |____
    #  |_|  |_| |______|
    # ===================

    def _handle_ME_NOTIFY(self, msg: MQTTMessage) -> MXErrorCode:
        notify_msg = MXNotifyMessage(msg)
        notify_msg.set_timestamp()
        self._send_SM_REFRESH()

        return MXErrorCode.NO_ERROR

    # ================
    #  _____ ___  ___
    # /  ___||  \/  |
    # \ `--. | .  . |
    #  `--. \| |\/| |
    # /\__/ /| |  | |
    # \____/ \_|  |_/
    # ================

    def _send_SM_REFRESH(self):
        super_refresh_msg = self.generate_super_refresh_message()
        super_refresh_mqtt_msg = super_refresh_msg.mqtt_message()
        self._publish(super_refresh_mqtt_msg.topic, super_refresh_mqtt_msg.payload)
        self._last_refresh_time = get_current_datetime()

    def _send_SM_SCHEDULE(self, subschedule_msg: MXSubScheduleMessage) -> None:
        subschedule_mqtt_msg = subschedule_msg.mqtt_message()
        self._publish(subschedule_mqtt_msg.topic, subschedule_mqtt_msg.payload)

    def _send_SM_RESULT_SCHEDULE(
        self,
        super_service_name: str,
        super_thing_name: str,
        super_middleware_name: str,
        requester_middleware_name: str,
        scenario: str,
        error: MXErrorCode,
    ) -> None:
        super_schedule_result_msg = MXSuperScheduleResultMessage(
            super_service_name=super_service_name,
            super_thing_name=super_thing_name,
            super_middleware_name=super_middleware_name,
            requester_middleware_name=requester_middleware_name,
            scenario=scenario,
            error=error,
        )
        super_schedule_result_mqtt_msg = super_schedule_result_msg.mqtt_message()
        self._publish(super_schedule_result_mqtt_msg.topic, super_schedule_result_mqtt_msg.payload)

    def _send_SM_EXECUTE(self, subservice_execute_msg: MXSubExecuteMessage) -> None:
        subservice_execute_mqtt_msg = subservice_execute_msg.mqtt_message()
        self._publish(subservice_execute_mqtt_msg.topic, subservice_execute_mqtt_msg.payload)

    def _send_SM_RESULT_EXECUTE(
        self,
        super_service_name: str,
        super_thing_name: str,
        super_middleware_name: str,
        requester_middleware_name: str,
        scenario: str,
        return_type: MXType,
        return_value: MXDataType,
        error: MXErrorCode,
    ):
        super_execute_result_msg = MXSuperExecuteResultMessage(
            super_service_name=super_service_name,
            super_thing_name=super_thing_name,
            super_middleware_name=super_middleware_name,
            requester_middleware_name=requester_middleware_name,
            scenario=scenario,
            return_type=return_type,
            return_value=return_value,
            error=error,
        )
        super_execute_result_mqtt_msg = super_execute_result_msg.mqtt_message()
        self._publish(super_execute_result_mqtt_msg.topic, super_execute_result_mqtt_msg.payload)

    # ===================================================================================
    # ___  ___ _____  _____  _____   _____         _  _  _                   _
    # |  \/  ||  _  ||_   _||_   _| /  __ \       | || || |                 | |
    # | .  . || | | |  | |    | |   | /  \/  __ _ | || || |__    __ _   ___ | | __ ___
    # | |\/| || | | |  | |    | |   | |     / _` || || || '_ \  / _` | / __|| |/ // __|
    # | |  | |\ \/' /  | |    | |   | \__/\| (_| || || || |_) || (_| || (__ |   < \__ \
    # \_|  |_/ \_/\_\  \_/    \_/    \____/ \__,_||_||_||_.__/  \__,_| \___||_|\_\|___/
    # ===================================================================================

    @override
    async def _on_message(self, client: MQTTClient, topic, payload, qos, properties):
        # topic, payload = decode_MQTT_message(msg)
        self._print_packet(topic=topic, payload=payload, direction=Direction.RECEIVED, mode=self._log_mode)
        msg = encode_MQTT_message(topic, payload)

        protocol = MXProtocolType.get(topic)
        if protocol in [
            MXProtocolType.Base.MT_REQUEST_REGISTER_INFO,
            MXProtocolType.Base.MT_REQUEST_UNREGISTER,
            MXProtocolType.Base.MT_RESULT_REGISTER,
            MXProtocolType.Base.MT_RESULT_UNREGISTER,
            MXProtocolType.Base.MT_RESULT_BINARY_VALUE,
            MXProtocolType.Super.MS_RESULT_SCHEDULE,
            MXProtocolType.Super.MS_RESULT_EXECUTE,
            MXProtocolType.Super.MS_RESULT_SERVICE_LIST,
            MXProtocolType.Super.MS_SCHEDULE,
            MXProtocolType.Super.MS_EXECUTE,
            MXProtocolType.Base.MT_EXECUTE,
            MXProtocolType.WebClient.ME_NOTIFY_CHANGE,
            MXProtocolType.WebClient.ME_RESULT_HOME,
        ]:
            await self._receive_queue[protocol].put(msg)
        else:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Unexpected topic! topic: {topic}')

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def _create_super_schedule_task(
        self,
        target_super_function: MXSuperFunction,
        super_schedule_request: MXSuperScheduleRequest,
        hierarchical_service_table: Dict[str, List[MXFunction] | List[MXValue]],
        timeout: float = 60,
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.super_schedule(
                super_schedule_request,
                hierarchical_service_table,
            ),
            done_callback=self._super_schedule_done_callback,
            timeout=timeout,
            target_super_function=target_super_function,
            super_schedule_request=super_schedule_request,
        )

    async def _super_schedule_done_callback(
        self,
        task: asyncio.Task,
        target_super_function: MXSuperFunction,
        super_schedule_request: MXSuperScheduleRequest,
    ) -> None:
        super_schedule_msg = super_schedule_request.trigger_msg
        call_requester = super_schedule_request.trigger_msg.call_requester

        info_message = f'{super_schedule_request.action_type.name} of {target_super_function.name} by scenario {call_requester.middleware}|{call_requester.scenario}'
        try:
            requester_schedule_result: Dict[int, List[MXScheduleTarget]] = task.result()
        except KeyboardInterrupt as e:
            MXLOG_ERROR('Super schedule exit by user')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_ERROR('Super schedule exit by user')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUPER_SCHEDULE TIMEOUT] {info_message} timeout...')
            super_schedule_request.result_msg.error = MXErrorCode.TIMEOUT
        except MXError as e:
            MXLOG_ERROR(f'[SUPER_SCHEDULE FAILED] {info_message} failed... error: {e.error_code.name}')
            super_schedule_request.result_msg.error = MXErrorCode.FAIL
        except Exception as e:
            MXLOG_ERROR(f'[SUPER_SCHEDULE FAILED] {info_message} failed by unknown error...')
            print_error(e)
            super_schedule_request.result_msg.error = MXErrorCode.FAIL
        else:
            # Thing execution mapping
            target_super_function.mapping_table[call_requester] = {}
            for line_num, schedule_target_list in requester_schedule_result.items():
                call_line_info = target_super_function.call_line_info_list[line_num]
                candidate_execute_target_list = get_candidate_list(
                    call_line_info=call_line_info,
                    hierarchical_service_table=self._hierarchical_service_table,
                    action_type=MXActionType.SUB_EXECUTE,
                )

                execute_target_list = []

                # Check candidate execute target's middleware is contained in confirmed schedule target list's middleware
                for candidate_execute_target in candidate_execute_target_list:
                    if candidate_execute_target.middleware in [t.middleware for t in schedule_target_list]:
                        execute_target_list.append(candidate_execute_target)

                select_target_list = target_super_function.select_target(execute_target_list, range_type=call_line_info.range_type)
                target_super_function.mapping_table[call_requester][line_num] = select_target_list

            super_schedule_request.result_msg.error = MXErrorCode.NO_ERROR
        finally:
            # Change super function state
            target_super_function.schedule_running = False
            super_schedule_request.timer_end()

            # Remove future table
            target_super_function.super_schedule_future_table.pop(call_requester)

            result_message = target_super_function.super_schedule_result_message()
            MXLOG_DEBUG(
                f'[SUPER_SCHEDULE END] Scheduling {target_super_function.name} by scenario {call_requester.scenario}. duration: {super_schedule_request._duration:.4f} Sec\n\
                {result_message}',
                'green',
            )

            self._send_SM_RESULT_SCHEDULE(
                super_service_name=super_schedule_msg.super_service_name,
                super_thing_name=super_schedule_msg.super_thing_name,
                super_middleware_name=super_schedule_msg.super_middleware_name,
                requester_middleware_name=call_requester.middleware,
                scenario=call_requester.scenario,
                error=super_schedule_request.result_msg.error,
            )

    ################################################################

    def _create_call_line_schedule_task(
        self,
        target_super_function: MXSuperFunction,
        call_line_info: MXCallLineInfo,
        super_schedule_request: MXSuperScheduleRequest,
        hierarchical_service_table: Dict[str, List[MXService]],
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.call_line_schedule(
                call_line_info=call_line_info,
                super_schedule_request=super_schedule_request,
                hierarchical_service_table=hierarchical_service_table,
            ),
            done_callback=self._call_line_schedule_done_callback,
            target_super_function=target_super_function,
            super_schedule_request=super_schedule_request,
            call_line_info=call_line_info,
        )

    async def _call_line_schedule_done_callback(
        self,
        task: asyncio.Task,
        target_super_function: MXSuperFunction,
        super_schedule_request: MXSuperScheduleRequest,
        call_line_info: MXCallLineInfo,
    ) -> MXErrorCode:
        super_schedule_msg = super_schedule_request.trigger_msg
        call_requester = super_schedule_msg.call_requester
        line_num = call_line_info.line_num

        info_message = f'Schedule call line: {line_num}'
        try:
            task.result()
        except KeyboardInterrupt as e:
            MXLOG_DEBUG('Subschedule exit by user', 'red')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_DEBUG('Subschedule exit by user', 'red')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUBSCHEDULE TIMEOUT] {info_message} timeout...')
            raise e from e
        except Exception as e:
            MXLOG_ERROR(f'[SUBSCHEDULE FAILED] {info_message} failed...')
            print_error(e)
            raise e from e
        finally:
            target_super_function.super_schedule_future_table[call_requester].pop(line_num)

            MXLOG_INFO(
                textwrap.dedent(
                    f'''\
                        [CALL LINE Schedule END] {info_message} success!
                    '''
                ),
                success=True,
            )

    ################################################################

    def _create_subschedule_task(
        self,
        target_super_function: MXSuperFunction,
        subschedule_request: MXSubScheduleRequest,
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.subservice_schedule(
                subschedule_request=subschedule_request,
            ),
            done_callback=self._subservice_schedule_done_callback,
            subschedule_request=subschedule_request,
        )

    async def _subservice_schedule_done_callback(
        self,
        task: asyncio.Task,
        subschedule_request: MXSubScheduleRequest,
    ) -> MXErrorCode:
        call_requester = subschedule_request.trigger_msg.call_requester
        schedule_target = subschedule_request.trigger_msg.schedule_target

        info_message = f'Schedule {schedule_target} by requester {call_requester}'
        try:
            task.result()
        except KeyboardInterrupt as e:
            MXLOG_DEBUG('Subschedule exit by user', 'red')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_DEBUG('Subschedule exit by user', 'red')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUBSCHEDULE TIMEOUT] {info_message} timeout...')
            raise e from e
        except Exception as e:
            MXLOG_ERROR(f'[SUBSCHEDULE FAILED] {info_message} failed...')
            print_error(e)
            raise e from e
        else:
            subschedule_request.result_msg.error = MXErrorCode.NO_ERROR
        finally:
            MXLOG_INFO(
                textwrap.dedent(
                    f'''\
                        [SUBSCHEDULE END] {info_message} success!
                        duration: {subschedule_request.duration:.4f} Sec
                    '''
                ),
                success=True,
            )

    ################################################################

    def _create_super_execute_task(
        self, target_super_function: MXSuperFunction, super_execute_request: MXSuperExecuteRequest, timeout: float = 60
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.super_execute(super_execute_request),
            done_callback=self._super_execute_done_callback,
            timeout=timeout,
            target_super_function=target_super_function,
            super_execute_request=super_execute_request,
        )

    async def _super_execute_done_callback(
        self,
        task: asyncio.Task,
        target_super_function: MXSuperFunction,
        super_execute_request: MXSuperExecuteRequest,
    ) -> MXErrorCode:
        super_execute_msg = super_execute_request.trigger_msg
        call_requester = super_execute_request.trigger_msg.call_requester

        info_message = f'{super_execute_request.action_type.name} of {target_super_function.name} by scenario {call_requester.middleware}|{call_requester.scenario}'
        try:
            result = task.result()
        except KeyboardInterrupt as e:
            MXLOG_ERROR('Super execute exit by user')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_ERROR('Super execute exit by user')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUPER_EXECUTE TIMEOUT] {info_message} timeout...')
            super_execute_request.result_msg.error = MXErrorCode.TIMEOUT
        except MXError as e:
            MXLOG_ERROR(f'[SUPER_EXECUTE FAILED] {info_message} failed... error: {e.error_code.name}')
            super_execute_request.result_msg.error = MXErrorCode.FAIL
        except Exception as e:
            MXLOG_ERROR(f'[SUPER_EXECUTE FAILED] {info_message} failed by unknown error...')
            print_error(e)
            super_execute_request.result_msg.error = MXErrorCode.FAIL
        else:
            super_execute_request.result_msg.error = MXErrorCode.NO_ERROR
        finally:
            delattr(target_super_function.func, LINE_NUM_ATTRIBUTE)

            # Remove the scenario from the running scenario list
            target_super_function.running_scenario_list.remove(super_execute_msg.scenario)
            target_super_function.super_execute_future_table.pop(call_requester)

            # Change super function state
            target_super_function.running = False
            super_execute_request.timer_end()

            # result_message = target_super_function.super_execute_result_message()
            result_message = ''
            MXLOG_DEBUG(
                f'[SUPER_EXECUTE END] Scheduling {target_super_function.name} by scenario {call_requester.scenario}. duration: {super_execute_request._duration:.4f} Sec\n\
                {result_message}',
                'green',
            )

            self._send_SM_RESULT_EXECUTE(
                super_service_name=super_execute_msg.super_service_name,
                super_thing_name=super_execute_msg.super_thing_name,
                super_middleware_name=super_execute_msg.super_middleware_name,
                requester_middleware_name=call_requester.middleware,
                scenario=call_requester.scenario,
                return_type=target_super_function.return_type,
                return_value=result,
                error=super_execute_request.result_msg.error,
            )

    ################################################################

    def _create_call_line_execute_task(
        self,
        call_line_info: MXCallLineInfo,
        target_super_function: MXSuperFunction,
        super_execute_request: MXSuperExecuteRequest,
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.call_line_execute(
                call_line_info=call_line_info,
                super_execute_request=super_execute_request,
            ),
            done_callback=self._call_line_execute_done_callback,
            call_line_info=call_line_info,
            target_super_function=target_super_function,
            super_execute_request=super_execute_request,
        )

    async def _call_line_execute_done_callback(
        self,
        task: asyncio.Task,
        call_line_info: MXCallLineInfo,
        target_super_function: MXSuperFunction,
        super_execute_request: MXSuperExecuteRequest,
    ) -> MXErrorCode:
        call_requester = super_execute_request.trigger_msg.call_requester
        line_num = call_line_info.line_num

        info_message = f'Execute call line: {line_num}'
        try:
            task.result()
        except KeyboardInterrupt as e:
            MXLOG_DEBUG('Subexecute exit by user', 'red')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_DEBUG('Subexecute exit by user', 'red')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUBEXECUTE TIMEOUT] {info_message} timeout...')
            raise e from e
        except Exception as e:
            MXLOG_ERROR(f'[SUBEXECUTE FAILED] {info_message} failed...')
            print_error(e)
            raise e from e
        finally:
            target_super_function.super_execute_future_table[call_requester].pop(line_num)

            MXLOG_INFO(
                textwrap.dedent(
                    f'''\
                        [CALL LINE EXECUTE END] {info_message} success!
                    '''
                ),
                success=True,
            )

    ################################################################

    def _create_subexecute_task(
        self,
        target_super_function: MXSuperFunction,
        subexecute_request: MXSubExecuteRequest,
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_super_function.subservice_execute(subexecute_request),
            done_callback=self._subexecute_done_callback,
            target_super_function=target_super_function,
            subexecute_request=subexecute_request,
        )

    async def _subexecute_done_callback(
        self,
        task: asyncio.Task,
        target_super_function: MXSuperFunction,
        subexecute_request: MXSubExecuteRequest,
    ):
        subexecute_msg = subexecute_request.trigger_msg
        call_requester = subexecute_msg.call_requester
        line_num = subexecute_msg.line_num
        execute_order = subexecute_msg.execute_order

        info_message = f'SUB Execute: {subexecute_request.trigger_msg.subservice_name}|{line_num}-{execute_order} by requester {call_requester}'
        try:
            task.result()
        except KeyboardInterrupt as e:
            MXLOG_DEBUG('Subexecute exit by user', 'red')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_DEBUG('Subexecute exit by user', 'red')
        except MXTimeoutError as e:
            MXLOG_ERROR(f'[SUBEXECUTE TIMEOUT] {info_message} timeout...')
            raise e from e
        except Exception as e:
            MXLOG_ERROR(f'[SUBEXECUTE FAILED] {info_message} failed...')
            print_error(e)
            raise e from e
        finally:
            target_super_function.super_execute_future_table[call_requester][line_num].pop(execute_order)

            MXLOG_INFO(
                textwrap.dedent(
                    f'''\
                        [CALL LINE EXECUTE END] {info_message} success!
                    '''
                ),
                success=True,
            )

    ################################################################

    def generate_super_refresh_message(self) -> MXSuperRefreshMessage:
        super_refresh_msg = MXSuperRefreshMessage(self.name)
        return super_refresh_msg

    @override
    def _get_function(self, function_name: str) -> MXSuperFunction:
        return super()._get_function(function_name=function_name)

    @override
    def _subscribe_init_topic_list(self, thing_data: MXThing):
        super()._subscribe_init_topic_list(thing_data)

        topic_list = [
            MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % "#",
        ]

        for topic in topic_list:
            self._subscribe(topic)

    @override
    def _subscribe_service_topic_list(self, thing_data: MXThing):
        topic_list = []
        for function in thing_data.function_list:
            # Super Schedule, Super Execute에 필요한 토픽들을 미리 구독을 해놓는다.
            topic_list += [
                MXProtocolType.Super.MS_SCHEDULE.value % (function.name, thing_data.name, thing_data.middleware_name, '#'),
                MXProtocolType.Super.MS_RESULT_SCHEDULE.value % ('+', '+', '#'),
                MXProtocolType.Super.MS_EXECUTE.value % (function.name, thing_data.name, thing_data.middleware_name, '#'),
                MXProtocolType.Super.MS_RESULT_EXECUTE.value % ('+', '+', '#'),
            ]

        for topic in topic_list:
            self._subscribe(topic)

    async def _dry_run_super_functions(self) -> None:
        MXLOG_DEBUG(f'Dry-run super service for detect call() line', 'green')

        for function in self.function_list:
            function._create_call_line_schedule_task = self._create_call_line_schedule_task
            function._create_subschedule_task = self._create_subschedule_task
            function._create_call_line_execute_task = self._create_call_line_execute_task
            function._create_subexecute_task = self._create_subexecute_task
            function._publish = self._publish
            setattr(function.func, DRY_RUN_ATTRIBUTE, ...)
            try:
                MXLOG_DEBUG(f'[{function.name}]', 'green')
                if asyncio.iscoroutinefunction(function.func):
                    await function.func(*tuple(function.arg_list))
                else:
                    function.func(*tuple(function.arg_list))
                function.call_line_info_list = getattr(function._func, CALL_LINE_INFO_LIST_ATTRIBUTE)
                for i, call_line_info in enumerate(function._call_line_info_list):
                    call_line_info.line_num = i
            except MXError as e:
                # call()를 실행하다가 MXError와 관련된 에러가 발생한다는 것은 call() 코드 명세가 잘못
                # 되었다는 것을 의미한다.
                # 만약 MXError 에러가 아닌 다른 예외가 발생한 경우, call() 외의 코드에서 발생한
                # 예외이다.
                MXLOG_CRITICAL(f'Super function {function.name} is not valid. Check call() line please')

                raise e
            finally:
                delattr(function.func, DRY_RUN_ATTRIBUTE)

    def _extract_value_info(self, thing: dict, middleware_name: str) -> List[MXValue]:
        thing_name: str = thing['name']
        value_list: List[dict] = thing['values']

        value_service_list = []
        for value_info in value_list:
            value_tag_list = [MXTag(tag['name']) for tag in value_info['tags']]
            format = value_info.get('format', '')
            if '(null)' in format:
                format = ''

            # TODO: cycle info is omit in service list
            value_service = MXValue(
                func=dummy_func(arg_list=[]),
                type=MXType.get(value_info['type']),
                bound=(float(value_info['bound']['min_value']), float(value_info['bound']['max_value'])),
                cycle=None,
                name=value_info['name'],
                tag_list=value_tag_list,
                desc=value_info['description'],
                thing_name=thing_name,
                middleware_name=middleware_name,
                format=format,
            )
            if value_service not in self._hierarchical_service_table[middleware_name]['values']:
                value_service_list.append(value_service)

        return value_service_list

    def _extract_function_info(self, thing_info: dict, middleware_name: str) -> List[MXFunction]:
        thing_name = thing_info['name']
        function_list = thing_info['functions']

        function_service_list = []
        for function_info in function_list:
            function_tag_list = [MXTag(tag['name']) for tag in function_info['tags']]
            arg_list = []
            if function_info['use_arg']:
                for argument in function_info['arguments']:
                    arg_list.append(
                        MXArgument(
                            name=argument['name'],
                            type=MXType.get(argument['type']),
                            bound=(float(argument['bound']['min_value']), float(argument['bound']['max_value'])),
                        )
                    )

            function_service = MXFunction(
                func=dummy_func(arg_list=arg_list),
                return_type=MXType.get(function_info['return_type']),
                name=function_info['name'],
                tag_list=function_tag_list,
                desc=function_info['description'],
                thing_name=thing_name,
                middleware_name=middleware_name,
                arg_list=arg_list,
                exec_time=function_info['exec_time'],
            )
            if function_service not in self._hierarchical_service_table[middleware_name]['functions']:
                function_service_list.append(function_service)

        return function_service_list

    # ====================================
    #               _    _
    #              | |  | |
    #   __ _   ___ | |_ | |_   ___  _ __
    #  / _` | / _ \| __|| __| / _ \| '__|
    # | (_| ||  __/| |_ | |_ |  __/| |
    #  \__, | \___| \__| \__| \___||_|
    #   __/ |
    #  |___/
    # ====================================

    @override
    @property
    def function_list(self) -> List[MXSuperFunction]:
        return sorted(
            [service for service in self._thing_data.service_list if isinstance(service, MXSuperFunction) and not service.name.startswith('__')],
            key=lambda x: x.name,
        )

    @property
    def refresh_cycle(self) -> float:
        return self._refresh_cycle

    @property
    def last_refresh_time(self) -> float:
        return self._last_refresh_time

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @refresh_cycle.setter
    def refresh_cycle(self, refresh_cycle: float):
        if not isinstance(refresh_cycle, (int, float)):
            raise MXTypeError(f'refresh_cycle must be int or float')
        if refresh_cycle <= 0:
            raise MXValueError(f'refresh_cycle must be greater than 0')

        self._refresh_cycle = refresh_cycle

    @last_refresh_time.setter
    def last_refresh_time(self, last_refresh_time: float):
        self._last_refresh_time = last_refresh_time
