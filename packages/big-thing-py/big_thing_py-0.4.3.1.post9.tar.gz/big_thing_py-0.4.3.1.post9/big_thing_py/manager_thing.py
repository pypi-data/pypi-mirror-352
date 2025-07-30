from big_thing_py.big_thing import *
from big_thing_py.manager import *
from big_thing_py.core.argument import MXArgumentData
from big_thing_py.staff_thing import MXStaffThing
from big_thing_py.core.service_model import Objects as Skill
import uuid
import pwd


class MXManagerThing(MXBigThing, metaclass=ABCMeta):

    def __init__(
        self,
        name: str = MXThing.DEFAULT_NAME,
        nick_name: str = MXThing.DEFAULT_NAME,
        category=DeviceCategory.ManagerThing,
        device_type=MXDeviceType.UNKNOWN,
        desc='',
        version=sdk_version(),
        service_list: List[MXService] = list(),
        alive_cycle: int = 60,
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
        is_matter: bool = False,
    ):
        super().__init__(
            name=name,
            nick_name=nick_name,
            category=category,
            device_type=device_type,
            desc=desc,
            version=version,
            service_list=service_list,
            alive_cycle=alive_cycle,
            is_super=False,
            is_parallel=True,
            is_builtin=False,
            is_manager=True,
            is_staff=False,
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

        self._staff_thing_list: List[MXStaffThing] = []
        self._event_handler_task: asyncio.Task = None

    @override
    async def _setup(self):
        default_tag_list = [MXTag('manager')]

        value_list = []
        function_list = [
            MXFunction(
                func=self._discover,
                category=Skill.manager.Functions.discover,
                tag_list=default_tag_list,
                exec_time=60,
                timeout=60,
            ),
            MXFunction(
                func=self._add_thing,
                category=Skill.manager.Functions.add_thing,
                tag_list=default_tag_list,
                exec_time=150,
                timeout=150,
            ),
            MXFunction(
                func=self._delete_thing,
                category=Skill.manager.Functions.delete_thing,
                tag_list=default_tag_list,
                exec_time=60,
                timeout=60,
            ),
        ]

        await super()._setup()
        self._event_handler_task = asyncio.create_task(self._event_handler())

        for service in value_list + function_list:
            self.add_service(service)

        self.default_staff_thing_store_path = f'{os.path.join(DEFAULT_WORKING_DIR, self.name, "staff_thing_info.json")}'

    @override
    async def _wrapup(self):
        try:
            if self._mqtt_client and self._mqtt_client.is_connected:
                self._send_TM_UNREGISTER(self._thing_data)
                for thing in self._staff_thing_list:
                    self._send_TM_UNREGISTER(thing)
                # FIXME: Need to wait for the result of unregister
                # recv_msg = await self._receive_queue[MXProtocolType.Base.MT_RESULT_UNREGISTER].get()
                # error = await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data)

            return True
        except Exception as e:
            print_error(e)
            return False
        finally:
            if await self._ble_advertiser.is_advertising():
                await self._ble_advertiser.stop()

            self._unregister_mdns_service()

            if self._mqtt_client and self._mqtt_client.is_connected:
                await self._disconnect_from_broker(disconnect_try=MXBigThing.CONNECT_RETRY)

            if self._event_handler_task:
                self._event_handler_task.cancel()

            MXLOG_DEBUG('Thing Exit', 'red')
            sys.exit(0)

    # ===========================================================================================
    #  _    _                             _    __                      _    _
    # | |  | |                           | |  / _|                    | |  (_)
    # | |_ | |__   _ __   ___   __ _   __| | | |_  _   _  _ __    ___ | |_  _   ___   _ __   ___
    # | __|| '_ \ | '__| / _ \ / _` | / _` | |  _|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
    # | |_ | | | || |   |  __/| (_| || (_| | | |  | |_| || | | || (__ | |_ | || (_) || | | |\__ \
    #  \__||_| |_||_|    \___| \__,_| \__,_| |_|   \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
    # ===========================================================================================

    @override
    async def _alive_check(self):
        """
        주기적으로 Thing의 상태를 확인하고, alive_cycle을 초과하면 TM_ALIVE 를 전송합니다.
        """
        check_interval = THREAD_TIME_OUT
        threshold = self.alive_cycle / MXBigThing.ALIVE_CYCLE_SCALER

        while True:
            await asyncio.sleep(check_interval)

            if self._state is not ThingState.RUNNING:
                continue

            for thing in self._whole_thing_list:
                if thing.is_manager:
                    thing: MXManagerThing
                    elapsed = get_current_datetime() - self.last_alive_time
                    if elapsed <= threshold:
                        continue

                    self._send_TM_ALIVE(self._thing_data)
                elif thing.is_staff:
                    thing: MXStaffThing
                    elapsed = get_current_datetime() - thing.last_alive_time
                    if elapsed <= threshold:
                        continue

                    if await self._check_thing_exist(thing):
                        if not thing.is_alive:
                            MXLOG_DEBUG(f'Staff Thing {thing.name} is online', 'cyan')
                        thing.is_alive = True
                    else:
                        if thing.is_alive:
                            MXLOG_DEBUG(f'Staff Thing {thing.name} is offline', 'red')
                        thing.is_alive = False

                    if thing.is_alive:
                        self._send_TM_ALIVE(thing)

    @override
    async def _BROKER_CONNECTED_state_process(self):

        async def wait_for_register(target_thing: MXThing) -> bool:
            recv_msg = await self._receive_queue[MXProtocolType.Base.MT_RESULT_REGISTER].get()
            error = await self._handle_mqtt_message(recv_msg, target_thing=target_thing, state_change=False)
            if not error in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE, MXErrorCode.INVALID_REQUEST, MXErrorCode.INVALID_DESTINATION]:
                return False
            else:
                return True

        # Prepare to register Manager Thing
        MXLOG_DEBUG(f'Run Manger Thing {self.name}', 'green')

        self._subscribe_init_topic_list(self._thing_data)
        self._send_TM_REGISTER(self._thing_data)
        if await wait_for_register(self._thing_data):
            self._subscribe_service_topic_list(self._thing_data)
        else:
            self.next_state = ThingState.SHUTDOWN
            return

        # Prepare to register Staff Things
        loaded_staff_thing_list = await self._load_staff_thing_info()
        for loaded_staff_thing in loaded_staff_thing_list:
            # Check staff thing reachable and update staff thing info to latest
            latest_staff_thing = await self._check_thing_exist(loaded_staff_thing)
            if not latest_staff_thing:
                # Staff thing is offline -> Add to staff_list and wait for online, while running
                MXLOG_WARN(f'Staff Thing {loaded_staff_thing.name} is offline', 'red')

                loaded_staff_thing.is_alive = False
                loaded_staff_thing.last_alive_check_time = get_current_datetime()
                staff_thing_to_add = loaded_staff_thing
            else:
                # Staff thing is online -> Register staff thing and Add to staff_list
                latest_staff_thing.is_alive = True
                # latest_staff_thing.last_alive_time = get_current_datetime()

                # If staff thing's info is updated, store the updated info
                if latest_staff_thing.name == loaded_staff_thing.name and latest_staff_thing.nick_name == loaded_staff_thing.nick_name:
                    MXLOG_INFO(f'Load staff thing {loaded_staff_thing.name} completed!')
                else:
                    MXLOG_INFO(
                        f'Update staff thing\'s nick name {loaded_staff_thing.name} completed! {loaded_staff_thing.nick_name} -> {latest_staff_thing.nick_name}'
                    )
                    self._delete_staff_thing_info(loaded_staff_thing)
                    self._store_staff_thing_info(latest_staff_thing)

                staff_thing_to_add = latest_staff_thing

            await self._add_staff_thing(staff_thing_to_add)
            self._subscribe_init_topic_list(staff_thing_to_add)
            if staff_thing_to_add.is_alive:
                # If Staff Thing is online, register and subscribe service topic
                MXLOG_INFO(f'Run Staff Thing {staff_thing_to_add.name}')
                self._send_TM_REGISTER(staff_thing_to_add)
                if await wait_for_register(staff_thing_to_add):
                    self._subscribe_service_topic_list(staff_thing_to_add)
                else:
                    MXLOG_ERROR(f'Register Staff Thing {staff_thing_to_add.name} failed!!!')
                    self.next_state = ThingState.SHUTDOWN
                    return

        self.next_state = ThingState.REGISTERED

    @override
    async def _RUNNING_state_process(self):
        # MQTT receive handling
        if not self._receive_queue_empty():
            recv_msg = await self._receive_queue_get()

            # # MQTT receive handling(Manager Thing)
            # error = await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data)
            # if error == MXErrorCode.INVALID_DESTINATION:

            # if not error in MXBigThing.HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST:
            #     MXLOG_DEBUG(f'[{get_current_function_name()}] MQTT Message handling failed', 'red')

            # MQTT receive handling(Staff Thing)
            for thing in self._whole_thing_list:
                if isinstance(thing, MXManagerThing):
                    thing_data = thing._thing_data
                    state_change = True
                elif isinstance(thing, MXStaffThing):
                    thing_data = thing
                    state_change = False

                target_thing_name = topic_split(decode_MQTT_message(recv_msg)[0])[-1]
                if target_thing_name != thing_data.name:
                    continue

                error = await self._handle_mqtt_message(recv_msg, target_thing=thing_data, state_change=state_change)
                if not error in MXBigThing.HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST:
                    MXLOG_DEBUG(f'[{get_current_function_name()}] MQTT Message handling failed', 'red')

        # Value publish (Manager Thing)
        current_time = get_current_datetime()
        for value in self.value_list:
            # NOTE (thsvkd): cycle == 0 mean, value is event-based
            if not value.is_initialized or current_time - value.last_update_time > value.cycle and value.cycle != 0:
                new_value = await value.async_update()
                if new_value is None:
                    continue

                self._send_TM_VALUE_PUBLISH(value)

        # Value publish (Staff Thing)
        for thing in self._staff_thing_list:
            for value in thing.value_list:
                if not thing.is_alive:
                    continue
                # NOTE (thsvkd): cycle == 0 mean, value is event-based
                if not value.is_initialized or current_time - value.last_update_time > value.cycle and value.cycle != 0:
                    new_value = await value.async_update()
                    if new_value is None:
                        continue

                    self._send_TM_VALUE_PUBLISH(value)

    @override
    async def _BROKER_RECONNECTED_state_process(self):
        get_home_msg = self._thing_data.generate_get_home_message().mqtt_message()
        result_home_topic = MXProtocolType.WebClient.ME_RESULT_HOME.value % '+'
        self._subscribe(result_home_topic)

        current_time = get_current_datetime()
        while get_current_datetime() - current_time < MXBigThing.MIDDLEWARE_RECONNECT_TIMEOUT:
            self._publish(get_home_msg.topic, get_home_msg.payload)
            try:
                recv_msg = self._receive_queue[MXProtocolType.WebClient.ME_RESULT_HOME].get_nowait()
                await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data, state_change=False)

                # Auto subscription restore feature
                subscriptions: List[Subscription] = self._mqtt_client.subscriptions
                for subscription in subscriptions:
                    self._mqtt_client.resubscribe(subscription)

                self._send_TM_ALIVE(self._thing_data)
                # Send alive for staff things
                for staff_thing in self._staff_thing_list:
                    self._send_TM_ALIVE(staff_thing)
                self.next_state = ThingState.REGISTERED
                break
            except asyncio.QueueEmpty:
                await asyncio.sleep(MXBigThing.MIDDLEWARE_ONLINE_CHECK_INTERVAL)
        else:
            if self.is_builtin or self.is_manager:
                self.next_state = ThingState.SHUTDOWN
            else:
                MXLOG_DEBUG(f'Middleware is offline... Go back to BLE setup.', 'red')
                self.next_state = ThingState.BLE_ADVERTISE

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

    # ===========================
    #            _____   _____
    #     /\    |  __ \ |_   _|
    #    /  \   | |__) |  | |
    #   / /\ \  |  ___/   | |
    #  / ____ \ | |      _| |_
    # /_/    \_\|_|     |_____|
    # ===========================

    @abstractmethod
    def _create_staff(self, staff_thing_info: dict) -> Union[MXStaffThing, None]:
        '''
        _scan_staff_thing() 함수를 통해 수집된 staff thing 정보를 바탕으로 staff thing을 생성하는 함수.
        만약 스캔하는 것만으로 완벽한 staff thing의 정보를 수집할 수 없다면, staff thing의 register 메시지를 받아 처리하는
        _handle_REGISTER_staff_message() 함수에서 staff thing을 self._staff_thing_list에서 찾아 정보를 추가할 수 있다.

        Args:
            staff_thing_info (dict): staff thing의 정보를 담고 있는 딕셔너리

        Returns:
            staff_thing(MXStaffThing): 생성한 staff thing 인스턴스
        '''
        ...

    @abstractmethod
    async def _scan_staff_thing(self, timeout: float) -> Tuple[List[dict], str]:
        '''
        지속적으로 staff thing을 발견하여 정보를 수집하여 반환하는 함수.
        timeout을 지정하여 한 번 staff thing을 검색하는데 소요될 시간을 지정할 수 있다.

        Args:
            timeout (float): staff thing을 검색하는데 소요될 시간

        Returns:
            List[dict]: staff thing의 정보를 담고 있는 리스트
        '''
        ...

    @abstractmethod
    async def _check_thing_exist__(self, staff_thing: MXStaffThing) -> Union[MXStaffThing, Literal[False]]:
        '''
        staff thing이 실제로 존재하는 지 검사하는 함수

        Args:
            staff_thing (MXStaffThing): staff thing의 정보를 담고 있는 문자열

        Returns:
            Union[MXStaffThing, Literal[False]]: staff thing가 존재하는 경우 staff thing 인스턴수를, 존재하지 않는 경우 False를 반환
        '''
        ...

    @abstractmethod
    async def _add_thing__(self, client_id: str, uid: str) -> Union[MXStaffThing, None]:
        '''
        staff thing을 추가하는 함수.

        Args:
            client_id (str): staff thing을 등록 요청하는 클라이언트의 ID
            uid (str): staff thing의 고유 ID

        Returns:
            dict: staff thing 추가 결과 딕셔너리
        '''
        ...

    @abstractmethod
    async def _delete_thing__(self, client_id: str, uid: str) -> Union[MXStaffThing, None]:
        '''
        staff thing을 삭제하는 함수.

        Args:
            uid (str): staff thing의 고유 ID

        Returns:
            dict: staff thing 삭제 결과 딕셔너리
        '''
        ...

    @abstractmethod
    async def _event_handler(self) -> asyncio.Task:
        '''
        event stream으로 부터 받아온 event를 처리하는 함수

        Args: None

        Returns:
            asyncio.Task: event를 처리하는 Task
        '''
        ...

    async def _check_thing_exist(self, staff_thing: MXStaffThing) -> Union[bool, MXStaffThing]:
        staff_thing.last_alive_check_time = get_current_datetime()

        try:
            return await self._check_thing_exist__(staff_thing)
        except Exception as e:
            print_error(e)
            return False

    async def _add_thing(self, staff_thing_info_string: str, client_id: str, name: str) -> str:
        uid = json_string_to_dict(staff_thing_info_string)['uid']
        fallback_thing_name = name

        try:
            target_staff_thing = self._get_staff_thing_by_uid(uid)
            if target_staff_thing:
                if await self._check_thing_exist(target_staff_thing):
                    error_string = f'Staff Thing {target_staff_thing.name} is already added'
                    MXLOG_WARN(f'[{get_current_function_name()}] {error_string}')
                    fallback_thing_name = target_staff_thing.name
                    raise MXDuplicatedError(error_string)
                else:
                    raise MXFailError(f'Staff Thing {target_staff_thing.name} is not exist')

            target_staff_thing = await self._add_thing__(client_id, uid)
            self._store_staff_thing_info(target_staff_thing)
            return dict_to_json_string(dict(thing=target_staff_thing.name, error=MXErrorCode.NO_ERROR.value, error_string=''))
        except MXDuplicatedError as e:
            await self._register_staff_thing(target_staff_thing)
            return dict_to_json_string(dict(thing=fallback_thing_name, error=MXErrorCode.DUPLICATE.value, error_string=str(e)))
        except Exception as e:
            return dict_to_json_string(dict(thing=fallback_thing_name, error=MXErrorCode.FAIL.value, error_string=str(e)))

    async def _delete_thing(self, staff_thing_name: str, client_id: str) -> str:
        try:
            target_staff_thing = self._get_staff_thing_by_name(staff_thing_name)
            if not target_staff_thing:
                error_string = f'Staff thing is not found. name: {staff_thing_name}'
                MXLOG_WARN(f'[{get_current_function_name()}] {error_string}')
                raise MXNotFoundError(error_string)

            if not (target_staff_thing := await self._check_thing_exist__(target_staff_thing)):
                error_string = f'Staff thing is not found from 3rd party platform. name: {staff_thing_name}'
                MXLOG_WARN(f'[{get_current_function_name()}] {error_string}')
                raise MXNotFoundError(error_string)

            target_staff_thing.request_client_id = client_id
            await self._delete_thing__(client_id, target_staff_thing.uid)
            await self._unregister_staff_thing(target_staff_thing)
            await self._delete_staff_thing(target_staff_thing)
            self._delete_staff_thing_info(target_staff_thing)
            return dict_to_json_string(dict(thing=target_staff_thing.name, error=MXErrorCode.NO_ERROR.value, error_string=''))
        except MXNotFoundError as e:
            return dict_to_json_string(dict(thing=staff_thing_name, error=MXErrorCode.TARGET_NOT_FOUND.value, error_string=''))
        except Exception as e:
            return dict_to_json_string(dict(thing=staff_thing_name, error=MXErrorCode.FAIL.value, error_string=str(e)))

    async def _discover(self) -> str:
        base_info = dict(
            type=self._thing_data.device_type.value,
            manager=self.name,
        )
        try:
            staff_thing_list = await self._scan_staff_thing()
            for staff_thing in staff_thing_list:
                staff_thing['device_category'] = staff_thing['device_category'].name
            discovered_things = dict(**base_info, things=staff_thing_list, error=MXErrorCode.NO_ERROR.value, error_string='')
        except MXNotSupportedError as e:
            MXLOG_ERROR(f'Scan staff thing failed... error: {e}')
            discovered_things = dict(**base_info, things=[], manager=self.name, error=MXErrorCode.FAIL.value, error_string=str(e))

        return dict_to_json_string(discovered_things)

    # ===============
    # ___  ___ _____
    # |  \/  ||_   _|
    # | .  . |  | |
    # | |\/| |  | |
    # | |  | |  | |
    # \_|  |_/  \_/
    # ===============

    # ===============
    #  _____ ___  ___
    # |_   _||  \/  |
    #   | |  | .  . |
    #   | |  | |\/| |
    #   | |  | |  | |
    #   \_/  \_|  |_/
    # ===============

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def _get_thing(self, thing_name: str) -> MXThing | None:
        for thing in self._whole_thing_list:
            if thing.name == thing_name:
                return thing
        else:
            return None

    async def _register_staff_thing(self, target_staff_thing: MXStaffThing) -> None:
        self._send_TM_REGISTER(target_staff_thing)
        recv_msg: MQTTMessage = await self._receive_queue[MXProtocolType.Base.MT_RESULT_REGISTER].get()
        error = await self._handle_mqtt_message(recv_msg, target_thing=target_staff_thing, state_change=False)
        if not error in MXBigThing.HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST:
            MXLOG_DEBUG(f'[{get_current_function_name()}] MQTT Message handling failed', 'red')

    async def _unregister_staff_thing(self, target_staff_thing: MXStaffThing) -> None:
        self._send_TM_UNREGISTER(target_staff_thing)
        recv_msg: MQTTMessage = await self._receive_queue[MXProtocolType.Base.MT_RESULT_UNREGISTER].get()
        error = await self._handle_mqtt_message(recv_msg, target_thing=target_staff_thing, state_change=False)
        if not error in MXBigThing.HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST:
            MXLOG_DEBUG(f'[{get_current_function_name()}] MQTT Message handling failed', 'red')

    async def _add_staff_thing(self, staff_thing: MXStaffThing) -> MXStaffThing:
        if not await staff_thing.setup():
            raise ValueError(f'[{get_current_function_name()}] Staff Thing {staff_thing.name} setup failed')

        self._staff_thing_list.append(staff_thing)

        return staff_thing

    async def _delete_staff_thing(self, staff_thing: MXStaffThing) -> bool:
        if not await staff_thing.wrapup():
            raise ValueError(f'[{get_current_function_name()}] Staff Thing {staff_thing.name} wrapup failed')

        if not staff_thing in self._staff_thing_list:
            MXLOG_WARN(f'[{get_current_function_name()}] Staff Thing {staff_thing.name} is not exist in _staff_thing_list')
        else:
            self._staff_thing_list.remove(staff_thing)

        return True

    def _store_staff_thing_info(self, target_staff_thing: MXStaffThing) -> None:
        if not os.path.exists(self.default_staff_thing_store_path):
            os.makedirs(os.path.dirname(self.default_staff_thing_store_path), exist_ok=True)
            json_file_write(self.default_staff_thing_store_path, dict(things=[]), mode='w')

        if os.geteuid() == 0:
            original_user = os.environ.get('SUDO_USER')
            if not original_user:
                raise ValueError('SUDO_USER environment variable is not set. Unable to determine the original user.')

            user_info = pwd.getpwnam(original_user)
            uid = user_info.pw_uid
            gid = user_info.pw_gid

            os.chown(self.default_staff_thing_store_path, uid, gid)
            os.chmod(self.default_staff_thing_store_path, 0o644)

        staff_thing_info_list = []
        staff_thing_info_file: Dict[str, list] = json_file_read(self.default_staff_thing_store_path)
        staff_thing_info_list = staff_thing_info_file['things']

        if not target_staff_thing.staff_dict() in staff_thing_info_list:
            staff_thing_info_list.append(target_staff_thing.staff_dict())

        json_file_write(self.default_staff_thing_store_path, dict(things=staff_thing_info_list))

    def _delete_staff_thing_info(self, target_staff_thing: MXStaffThing) -> None:
        staff_thing_info_file = json_file_read(self.default_staff_thing_store_path)
        staff_thing_info_list = staff_thing_info_file['things']
        staff_thing_info_list = [
            info for info in staff_thing_info_list if info['uid'] != target_staff_thing.name and info['nick_name'] != target_staff_thing.nick_name
        ]
        json_file_write(self.default_staff_thing_store_path, dict(things=staff_thing_info_list))

    async def _load_staff_thing_info(self) -> List[MXStaffThing]:
        staff_thing_info_list = json_file_read(self.default_staff_thing_store_path)
        if not staff_thing_info_list:
            return []
        else:
            staff_thing_info_list = [self._create_staff(staff_thing_info) for staff_thing_info in staff_thing_info_list['things']]

        return staff_thing_info_list

    @override
    def _subscribe_init_topic_list(self, staff_thing: MXThing) -> None:
        topic_list = [
            MXProtocolType.Base.MT_REQUEST_REGISTER_INFO.value % staff_thing.name,
            MXProtocolType.Base.MT_RESULT_REGISTER.value % staff_thing.name,
            MXProtocolType.Base.MT_RESULT_UNREGISTER.value % staff_thing.name,
            MXProtocolType.Base.MT_RESULT_BINARY_VALUE.value % staff_thing.name,
        ]

        for topic in topic_list:
            self._subscribe(topic)

    @override
    def _subscribe_service_topic_list(self, thing: MXThing):
        topic_list = []

        if find_class_in_hierarchy(thing, MXManagerThing) or type(thing) is MXThing:
            target_thing = self._thing_data
            for service in target_thing.function_list:
                topic_list += [
                    MXProtocolType.Base.MT_IN_EXECUTE.value % (service.name, target_thing.name),
                ]
        elif find_class_in_hierarchy(thing, MXStaffThing):
            target_thing = thing
            for function in target_thing.function_list:
                topic_list += [
                    MXProtocolType.Base.MT_EXECUTE.value % (function.name, target_thing.name, '+', '+'),
                    (MXProtocolType.Base.MT_EXECUTE.value % (function.name, target_thing.name, '', '')).rstrip('/'),
                ]
        else:
            raise ValueError(f'Unknown type instance: {type(thing)}')

        for topic in topic_list:
            self._subscribe(topic)

    def _get_staff_thing_by_name(self, name: str) -> MXStaffThing:
        for staff_thing in self._staff_thing_list:
            if staff_thing.name == name:
                return staff_thing
        else:
            return None

    def _get_staff_thing_by_uid(self, uid: str) -> MXStaffThing:
        for staff_thing in self._staff_thing_list:
            if staff_thing.uid == uid:
                return staff_thing
        else:
            return None

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

    @property
    def _whole_thing_list(self) -> List[MXThing]:
        return [self, *self._staff_thing_list]
