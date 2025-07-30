from big_thing_py.core.thing import *
from big_thing_py.core.argument import MXArgument
from big_thing_py.core.mqtt_message import (
    MXRequestRegisterInfoMessage,
    MXRequestUnregisterMessage,
    MXExecuteMessage,
    MXExecuteResultMessage,
    MXRegisterResultMessage,
    MXUnregisterResultMessage,
    MXBinaryValueResultMessage,
    MXHomeResultMessage,
)
from big_thing_py.core.request import MXExecuteRequest, MXInnerExecuteRequest
from big_thing_py.core.ble_advertiser import BLEAdvertiser, BLEErrorCode, DeviceWifiService
from big_thing_py.core.wifi_manager import WiFiManager
from big_thing_py.core.ethernet_manager import EthernetManager
from big_thing_py.core.device_model import Objects as DeviceCategory
from big_thing_py.core.device_model.DeviceObjects import ALL_DEVICE_TYPES
from .core.kvstore_controller import KVStoreController
from .common.helper.util import *

import ssl
import asyncio
import uvloop
import zeroconf
from zeroconf import ServiceInfo, Zeroconf
import socket
from functools import partial, wraps

from gmqtt import Client as MQTTClient, Subscription

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# ASCII Art from https://patorjk.com/software/taag/#p=display&h=1&v=1&f=Big

# ======================================================================== #
#    _____         _____   ____   _      _______  _      _                 #
#   / ____|       |  __ \ |  _ \ (_)    |__   __|| |    (_)                #
#  | (___    ___  | |__) || |_) | _   __ _ | |   | |__   _  _ __    __ _   #
#   \___ \  / _ \ |  ___/ |  _ < | | / _` || |   | '_ \ | || '_ \  / _` |  #
#   ____) || (_) || |     | |_) || || (_| || |   | | | || || | | || (_| |  #
#  |_____/  \___/ |_|     |____/ |_| \__, ||_|   |_| |_||_||_| |_| \__, |  #
#                                     __/ |                         __/ |  #
#                                    |___/                         |___/   #
# ======================================================================== #

# KVS Storage key definitions
KVS_KEY_NAME = 'name'
KVS_KEY_NICK_NAME = 'nick_name'
KVS_KEY_CATEGORY = 'category'
KVS_KEY_DESC = 'desc'
KVS_KEY_VERSION = 'version'
KVS_KEY_ALIVE_CYCLE = 'alive_cycle'
KVS_KEY_MIDDLEWARE_NAME = 'middleware_name'
KVS_KEY_LAST_ALIVE_TIME = 'last_alive_time'
KVS_KEY_SSID = 'ssid'
# KVS_KEY_PW = 'pw'
KVS_KEY_HOST = 'ip'
KVS_KEY_PORT = 'port'
KVS_KEY_SSL_CA_PATH = 'ssl_ca_path'
KVS_KEY_SSL_CERT_PATH = 'ssl_cert_path'
KVS_KEY_SSL_KEY_PATH = 'ssl_key_path'

DEFAULT_WORKING_DIR = '/tmp/joi_thing/'
DEFAULT_LOG_PATH = DEFAULT_WORKING_DIR
DEFAULT_KVS_STORAGE_PATH = DEFAULT_WORKING_DIR


class ThingState(Enum):
    RESET = auto()
    NETWORK_SETUP = auto()
    BLE_ADVERTISE = auto()
    BROKER_SETUP = auto()
    NETWORK_CONNECTED = auto()
    BROKER_CONNECTED = auto()
    REGISTERED = auto()
    RUNNING = auto()
    UNREGISTERED = auto()
    NETWORK_LOST = auto()
    BROKER_LOST = auto()
    BROKER_RECONNECTED = auto()
    SHUTDOWN = auto()


class MXBigThing:
    MIDDLEWARE_ONLINE_CHECK_INTERVAL = 0.5
    MIDDLEWARE_RECONNECT_TIMEOUT = 30
    CONNECT_RETRY = 3
    ALIVE_CYCLE_SCALER = 2.1
    HANDLE_MQTT_MESSAGE_IGNORE_ERROR_LIST = [
        MXErrorCode.NO_ERROR,
        MXErrorCode.DUPLICATE,
        MXErrorCode.TARGET_NOT_FOUND,
    ]

    def __init__(
        self,
        name: str = MXThing.DEFAULT_NAME,
        nick_name: str = MXThing.DEFAULT_NAME,
        category: DeviceCategory = DeviceCategory.Undefined,
        device_type: MXDeviceType = MXDeviceType.NORMAL,
        desc='',
        version=sdk_version(),
        service_list: List[MXService] = list(),
        alive_cycle: int = 60,
        is_super: bool = False,
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
    ):
        self._thing_data: MXThing = MXThing(
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
        )

        if self.is_super and not self.is_parallel:
            raise MXValueError('Super Thing must be parallel')
        if is_ble_wifi and (is_builtin or is_manager):
            MXLOG_WARN(f'Flag `is_ble_wifi` and `is_builtin` cannot be True at the same time. Flag `is_ble_wifi` will be disabled.')
            is_ble_wifi = False

        # KVS Storage
        self._reset_kvs = reset_kvs
        self._kv_controller: KVStoreController = None
        self._kvs_storage_path = kvs_storage_path

        # Log
        self._log_mode = log_mode
        self._log_enable = log_enable
        self._log_path = log_path if log_path else DEFAULT_LOG_PATH
        self._async_log = async_log

        # WiFi
        self._ssid = ''
        self._pw = ''

        # MQTT
        self._mqtt_client: MQTTClient = None
        self._host = ip
        self._port = port
        self._ssl_ca_path = ssl_ca_path
        self._ssl_cert_path = ssl_cert_path
        self._ssl_key_path = ssl_key_path
        self._ssl_enable = None

        # Util
        self._append_mac_address = append_mac_address
        self._no_wait_request_register = no_wait_request_register
        self._wait_request_register_task: asyncio.Task = None

        # Queue
        # self._receive_queue: asyncio.Queue = asyncio.Queue()
        self._receive_queue: Dict[MXProtocolType, asyncio.Queue] = {
            k: asyncio.Queue()
            for k in [
                MXProtocolType.Base.MT_REQUEST_REGISTER_INFO,
                MXProtocolType.Base.MT_REQUEST_UNREGISTER,
                MXProtocolType.Base.MT_RESULT_REGISTER,
                MXProtocolType.Base.MT_RESULT_UNREGISTER,
                MXProtocolType.Base.MT_RESULT_BINARY_VALUE,
                MXProtocolType.Base.MT_EXECUTE,
                MXProtocolType.Base.MT_IN_EXECUTE,
                MXProtocolType.WebClient.ME_RESULT_HOME,
            ]
        }

        # Tasks
        self._g_exit = asyncio.Event()
        self._task_list: List[asyncio.Task] = []

        self._loop: asyncio.BaseEventLoop = None
        self._state = ThingState.RESET
        self._ble_advertiser = BLEAdvertiser(server_name=f'JOI SD {get_mac_address()[6:]}')
        self._ethernet_manager = EthernetManager()
        self._wifi_manager = WiFiManager()
        self._zeroconf = Zeroconf()
        self._mqtt_mdns_service: ServiceInfo = None
        self._mqtt_ssl_mdns_service: ServiceInfo = None

        self._init_logger()

    def __eq__(self, o: 'MXBigThing') -> bool:
        instance_check = isinstance(o, MXBigThing)
        is_parallel_check = self.is_parallel == o.is_parallel
        is_super_check = self.is_super == o.is_super

        return super().__eq__(o) and instance_check and is_parallel_check and is_super_check

    def __getstate__(self):
        state = super().__getstate__()

        state['_host'] = self._host
        state['_port'] = self._port
        state['_ssl_ca_path'] = self._ssl_ca_path
        state['_ssl_cert_path'] = self._ssl_cert_path
        state['_ssl_key_path'] = self._ssl_key_path
        state['_append_mac_address'] = self._append_mac_address

        del state['_log_mode']
        del state['_log_enable']
        del state['_log_path']
        del state['_mqtt_client']
        del state['_g_exit']

        return state

    def __setstate__(self, state):
        super().__setstate__(state)

        self._host = state['_host']
        self._port = state['_port']
        self._ssl_ca_path = state['_ssl_ca_path']
        self._ssl_cert_path = state['_ssl_cert_path']
        self._ssl_key_path = state['_ssl_key_path']
        self._append_mac_address = state['_append_mac_address']

        self._log_mode = MXPrintMode.ABBR
        self._log_enable = True
        self._log_path = ''
        self._mqtt_client = None
        self._g_exit = asyncio.Event()

    async def _setup(self) -> 'MXBigThing':
        if not check_python_version():
            raise MXNotSupportedError('Python version must be 3.7>=')

        self.name = self._thing_data.generate_thing_id(self.name, self._append_mac_address)
        self._load_kvs()

        if not 'mqtts://' in self._host or not 'ssl://' in self._host or not 'mqtt://' in self._host:
            if 'mqtts://' in self._host:
                self._ssl_enable = True
                self._host = self._host.removeprefix('mqtts://')
            elif 'ssl://' in self._host:
                self._ssl_enable = True
                self._host = self._host.removeprefix('ssl://')
            elif 'mqtt://' in self._host:
                self._ssl_enable = False
                self._host = self._host.removeprefix('mqtt://')

        self._host = convert_url_to_ip(self._host)
        if not is_valid_ip_address(self._host) or not 1024 < self._port <= 65535:
            raise MXValueError(f"Invalid IP address or port number: {self._host}:{self._port}")
        else:
            self._kv_controller.set(KVS_KEY_HOST, self._host)
            self._kv_controller.set(KVS_KEY_PORT, self._port)

        for service in self.service_list:
            service.add_tag(MXTag(self.name))

        # FIXME: Later, username and password options must be given by argument of the MXBigThing class
        self._mqtt_client = MQTTClient(client_id=self.name)
        self._mqtt_client.set_auth_credentials('tester', 'test12')
        self._mqtt_client.set_config({'reconnect_delay': 1})

        self._loop = asyncio.get_running_loop()

        self._task_list.append(asyncio.create_task(self._alive_check()))

        return self

    async def run(self, pre_run_callback: Callable[..., Any] = None, await_pre_run: bool = False) -> None:
        await self._setup()

        if asyncio.iscoroutinefunction(pre_run_callback):
            pre_run_task = asyncio.create_task(pre_run_callback())
            if await_pre_run:
                await pre_run_task
        elif callable(pre_run_callback):
            if await_pre_run:
                pre_run_callback()
            else:
                self._loop.run_in_executor(None, pre_run_callback)
        elif pre_run_callback is not None:
            raise ValueError("`pre_run_callback` must be either a callable or a coroutine function")

        await self._main_event_loop()

    async def _wrapup(self) -> None:
        try:
            if self._mqtt_client and self._mqtt_client.is_connected:
                self._send_TM_UNREGISTER(self._thing_data)
                # FIXME: Need to wait for the result of unregister
                # recv_msg = await self._receive_queue[MXProtocolType.Base.MT_RESULT_UNREGISTER].get()
                # error = await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data)

        except Exception as e:
            print_error(e)
            return False
        finally:
            if await self._ble_advertiser.is_advertising():
                await self._ble_advertiser.stop()

            self._unregister_mdns_service()

            if self._mqtt_client and self._mqtt_client.is_connected:
                await self._disconnect_from_broker(disconnect_try=MXBigThing.CONNECT_RETRY)

            if self._thing_data.middleware_name:
                self._kv_controller.save_to_disk()
            self._kv_controller.close()

            for task in self._task_list:
                task.cancel()

            MXLOG_DEBUG('Thing Exit', 'red')
            sys.exit(0)

    # ================================================================================================= #
    #   _______  _                            _   ______                    _    _                      #
    #  |__   __|| |                          | | |  ____|                  | |  (_)                     #
    #     | |   | |__   _ __  ___   __ _   __| | | |__  _   _  _ __    ___ | |_  _   ___   _ __   ___   #
    #     | |   | '_ \ | '__|/ _ \ / _` | / _` | |  __|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|  #
    #     | |   | | | || |  |  __/| (_| || (_| | | |   | |_| || | | || (__ | |_ | || (_) || | | |\__ \  #
    #     |_|   |_| |_||_|   \___| \__,_| \__,_| |_|    \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/  #
    # ================================================================================================= #

    async def _alive_check(self) -> None:
        """
        주기적으로 Thing의 상태를 확인하고, alive_cycle을 초과하면 TM_ALIVE 를 전송합니다.
        """
        check_interval = THREAD_TIME_OUT
        threshold = self.alive_cycle / MXBigThing.ALIVE_CYCLE_SCALER

        while True:
            await asyncio.sleep(check_interval)

            if self._state is not ThingState.RUNNING:
                continue

            elapsed = get_current_datetime() - self.last_alive_time
            if elapsed <= threshold:
                continue

            self._send_TM_ALIVE(self._thing_data)

    async def _RESET_state_process(self):
        if self._kv_controller.exists(KVS_KEY_MIDDLEWARE_NAME):
            self.next_state = ThingState.NETWORK_SETUP
        elif self.is_ble_wifi:
            self.next_state = ThingState.BLE_ADVERTISE
        elif self.is_builtin or self.is_manager or self._no_wait_request_register:
            self.next_state = ThingState.NETWORK_SETUP
        else:
            self.next_state = ThingState.NETWORK_SETUP

    async def _BLE_ADVERTISE_state_process(self):
        # BLE Advertise
        if not self._ble_advertiser.is_initialized:
            await self._ble_advertiser.init(thing_id=self.name)

        if await self._ble_advertiser.is_advertising():
            await self._ble_advertiser.stop()
        await self._ble_advertiser.start()

        # Save WiFi, Broker info
        MXLOG_INFO(f'Wait for WiFi credentials from BLE...')
        self._ssid, self._pw, broker, ble_error = await self._ble_advertiser.wait_until_wifi_credentials_set(timeout=None)
        self._host = broker.split(':')[0]
        self._port = int(broker.split(':')[1])

        if ble_error != BLEErrorCode.NO_ERROR:
            MXLOG_CRITICAL(f'Something getting wrong while BLE setup! error code: {ble_error}')
            if await self._ble_advertiser.is_advertising():
                await self._ble_advertiser.stop()
            self.next_state = ThingState.RESET
            return

        self.next_state = ThingState.NETWORK_SETUP

    async def _NETWORK_SETUP_state_process(self):
        if ssid := await self._wifi_manager.get_current_ssid():
            self._ssid = ssid
            self._kv_controller.set_many(
                {
                    KVS_KEY_SSID: self._ssid,
                }
            )

            self.next_state = ThingState.BROKER_SETUP
            return
        elif self._ethernet_manager.is_connected():
            self.next_state = ThingState.BROKER_SETUP
            return

        # WiFi Connect
        self._wifi_manager.ssid = self._ssid
        self._wifi_manager.password = self._pw

        wifi_connect_try = MXBigThing.CONNECT_RETRY
        while wifi_connect_try > 0:
            try:
                connect_result = await asyncio.wait_for(self._wifi_manager.connect(), timeout=30)
                # connect_result = await self._wifi_manager.connect()
                if not connect_result:
                    MXLOG_INFO(f'Connect to SSID {self._wifi_manager.ssid} failed... (try: {wifi_connect_try})', success=False)
                    wifi_connect_try -= 1
                    continue
            except asyncio.TimeoutError:
                MXLOG_INFO(f'Connect to SSID {self._wifi_manager.ssid} failed... (try: {wifi_connect_try})', success=False)
                wifi_connect_try -= 1
                continue

            # if self._wifi_manager.check_connection(ssid=self._ssid) and self._wifi_manager.network_reachable(self._host, self._port):
            if self._wifi_manager.check_connection(ssid=self._ssid):
                MXLOG_INFO(f'WiFi connection success. SSID: {self._wifi_manager.get_connected_wifi_ssid()}', success=True)

                # Ready to receive TM_REQUEST_REGISTER_INFO
                self._ble_advertiser.write_characteristic(
                    DeviceWifiService.ErrorCodeCharacteristic().uuid, bytearray(str(BLEErrorCode.NO_ERROR.value).encode())
                )

                self._kv_controller.set_many(
                    {
                        KVS_KEY_SSID: self._ssid,
                    }
                )

                self.next_state = ThingState.BROKER_SETUP
                return
            else:
                if wifi_connect_try > 0:
                    MXLOG_INFO(f'Connect to SSID {self._wifi_manager.ssid} failed... (try: {wifi_connect_try})', success=False)
                    wifi_connect_try -= 1
                else:
                    MXLOG_INFO(f'WiFi connection failed... Go back to BLE setup.', success=False)
                    wifi_connect_try = MXBigThing.CONNECT_RETRY
                    self.next_state = ThingState.RESET
                    return
        else:
            MXLOG_INFO(f'WiFi connection failed... Go back to BLE setup.', success=False)
            wifi_connect_try = MXBigThing.CONNECT_RETRY
            self.next_state = ThingState.RESET

    async def _BROKER_SETUP_state_process(self):
        if not await self._connect_to_broker(MXBigThing.CONNECT_RETRY * 10):
            MXLOG_INFO(f'Connect to broker failed... Check broker host and port -> {self._host}:{self._port}. Go back to BLE setup.', success=False)
            self.next_state = ThingState.RESET
            return

        # Setup avahi mDNS service
        if not (self.is_manager or self.is_builtin):
            rst = self._register_mdns_service()
            if not rst:
                MXLOG_INFO(f'Register mDNS service failed... Retry to register mDNS service.', success=False)
                self._unregister_mdns_service()
                self.next_state = ThingState.BROKER_SETUP
                return

        self._kv_controller.set_many(
            {
                KVS_KEY_HOST: self._host,
                KVS_KEY_PORT: self._port,
            }
        )

        self.next_state = ThingState.BROKER_CONNECTED

    async def _BROKER_CONNECTED_state_process(self):

        async def wait_for_register(target_thing: MXThing) -> bool:
            recv_msg = await self._receive_queue[MXProtocolType.Base.MT_RESULT_REGISTER].get()
            result = await self._handle_mqtt_message(recv_msg, target_thing=target_thing, state_change=False)
            if not result in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE, MXErrorCode.INVALID_REQUEST, MXErrorCode.INVALID_DESTINATION]:
                return False
            else:
                return True

        # Prepare to register
        self._subscribe_init_topic_list(self._thing_data)

        if self.is_builtin or self.is_manager or self._no_wait_request_register or self._kv_controller.exists(KVS_KEY_MIDDLEWARE_NAME):
            if self.is_builtin or self.is_manager:
                MXLOG_INFO(f'Run Thing with builtin/plugin mode')
            elif self._no_wait_request_register:
                MXLOG_INFO(f'Run Thing with no wait request register mode')
            else:
                MXLOG_INFO(f'Run Thing with load config from KVS ({self._kv_controller.db_path})')

            self._send_TM_REGISTER(self._thing_data)
        else:
            MXLOG_INFO(f'Wait for receive MT_REQUEST_REGISTER_INFO packet from middleware...')

            # Wait for register info request from Middleware
            self._wait_request_register_task = asyncio.create_task(self._receive_queue[MXProtocolType.Base.MT_REQUEST_REGISTER_INFO].get())
            recv_msg = await self._wait_request_register_task
            result = await self._handle_mqtt_message(recv_msg, target_thing=self._thing_data, state_change=False)
            if result != MXErrorCode.NO_ERROR:
                self.next_state = ThingState.SHUTDOWN
                return

        if await wait_for_register(self._thing_data):
            self._subscribe(MXProtocolType.Base.MT_REQUEST_UNREGISTER.value % self.name)
            self._subscribe_service_topic_list(self._thing_data)
            self.next_state = ThingState.REGISTERED
        else:
            self.next_state = ThingState.SHUTDOWN

    async def _REGISTERED_state_process(self):
        self.next_state = ThingState.RUNNING

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

    async def _UNREGISTERED_state_process(self):
        if await self._ble_advertiser.is_advertising():
            await self._ble_advertiser.stop()

        self._unregister_mdns_service()

        # NOTE (thsvkd): Wait for finish previous MQTT tasks... It needs to be modified to wait based on conditions, not fixed time.
        await asyncio.sleep(0.1)
        if self._mqtt_client and self._mqtt_client.is_connected:
            await self._disconnect_from_broker(disconnect_try=MXBigThing.CONNECT_RETRY)
            self._kv_controller.reset_db()

        # TODO: need to disconnect from wifi router

        self.next_state = ThingState.RESET

    async def _NETWORK_LOST_state_process(self):
        wifi_connect_try = MXBigThing.CONNECT_RETRY
        while wifi_connect_try > 0:
            await self._wifi_manager.connect()
            if self._wifi_manager.check_connection(ssid=self._ssid) and self._wifi_manager.network_reachable(self._host, self._port):
                # if self._wifi_manager.check_connection(ssid=self._ssid):
                MXLOG_INFO(f'WiFi connection success. SSID: {self._wifi_manager.get_connected_wifi_ssid()}', success=True)
                self.next_state = ThingState.BROKER_LOST
                return
            else:
                if wifi_connect_try > 0:
                    MXLOG_INFO(f'Connect to SSID {self._wifi_manager.ssid} failed... (try: {wifi_connect_try})', success=False)
                    wifi_connect_try -= 1
                else:
                    MXLOG_INFO(f'WiFi connection failed... Go back to BLE setup.', success=False)
                    wifi_connect_try = MXBigThing.CONNECT_RETRY
                    self.next_state = ThingState.RESET
                    return

    async def _BROKER_LOST_state_process(self):
        if self._mqtt_client.is_connected:
            self.next_state = ThingState.BROKER_RECONNECTED
        else:
            self.next_state = ThingState.BROKER_LOST
            await asyncio.sleep(1)

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
                self._resubscribe_all()

                self._send_TM_ALIVE(self._thing_data)
                self.next_state = ThingState.REGISTERED
                break
            except asyncio.QueueEmpty:
                await asyncio.sleep(MXBigThing.MIDDLEWARE_ONLINE_CHECK_INTERVAL)
        else:
            if self.is_builtin or self.is_manager:
                self.next_state = ThingState.SHUTDOWN
            else:
                if self.is_ble_wifi:
                    self.next_state = ThingState.BLE_ADVERTISE
                elif self.is_builtin or self.is_manager:
                    self.next_state = ThingState.SHUTDOWN
                else:
                    self.next_state = ThingState.BROKER_CONNECTED
                MXLOG_ERROR(f'Middleware is offline... Go back to {self.next_state.name} setup.')

    async def _main_event_loop(self):
        while not self._g_exit.is_set():
            try:
                await asyncio.sleep(THREAD_TIME_OUT)

                if self._state == ThingState.RESET:
                    await self._RESET_state_process()
                elif self._state == ThingState.BLE_ADVERTISE:
                    await self._BLE_ADVERTISE_state_process()
                elif self._state == ThingState.NETWORK_SETUP:
                    await self._NETWORK_SETUP_state_process()
                elif self._state == ThingState.BROKER_SETUP:
                    await self._BROKER_SETUP_state_process()
                elif self._state == ThingState.BROKER_CONNECTED:
                    await self._BROKER_CONNECTED_state_process()
                elif self._state == ThingState.REGISTERED:
                    await self._REGISTERED_state_process()
                elif self._state == ThingState.RUNNING:
                    await self._RUNNING_state_process()
                elif self._state == ThingState.UNREGISTERED:
                    await self._UNREGISTERED_state_process()
                elif self._state == ThingState.NETWORK_LOST:
                    await self._NETWORK_LOST_state_process()
                elif self._state == ThingState.BROKER_LOST:
                    await self._BROKER_LOST_state_process()
                elif self._state == ThingState.BROKER_RECONNECTED:
                    await self._BROKER_RECONNECTED_state_process()
                elif self._state == ThingState.SHUTDOWN:
                    await self._wrapup()
                else:
                    MXLOG_CRITICAL(f'Unexpected state!!! state: {self._state}')
                    self.next_state = ThingState.SHUTDOWN
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    MXLOG_ERROR('KeyboardInterrupt Exit')
                    self.next_state = ThingState.SHUTDOWN
                    await self._wrapup()
                elif isinstance(e, asyncio.CancelledError):
                    MXLOG_ERROR('asyncio.CancelledError Exit')
                    self.next_state = ThingState.SHUTDOWN
                    await self._wrapup()
                elif isinstance(e, zeroconf._exceptions.NonUniqueNameException):
                    self._unregister_mdns_service()
                    self.next_state = ThingState.BROKER_SETUP
                elif isinstance(e, ConnectionRefusedError):
                    MXLOG_INFO(f'Connect to broker failed... broker - {self._host}:{self._port}', success=False)
                elif isinstance(e, ConnectionResetError):
                    MXLOG_INFO(f'Disconnect from broker failed... broker - {self._host}:{self._port}', success=False)
                else:
                    print_error(e)
                    raise e

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

    async def _handle_mqtt_message(self, msg: MQTTMessage, target_thing: MXThing, state_change: bool = True) -> MXErrorCode:
        topic = decode_MQTT_message(msg)[0]
        protocol = MXProtocolType.get(topic)

        if protocol == MXProtocolType.Base.MT_REQUEST_REGISTER_INFO:
            error = self._handle_MT_REQUEST_REGISTER_INFO(msg, target_thing=target_thing)
        elif protocol == MXProtocolType.Base.MT_REQUEST_UNREGISTER:
            error = self._handle_MT_REQUEST_UNREGISTER(msg, target_thing=target_thing)
        elif protocol == MXProtocolType.Base.MT_RESULT_REGISTER:
            error = self._handle_MT_RESULT_REGISTER(msg, target_thing=target_thing)
            if error in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE]:
                # NOTE (thsvkd): MT_RESULT_REGISTER topic also use as a trigger for sending the current
                # Value to the middleware regardless of the cycle. If the MT_RESULT_REGISTER topic comes
                # while running after being registered, it is implemented to work as a trigger for value
                # publish by initializing the values.
                if self._state in [ThingState.RUNNING, ThingState.REGISTERED]:
                    for value in target_thing.value_list:
                        value.is_initialized = False

                self.next_state = ThingState.REGISTERED if state_change else self._state
            elif error == MXErrorCode.INVALID_DESTINATION:
                self.next_state = ThingState.REGISTERED if state_change else self._state
            elif error == MXErrorCode.FAIL:
                MXLOG_ERROR(f'{PrintTag.ERROR} Register failed... Thing {self.name} register packet is not valid. error code: {error}')
                self.next_state = ThingState.SHUTDOWN if state_change else self._state
            elif error == MXErrorCode.INVALID_REQUEST:
                MXLOG_DEBUG(f'Receive unexpected packet... Drop it. topic: {topic}', 'magenta')
            else:
                MXLOG_ERROR(f'{PrintTag.ERROR} Register failed... Thing {self.name} register packet is not valid. error code: {error}')
                self.next_state = ThingState.SHUTDOWN if state_change else self._state
        elif protocol == MXProtocolType.Base.MT_RESULT_UNREGISTER:
            error = self._handle_MT_RESULT_UNREGISTER(msg, target_thing=target_thing)
            if error in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE]:
                self.next_state = ThingState.UNREGISTERED if state_change else self._state
            elif error == MXErrorCode.INVALID_DESTINATION:
                self.next_state = ThingState.UNREGISTERED if state_change else self._state
            elif error == MXErrorCode.FAIL:
                MXLOG_ERROR(f'{PrintTag.ERROR} Unregister failed...')
            elif error == MXErrorCode.INVALID_REQUEST:
                MXLOG_DEBUG(f'Receive unexpected packet... Drop it. topic: {topic}', 'magenta')
            else:
                MXLOG_ERROR(f'{PrintTag.ERROR} Unregister failed... Thing {self.name} Unregister packet is not valid. error code: {error}')
                self.next_state = ThingState.SHUTDOWN if state_change else self._state
        elif protocol == MXProtocolType.Base.MT_RESULT_BINARY_VALUE:
            error = self._handle_MT_RESULT_BINARY_VALUE(msg, target_thing=target_thing)
        elif protocol in [MXProtocolType.Base.MT_EXECUTE, MXProtocolType.Base.MT_IN_EXECUTE]:
            error = await self._handle_MT_EXECUTE(msg, target_thing=target_thing)
        # for Auto Re-register feature
        elif protocol == MXProtocolType.WebClient.ME_RESULT_HOME:
            error = self._handle_ME_HOME_RESULT(msg)

            result_home_topic = MXProtocolType.WebClient.ME_RESULT_HOME.value % '+'
            if error == MXErrorCode.NO_ERROR:
                self._unsubscribe(result_home_topic)
                self.next_state = ThingState.REGISTERED if state_change else self._state
        else:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Unexpected topic! topic: {topic}')
            error = MXErrorCode.FAIL

        return error

    # ===============
    # ___  ___ _____
    # |  \/  ||_   _|
    # | .  . |  | |
    # | |\/| |  | |
    # | |  | |  | |
    # \_|  |_/  \_/
    # ===============

    def _handle_MT_REQUEST_REGISTER_INFO(self, msg: MQTTMessage, target_thing: MXThing) -> MXErrorCode:
        request_register_info_msg = MXRequestRegisterInfoMessage(msg)

        if request_register_info_msg.topic_error or request_register_info_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        middleware_name = request_register_info_msg.middleware_name
        MXLOG_INFO(f'Receive register request from Middleware {middleware_name}! Send Register packet.', success=True)

        target_thing.request_client_id = request_register_info_msg.client_id
        self._send_TM_REGISTER(target_thing)
        return MXErrorCode.NO_ERROR

    def _handle_MT_REQUEST_UNREGISTER(self, msg: MQTTMessage, target_thing: MXThing) -> MXErrorCode:
        request_unregister_msg = MXRequestUnregisterMessage(msg)

        if request_unregister_msg.topic_error or request_unregister_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        middleware_name = request_unregister_msg.middleware_name
        MXLOG_INFO(f'Receive unregister request from Middleware {middleware_name}! Send Unregister packet.', success=True)

        target_thing.request_client_id = request_unregister_msg.client_id
        self._send_TM_UNREGISTER(target_thing)
        return MXErrorCode.NO_ERROR

    def _handle_MT_RESULT_REGISTER(self, msg: MQTTMessage, target_thing: MXThing) -> MXErrorCode:
        register_result_msg = MXRegisterResultMessage(msg)
        error = register_result_msg.error

        if register_result_msg.topic_error or register_result_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        if target_thing.name != register_result_msg.thing_name:
            # MXLOG_DEBUG(
            #     f'[{get_current_function_name()}] Wrong payload arrive... {target_thing.name} should be arrive, not {register_result_msg.thing_name}'
            # )
            return MXErrorCode.INVALID_DESTINATION

        if error in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE]:
            MXLOG_DEBUG(
                f'{PrintTag.GOOD if error == MXErrorCode.NO_ERROR else PrintTag.DUP} Thing {target_thing.name} {colored("register", "green")} success!'
            )
            target_thing.middleware_name = register_result_msg.middleware_name
            for service in target_thing.service_list:
                service.middleware_name = target_thing.middleware_name
                service.thing_name = target_thing.name
            self._subscribe_service_topic_list(target_thing)

            self._kv_controller.set_many(
                {
                    KVS_KEY_NAME: self.name,
                    KVS_KEY_NICK_NAME: self.nick_name,
                    KVS_KEY_CATEGORY: self.category.name,
                    KVS_KEY_DESC: self.desc,
                    KVS_KEY_VERSION: self.version,
                    KVS_KEY_ALIVE_CYCLE: self.alive_cycle,
                    KVS_KEY_MIDDLEWARE_NAME: self.middleware_name,
                    # KVS_KEY_LAST_ALIVE_TIME: self.last_alive_time,
                    # KVS_KEY_SSID: self._ssid,
                    # KVS_KEY_HOST: self._host,
                    # KVS_KEY_PORT: self._port,
                    KVS_KEY_SSL_CA_PATH: self._ssl_ca_path,
                    KVS_KEY_SSL_CERT_PATH: self._ssl_cert_path,
                    KVS_KEY_SSL_KEY_PATH: self._ssl_key_path,
                }
            )
            self._kv_controller.save_to_disk()
        elif error == MXErrorCode.FAIL:
            MXLOG_DEBUG(
                f'{PrintTag.ERROR} Register failed... Thing {target_thing.name} register packet is not valid. error code: {register_result_msg.error}',
                'red',
            )
        else:
            MXLOG_DEBUG(
                f'{PrintTag.ERROR} Register failed... Unexpected error occurred!!! error code: {register_result_msg.error}',
                'red',
            )

        return error

    def _handle_MT_RESULT_UNREGISTER(self, msg: MQTTMessage, target_thing: MXThing) -> MXErrorCode:
        unregister_result_msg = MXUnregisterResultMessage(msg)
        error = unregister_result_msg.error

        if unregister_result_msg.topic_error or unregister_result_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        if target_thing.name != unregister_result_msg.thing_name:
            # MXLOG_DEBUG(
            #     f'[{get_current_function_name()}] Wrong payload arrive... {target_thing.name} should be arrive, not {unregister_result_msg.thing_name}',
            #     'red',
            # )
            return MXErrorCode.INVALID_DESTINATION

        if error in [MXErrorCode.NO_ERROR, MXErrorCode.DUPLICATE]:
            MXLOG_DEBUG(
                f'{PrintTag.GOOD if error == MXErrorCode.NO_ERROR else PrintTag.DUP} Thing {target_thing.name} {colored("unregister", "red")} success!'
            )
            self._unsubscribe_all_topic_list(target_thing)
        elif error == MXErrorCode.FAIL:
            MXLOG_DEBUG(
                f'{PrintTag.ERROR} Unregister failed... Thing {target_thing.name} unregister packet is not valid. error code: {unregister_result_msg.error}',
                'red',
            )
        else:
            MXLOG_DEBUG(
                f'{PrintTag.ERROR} Unregister failed... Unexpected error occurred!!! error code: {unregister_result_msg.error}',
                'red',
            )

        return error

    async def _handle_MT_EXECUTE(self, msg: MQTTMessage, target_thing: MXThing) -> Tuple[asyncio.Task, MXErrorCode]:
        execute_msg = MXExecuteMessage(msg)
        if execute_msg.topic_error or execute_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        target_function = target_thing.get_function(execute_msg.function_name)
        if not target_function:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Target function not found! - topic: {decode_MQTT_message(msg)[0]}')
            return MXErrorCode.TARGET_NOT_FOUND
        if target_thing.name != execute_msg.thing_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong payload arrive... {target_thing.name} should be arrive, not {execute_msg.thing_name}'
            )
            return MXErrorCode.INVALID_REQUEST
        if execute_msg.topic_error or execute_msg.payload_error:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] execute_msg error! - topic: {decode_MQTT_message(msg)[0]}{execute_msg.topic_error}')
            return MXErrorCode.INVALID_REQUEST

        execute_protocol = MXProtocolType.get(execute_msg.topic)
        if execute_protocol == MXProtocolType.Base.MT_EXECUTE:
            action_type = MXActionType.EXECUTE
            request_class = MXExecuteRequest
        elif execute_protocol == MXProtocolType.Base.MT_IN_EXECUTE:
            action_type = MXActionType.INNER_EXECUTE
            request_class = MXInnerExecuteRequest
        else:
            raise MXValueError('Invalid protocol type')

        execute_request = request_class(
            trigger_msg=execute_msg,
            result_msg=MXExecuteResultMessage(
                function_name=target_function.name,
                thing_name=target_function.thing_name,
                middleware_name=target_function.middleware_name,
                scenario=execute_msg.scenario,
                client_id=execute_msg.client_id,
                request_ID=execute_msg.request_ID,
                return_type=target_function.return_type,
                return_value=None,
                action_type=action_type,
            ),
        )

        # 서로의 arg_list가 일치하는 지 확인한다.
        if not compare_arg_list(target_function.arg_list, list(execute_request.trigger_msg.tuple_arguments())):
            execute_request.result_msg.error = MXErrorCode.EXECUTE_ARG_FAIL
            self._send_TM_RESULT_EXECUTE(execute_request, self._thing_data)
            return execute_request.result_msg.error

        # 중복된 시나리오로부터 온 실행 요청이면 -4 에러코드를 보낸다.
        if execute_request.trigger_msg.scenario in target_function.running_scenario_list:
            execute_request.result_msg.error = MXErrorCode.DUPLICATE
            self._send_TM_RESULT_EXECUTE(execute_request, self._thing_data)
            return execute_request.result_msg.error

        # 병렬실행이 가능하거나 현재 함수가 실행 중이지 않으면 함수를 실행한다.
        if target_thing.is_parallel or not target_function._running:
            curr_time = get_current_datetime(TimeFormat.DATETIME2)
            MXLOG_INFO(f'[FUNC RUN REQUEST] Request function {target_function.name} run by {execute_msg.scenario} at [{curr_time}]', success=True)

            self._create_execute_task(target_thing, target_function, execute_request)
        else:
            execute_request.result_msg.error = MXErrorCode.FAIL
            self._send_TM_RESULT_EXECUTE(execute_request, self._thing_data)
            return execute_request.result_msg.error

        return MXErrorCode.NO_ERROR

    def _handle_MT_RESULT_BINARY_VALUE(self, msg: MQTTMessage, target_thing: MXThing) -> bool:
        binary_value_result_msg = MXBinaryValueResultMessage(msg)

        if binary_value_result_msg.topic_error or binary_value_result_msg.payload_error:
            return MXErrorCode.INVALID_REQUEST

        if target_thing.name != binary_value_result_msg.thing_name:
            MXLOG_CRITICAL(
                f'[{get_current_function_name()}] Wrong payload arrive... {target_thing.name} should be arrive, not {binary_value_result_msg.thing_name}'
            )
            return MXErrorCode.INVALID_REQUEST

        for value in target_thing.value_list:
            if value.name == binary_value_result_msg.value_name and value.type == MXType.BINARY:
                value.binary_sending = False
                return MXErrorCode.NO_ERROR
        else:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Value {binary_value_result_msg.value_name} does not exist!!!')
            return MXErrorCode.TARGET_NOT_FOUND

    # ===============
    #  _____ ___  ___
    # |_   _||  \/  |
    #   | |  | .  . |
    #   | |  | |\/| |
    #   | |  | |  | |
    #   \_/  \_|  |_/
    # ===============

    def _send_TM_REGISTER(self, thing_data: MXThing) -> None:
        self._subscribe_init_topic_list(thing_data)

        register_msg = thing_data.generate_register_message()
        if not register_msg:
            raise Exception('TM_REGISTER packet error')

        register_mqtt_msg = register_msg.mqtt_message()
        self._publish(register_mqtt_msg.topic, register_mqtt_msg.payload)

    def _send_TM_UNREGISTER(self, thing_data: MXThing):
        unregister_msg = thing_data.generate_unregister_message()
        if not unregister_msg:
            raise Exception('TM_UNREGISTER packet error')

        unregister_mqtt_msg = unregister_msg.mqtt_message()
        self._publish(unregister_mqtt_msg.topic, unregister_mqtt_msg.payload)

    def _send_TM_ALIVE(self, thing_data: MXThing):
        alive_msg = thing_data.generate_alive_message()
        alive_mqtt_msg = alive_msg.mqtt_message()
        self._publish(alive_mqtt_msg.topic, alive_mqtt_msg.payload)
        thing_data.last_alive_time = get_current_datetime()

        self._kv_controller.set(KVS_KEY_LAST_ALIVE_TIME, thing_data.last_alive_time)
        # self._kv_controller.save_to_disk()

    def _send_TM_VALUE_PUBLISH(self, value: MXValue) -> None:
        if MXType.get(type(value.last_value)) != value.type:
            MXLOG_WARN(
                f'[{get_current_function_name()}] Value type mismatch... (Value: {value.name} | expected value type: {value.type}, return value type: {MXType.get(type(value.last_value))}|{value.last_value})'
            )
            return

        if value.type == MXType.STRING and len(value.last_value) > STRING_VALUE_LIMIT:
            MXLOG_WARN(
                f'[{get_current_function_name()}] String value should be limited to `STRING_VALUE_LIMIT`(100) words... (len: {len(value.last_value)})'
            )
            value_copy = copy.deepcopy(value)
            value_copy.last_value = value.last_value[:STRING_VALUE_LIMIT]
            value_publish_msg = value_copy.generate_value_publish_message()
            value_publish_mqtt_msg = value_publish_msg.mqtt_message()
        else:
            value_publish_msg = value.generate_value_publish_message()
            value_publish_mqtt_msg = value_publish_msg.mqtt_message()

        if value.type == MXType.BINARY:
            value.binary_sending = True

        self._publish(value_publish_mqtt_msg.topic, value_publish_mqtt_msg.payload)

    def _send_TM_RESULT_EXECUTE(self, execute_request: Union[MXExecuteRequest, MXInnerExecuteRequest], thing_data: MXThing) -> MXErrorCode:
        target_function = thing_data.get_function(execute_request.result_msg.function_name)
        if target_function is None:
            return MXErrorCode.TARGET_NOT_FOUND

        execute_result_msg = target_function.generate_execute_result_message(execute_request)
        execute_result_mqtt_msg = execute_result_msg.mqtt_message()
        self._publish(execute_result_mqtt_msg.topic, execute_result_mqtt_msg.payload)
        return MXErrorCode.NO_ERROR

    # ================
    #  __  __  ______
    # |  \/  ||  ____|
    # | \  / || |__
    # | |\/| ||  __|
    # | |  | || |____
    # |_|  |_||______|
    # ================

    # for Auto Re-register feature
    def _handle_ME_HOME_RESULT(self, msg: MQTTMessage) -> MXErrorCode:
        execute_msg = MXHomeResultMessage(msg)
        if 'location' in execute_msg.payload:
            MXLOG_INFO(f'Middleware detected!!!')
            return MXErrorCode.NO_ERROR
        else:
            return MXErrorCode.FAIL

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def _create_execute_task(
        self,
        target_thing: MXThing,
        target_function: MXFunction,
        execute_request: Union[MXExecuteRequest, MXInnerExecuteRequest],
    ) -> asyncio.Task:
        return self._create_task(
            co_routine=target_function.execute(execute_request),
            done_callback=self._execute_done_callback,
            timeout=target_function.timeout,
            target_thing=target_thing,
            target_function=target_function,
            execute_request=execute_request,
        )

    async def _execute_done_callback(
        self,
        task: asyncio.Task,
        target_thing: MXThing,
        target_function: MXFunction,
        execute_request: MXExecuteRequest,
    ) -> None:

        async def update_values():
            '''
            Update Values that depend on the Function.
            If the Function executes successfully, update the associated Values.
            '''
            for v in target_function._value_update_map.values():
                if execute_request.result_msg.error != MXErrorCode.NO_ERROR:
                    continue

                value = v['value']
                callback = v['callback']
                arguments = execute_request.trigger_msg.arguments
                task = callback(arguments=arguments) if len(arguments) > 0 else callback()
                if isinstance(task, asyncio.Task):
                    await task
                self._send_TM_VALUE_PUBLISH(value)

        def update_return_value(return_value: MXDataType):
            callback_return_type = MXType.get(type(return_value))
            if callback_return_type != target_function._return_type and execute_request.result_msg.error == MXErrorCode.NO_ERROR:
                raise MXValueError(
                    f'expected return value type is {target_function._return_type} but, callback function\'s return value type is {callback_return_type}'
                )

            target_function.return_value = return_value
            execute_request.result_msg.return_value = return_value

        execute_msg = execute_request.trigger_msg
        return_value = None
        try:
            return_value: MXDataType = task.result()
        except KeyboardInterrupt as e:
            MXLOG_ERROR('Function execution exit by user')
            raise e
        except asyncio.CancelledError as e:
            MXLOG_ERROR('Function execution exit by user')
            raise e
        except MXTimeoutError as e:
            MXLOG_WARN(f'[FUNC TIMEOUT] function {target_function.name} by scenario {execute_msg.scenario} was timeout!!!')
            execute_request.result_msg.error = MXErrorCode.TIMEOUT
        except Exception as e:
            MXLOG_ERROR(f'[FUNC FAIL] function {target_function.name} by scenario {execute_msg.scenario} is failed while executing!!!')
            print_error(e)
            execute_request.result_msg.error = MXErrorCode.FAIL
        else:
            execute_request.result_msg.error = MXErrorCode.NO_ERROR
        finally:
            # Remove the scenario from the running scenario list
            target_function.running_scenario_list.remove(execute_msg.scenario)

            update_return_value(return_value)
            await update_values()

            # Change function state
            target_function.running = False
            execute_request.timer_end()

            MXLOG_DEBUG(
                f'[FUNC END] function {target_function.name} end. -> return value : {target_function.return_value}, duration: {execute_request._duration:.4f} Sec',
                'green',
            )

            self._send_TM_RESULT_EXECUTE(execute_request, target_thing)

    def _create_task(self, co_routine: Coroutine, done_callback: Callable[..., Any], timeout: float = 0.0, *args, **kwargs) -> asyncio.Task:
        '''
        Utility function to create an asynchronous task.

        Args:
            co_routine (Coroutine): The coroutine to be executed.
            done_callback (Callable[..., Any]): The callback function to be called once the task is completed.
            *args: Additional arguments to pass to the done_callback.
            **kwargs: Keyword arguments to pass to the done_callback.

        Returns:
            asyncio.Task: An awaitable Task object.
        '''

        def wrapper(
            co_routine: Coroutine,
            done_callback: Callable[..., Any],
            *args,
            **kwargs,
        ) -> asyncio.Task:
            event = asyncio.Event()

            async def event_wait_wrapper() -> Any:
                await event.wait()
                if timeout > 0:
                    try:
                        return await asyncio.wait_for(co_routine, timeout)
                    except asyncio.TimeoutError as e:
                        raise MXTimeoutError from e
                else:
                    return await asyncio.create_task(co_routine)

            def done_callback_wrapper(task: asyncio.Task, done_callback: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
                asyncio.create_task(done_callback(task, *args, **kwargs))

            event_wait_task = asyncio.create_task(event_wait_wrapper())
            event_wait_task.add_done_callback(
                partial(
                    done_callback_wrapper,
                    done_callback=done_callback,
                    *args,
                    **kwargs,
                )
            )

            event.set()
            return event_wait_task

        return wrapper(co_routine, done_callback, *args, **kwargs)

    # def _create_task(
    #     self,
    #     co_routine: Coroutine,
    #     done_callback: Callable[..., Any],
    #     timeout: float = 0.0,
    #     wait_return_until_done: bool = False,
    #     *args,
    #     **kwargs,
    # ) -> asyncio.Task:
    #     '''
    #     Utility function to create an asynchronous task.

    #     Args:
    #         co_routine (Coroutine): The coroutine to be executed.
    #         done_callback (Callable[..., Any]): The callback function to be called once the task is completed.
    #         *args: Additional arguments to pass to the done_callback.
    #         **kwargs: Keyword arguments to pass to the done_callback.

    #     Returns:
    #         asyncio.Task: An awaitable Task object.
    #     '''

    #     async def _wrapped_task():
    #         try:
    #             # 원본 코루틴 실행 (타임아웃 적용)
    #             result = await asyncio.wait_for(co_routine, timeout) if timeout > 0 else await co_routine
    #         except asyncio.TimeoutError as e:
    #             raise MXTimeoutError from e
    #         finally:
    #             if inspect.iscoroutinefunction(done_callback):
    #                 if wait_return_until_done:
    #                     await done_callback(result, *args, **kwargs)
    #                 else:
    #                     asyncio.create_task(done_callback(result, *args, **kwargs))
    #             else:
    #                 done_callback(result, *args, **kwargs)
    #         return result

    #     return asyncio.create_task(_wrapped_task())

    ################################################################

    # ref from paho.mqtt.python: (https://github.com/eclipse-paho/paho.mqtt.python)
    def _topic_matches_sub(sub: str, topic: str) -> bool:
        """Check whether a topic matches a subscription.

        For example:

        * Topic "foo/bar" would match the subscription "foo/#" or "+/bar"
        * Topic "non/matching" would not match the subscription "non/+/+"
        """
        matcher = MQTTMatcher()
        matcher[sub] = True
        try:
            next(matcher.iter_match(topic))
            return True
        except StopIteration:
            return False

    async def _expect(self, topic: str, payload: dict = None, payload_filter: Callable = None, timeout: float = None) -> MQTTMessage:
        async def wrapper() -> MQTTMessage:
            mqtt_msg = await self._receive_queue_get()
            if self._topic_matches_sub(topic, mqtt_msg.topic):
                if payload is not None:
                    if payload_filter is not None:
                        if payload_filter(mqtt_msg.payload):
                            return mqtt_msg
                    else:
                        if mqtt_msg.payload == payload:
                            return mqtt_msg
                else:
                    return mqtt_msg

        try:
            return asyncio.wait_for(wrapper(), timeout=timeout)
        except asyncio.TimeoutError as e:
            raise MXTimeoutError from e

    async def _publish_with_expect(
        self,
        topic: str,
        payload: dict,
        payload_filter: Callable = None,
        timeout: float = None,
    ) -> MQTTMessage:
        self._subscribe(topic)
        self._publish(topic, payload)
        try:
            return await self._expect(topic, payload=payload, payload_filter=payload_filter, timeout=timeout)
        except asyncio.TimeoutError as e:
            raise MXTimeoutError from e
        except Exception as e:
            MXLOG_ERROR(f'[{get_current_function_name()}] Unexpected error occurred: {e}')
            raise e

    def _get_function(self, function_name: str) -> MXFunction:
        return self._thing_data.get_function(function_name)

    def _receive_queue_empty(self) -> bool:
        for queue in self._receive_queue.values():
            if not queue.empty():
                return False
        return True

    async def _receive_queue_get(self) -> Optional[MQTTMessage]:
        for queue in self._receive_queue.values():
            if not queue.empty():
                return await queue.get()
        return None

    def _subscribe_init_topic_list(self, thing_data: MXThing) -> None:
        topic_list = [
            MXProtocolType.Base.MT_REQUEST_REGISTER_INFO.value % thing_data.name,
            # MXProtocolType.Base.MT_REQUEST_UNREGISTER.value % thing_data.name,
            MXProtocolType.Base.MT_RESULT_REGISTER.value % thing_data.name,
            MXProtocolType.Base.MT_RESULT_UNREGISTER.value % thing_data.name,
            MXProtocolType.Base.MT_RESULT_BINARY_VALUE.value % thing_data.name,
        ]

        for topic in topic_list:
            self._subscribe(topic)

    def _subscribe_service_topic_list(self, thing_data: MXThing):
        topic_list = []
        for function in thing_data.function_list:
            topic_list += [
                MXProtocolType.Base.MT_EXECUTE.value % (function.name, thing_data.name, '+', '+'),
                (MXProtocolType.Base.MT_EXECUTE.value % (function.name, thing_data.name, '', '')).rstrip('/'),
                MXProtocolType.Base.MT_IN_EXECUTE.value % (function.name, thing_data.name),
            ]

        for topic in topic_list:
            self._subscribe(topic)

    def _unsubscribe_service_topic_list(self):
        topic_list = []

        subscriptions: List[Subscription] = self._mqtt_client.subscriptions
        for topic in [sub.topic for sub in subscriptions]:
            if (
                MXProtocolType.Base.MT_EXECUTE.get_prefix() in topic
                or MXProtocolType.Base.MT_IN_EXECUTE.get_prefix() in topic
                or MXProtocolType.Base.MT_EXECUTE.get_prefix() in topic
            ):
                topic_list.append(topic)

        for topic in topic_list:
            self._unsubscribe(topic)

    def _unsubscribe_all_topic_list(self, target_thing: MXThing) -> None:
        subscriptions: List[Subscription] = self._mqtt_client.subscriptions
        for topic in [sub.topic for sub in subscriptions if target_thing.name in sub.topic]:
            self._unsubscribe(topic)

    def _print_packet(
        self, topic: Union[str, bytes], payload: Union[str, bytes], direction: Direction, mode: MXPrintMode = MXPrintMode.FULL, pretty: bool = False
    ) -> str:
        if isinstance(topic, bytes):
            topic = topic.decode()
        if isinstance(payload, bytes):
            payload = dict_to_json_string(json_string_to_dict(payload.decode()), ensure_ascii=False)

        topic_template = MXProtocolType.get(topic)
        if not topic_template:
            MXLOG_CRITICAL(f'[print_packet] Unknown topic!!! topic : {topic}')

        topic_indicator = '_'.join([topic_token for topic_token in topic_template.value.split('/') if topic_token != '%s'])
        payload = prune_payload(payload=dict_to_json_string(dict_object=payload, pretty=pretty), mode=mode)

        MXLOG_DEBUG(f'[{topic_indicator:20}][{direction.value}] topic: {topic} payload: {payload}')

    def add_service(self, service: MXService) -> 'MXThing':
        return self._thing_data.add_service(service)

    def dict(self) -> dict:
        return self._thing_data.dict()

    #### MQTT utils ####

    async def _connect_to_broker(self, connect_try: int = 0) -> bool:
        # Set SSL options
        if self._check_ssl_enable():
            MXLOG_INFO('Connect with SSL...')
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.load_cert_chain(certfile=self._ssl_cert_path, keyfile=self._ssl_key_path)
            ssl_context.load_verify_locations(cafile=self._ssl_ca_path)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            # ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # TLSv1.2 이상만 사용
            ssl_context.check_hostname = False
        else:
            ssl_context = False
            MXLOG_INFO('[WARN] Connect without SSL...')

        if self._port == 1883 and self._ssl_enable == True:
            MXLOG_WARN('SSL is enabled but port is 1883. Consider to check the port number.')
        elif self._port == 8883 and self._ssl_enable == False:
            MXLOG_WARN('SSL is disabled but port is 8883. Consider to check the port number.')

        async def try_to_connect() -> bool:
            async def handle_fail() -> bool:
                await asyncio.sleep(THREAD_TIME_OUT * 100)
                MXLOG_INFO(f'Connect to Broker {self._host}:{self._port} failed... (try: {connect_try})', success=False)
                return False

            try:
                if self._mqtt_client.is_connected or await self._connect(self._host, self._port, ssl=ssl_context):
                    return True

                return await handle_fail()
            except BaseException as e:
                return await handle_fail()

        # Broker Connect
        if connect_try:
            while connect_try:
                if await try_to_connect():
                    return True
                else:
                    connect_try -= 1
            else:
                MXLOG_ERROR(f'Broker connection failed...')
                connect_try = MXBigThing.CONNECT_RETRY
                return False
        else:
            return await try_to_connect()

    async def _disconnect_from_broker(self, disconnect_try: int) -> bool:
        # Broker Disconnect
        while disconnect_try:
            try:
                await self._disconnect()
                if not self._mqtt_client.is_connected:
                    return True

                await asyncio.sleep(THREAD_TIME_OUT * 10)
                MXLOG_INFO(f'Disconnect to Broker {self._host}:{self._port} failed... (try: {disconnect_try})', success=False)
                disconnect_try -= 1
            except BaseException as e:
                if isinstance(e, ConnectionResetError):
                    await asyncio.sleep(THREAD_TIME_OUT * 10)
                    MXLOG_INFO(f'Disconnect to Broker {self._host}:{self._port} failed... (try: {disconnect_try})', success=False)
                    disconnect_try -= 1
                else:
                    raise e
        else:
            MXLOG_INFO(f'Broker disconnection failed... Go back to BLE setup.', success=False)
            disconnect_try = MXBigThing.CONNECT_RETRY
            return False

    async def _connect(self, ip: str, port: int, ssl: Union[ssl.SSLContext, bool], timeout: float = 1) -> bool:
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        # self._mqtt_client.on_publish = self._on_publish
        self._mqtt_client.on_subscribe = self._on_subscribe
        self._mqtt_client.on_unsubscribe = self._on_unsubscribe
        self._mqtt_client.on_message = self._on_message

        try:
            await asyncio.wait_for(self._mqtt_client.connect(ip, port, ssl=ssl), timeout=timeout)
        except asyncio.TimeoutError:
            return False

        return self._mqtt_client.is_connected

    async def _disconnect(self):
        await self._mqtt_client.disconnect()

    def _subscribe(self, topic: str, qos: int = 0) -> bool:
        subscriptions: List[Subscription] = self._mqtt_client.subscriptions
        if not topic in [sub.topic for sub in subscriptions]:
            rc = self._mqtt_client.subscribe(topic, qos=qos)

        return True

    def _unsubscribe(self, topic: str) -> bool:
        subscriptions: List[Subscription] = self._mqtt_client.subscriptions
        if topic in [sub.topic for sub in subscriptions]:
            rc = self._mqtt_client.unsubscribe(topic)
            MXLOG_DEBUG(f'{PrintTag.UNSUBSCRIBE} {topic}')

        return True

    def _resubscribe_all(self) -> bool:
        subscriptions: List[Subscription] = self._mqtt_client.subscriptions
        for subscription in subscriptions:
            self._mqtt_client.resubscribe(subscription)

        return True

    def _publish(self, topic: Union[str, bytes], payload: Union[str, bytes], qos: int = 0) -> int:
        self._print_packet(topic=topic, payload=payload, direction=Direction.PUBLISH, mode=self._log_mode)

        if isinstance(topic, str):
            topic = topic.encode()
        if isinstance(payload, str):
            payload = payload.encode()

        self._mqtt_client.publish(topic, payload, qos=qos)

    def _load_kvs(self):
        kvs_file_path = f'{os.path.join(self._kvs_storage_path, self.name)}.db'
        os.makedirs(os.path.dirname(kvs_file_path), exist_ok=True)
        self._kv_controller = KVStoreController(kvs_file_path)
        if self._reset_kvs:
            MXLOG_INFO(f'Reset KVS Storage: {self._kv_controller.db_path}')
            self._kv_controller.reset_db()

        if self._kv_controller.exists(KVS_KEY_MIDDLEWARE_NAME):
            MXLOG_INFO(f'Load KVS Storage: {self._kv_controller.db_path}')
            load_thing_info = self._kv_controller.get_many(
                [
                    KVS_KEY_NAME,
                    KVS_KEY_NICK_NAME,
                    KVS_KEY_CATEGORY,
                    KVS_KEY_DESC,
                    KVS_KEY_VERSION,
                    KVS_KEY_ALIVE_CYCLE,
                    KVS_KEY_MIDDLEWARE_NAME,
                    KVS_KEY_LAST_ALIVE_TIME,
                    KVS_KEY_SSID,
                    # KVS_KEY_PW,
                    KVS_KEY_HOST,
                    KVS_KEY_PORT,
                    KVS_KEY_SSL_CA_PATH,
                    KVS_KEY_SSL_CERT_PATH,
                    KVS_KEY_SSL_KEY_PATH,
                ]
            )

            self.name = load_thing_info.get(KVS_KEY_NAME, '')
            self.nick_name = load_thing_info.get(KVS_KEY_NICK_NAME, '')
            self.category = ALL_DEVICE_TYPES.get(load_thing_info.get(KVS_KEY_CATEGORY, ''), '')
            self.desc = load_thing_info.get(KVS_KEY_DESC, '')
            self.version = load_thing_info.get(KVS_KEY_VERSION, '')
            self.alive_cycle = load_thing_info.get(KVS_KEY_ALIVE_CYCLE, 0)
            self.middleware_name = load_thing_info.get(KVS_KEY_MIDDLEWARE_NAME, '')
            self.last_alive_time = load_thing_info.get(KVS_KEY_LAST_ALIVE_TIME, 0)

            self._ssid = load_thing_info.get(KVS_KEY_SSID, '')
            self._host = load_thing_info.get(KVS_KEY_HOST, '8883')
            self._port = load_thing_info.get(KVS_KEY_PORT, '127.0.0.1')
            self._ssl_ca_path = load_thing_info.get(KVS_KEY_SSL_CA_PATH, '')
            self._ssl_cert_path = load_thing_info.get(KVS_KEY_SSL_CERT_PATH, '')
            self._ssl_key_path = load_thing_info.get(KVS_KEY_SSL_KEY_PATH, '')
        else:
            # Store Thing data to KVStore
            MXLOG_INFO(f'Init KVS Storage: {self._kv_controller.db_path}')
            self._kv_controller.set_many(
                {
                    KVS_KEY_NAME: self.name,
                    KVS_KEY_NICK_NAME: self.nick_name,
                    KVS_KEY_CATEGORY: self.category.name,
                    KVS_KEY_DESC: self.desc,
                    KVS_KEY_VERSION: self.version,
                    KVS_KEY_ALIVE_CYCLE: self.alive_cycle,
                    # KVS_KEY_MIDDLEWARE_NAME: self.middleware_name,
                    # KVS_KEY_LAST_ALIVE_TIME: self.last_alive_time,
                    # KVS_KEY_SSID: self._ssid,
                    # KVS_KEY_HOST: self._host,
                    # KVS_KEY_PORT: self._port,
                    KVS_KEY_SSL_CA_PATH: self._ssl_ca_path,
                    KVS_KEY_SSL_CERT_PATH: self._ssl_cert_path,
                    KVS_KEY_SSL_KEY_PATH: self._ssl_key_path,
                }
            )
            self._kv_controller.save_to_disk()

    def _init_logger(self):
        log_file_path = f'{os.path.join(self._log_path, self.name)}.log'
        if self._log_enable:
            MXLogger(
                log_file_path=log_file_path,
                logger_type=LoggerType.ALL,
                logging_mode=LogLevel.DEBUG,
                async_mode=self._async_log,
            ).start()
        else:
            MXLogger(
                log_file_path=log_file_path,
                logger_type=LoggerType.OFF,
                logging_mode=LogLevel.DEBUG,
                async_mode=self._async_log,
            ).start()

    def _check_ssl_enable(self) -> bool:
        ssl_ca_exist = False
        if not self._ssl_ca_path and not self._ssl_cert_path and not self._ssl_key_path:
            ssl_ca_exist = False
        else:
            if not os.path.exists(self._ssl_ca_path):
                raise MXNotFoundError(f'SSL CA file not found. invalid path: {self._ssl_ca_path}')
            elif not os.path.exists(self._ssl_cert_path):
                raise MXNotFoundError(f'SSL Cert file not found. invalid path: {self._ssl_cert_path}')
            elif not os.path.exists(self._ssl_key_path):
                raise MXNotFoundError(f'SSL Key file not found.. invalid path: {self._ssl_key_path}')
            else:
                ssl_ca_exist = True

        if self._ssl_enable == False:
            return False
        if not ssl_ca_exist:
            return False

        return True

    def _register_mdns_service(self) -> bool:
        mDNS_service_name = '_joi-thing'
        ssl_mDNS_service_name = '_joi-thing-ssl'
        self._mqtt_mdns_service = ServiceInfo(
            type_=f'{mDNS_service_name}._tcp.local.',
            name=f'{mDNS_service_name}-{self.name}.{mDNS_service_name}._tcp.local.',
            addresses=[socket.inet_aton(get_local_ip())],
            port=1883,
            properties={'info': 'MySSIX Thing for Non-SSL', 'thing_id': f'{self.name}'},
        )
        self._mqtt_ssl_mdns_service = ServiceInfo(
            type_=f'{ssl_mDNS_service_name}._tcp.local.',
            name=f'{ssl_mDNS_service_name}-{self.name}.{ssl_mDNS_service_name}._tcp.local.',
            addresses=[socket.inet_aton(get_local_ip())],
            port=8883,
            properties={'info': 'MySSIX Thing for SSL', 'thing_id': f'{self.name}'},
        )

        try:
            self._zeroconf.register_service(self._mqtt_mdns_service)
            self._zeroconf.register_service(self._mqtt_ssl_mdns_service)
            return True
        except zeroconf.NonUniqueNameException as e:
            return True
        except Exception as e:
            print_error(e)
            return False

    def _unregister_mdns_service(self) -> None:
        if self._mqtt_mdns_service:
            self._zeroconf.unregister_service(self._mqtt_mdns_service)
        if self._mqtt_ssl_mdns_service:
            self._zeroconf.unregister_service(self._mqtt_ssl_mdns_service)

    # ===================================================================================
    # ___  ___ _____  _____  _____   _____         _  _  _                   _
    # |  \/  ||  _  ||_   _||_   _| /  __ \       | || || |                 | |
    # | .  . || | | |  | |    | |   | /  \/  __ _ | || || |__    __ _   ___ | | __ ___
    # | |\/| || | | |  | |    | |   | |     / _` || || || '_ \  / _` | / __|| |/ // __|
    # | |  | |\ \/' /  | |    | |   | \__/\| (_| || || || |_) || (_| || (__ |   < \__ \
    # \_|  |_/ \_/\_\  \_/    \_/    \____/ \__,_||_||_||_.__/  \__,_| \___||_|\_\|___/
    # ===================================================================================

    def _on_connect(self, client: MQTTClient, flags, rc, properties):
        if rc == 0:
            self._resubscribe_all()
            if self._state == ThingState.BROKER_LOST:
                self.next_state = ThingState.BROKER_RECONNECTED

            MXLOG_DEBUG(f'{PrintTag.CONNECT} Connect to Host: {self._host}:{self._port}')
        else:
            MXLOG_DEBUG(f'{PrintTag.ERROR} Bad connection... Returned code: {rc}', 'red')

    def _on_disconnect(self, client: MQTTClient, packet, exc=None):
        if self._state != ThingState.SHUTDOWN and (self._wait_request_register_task != None and self._wait_request_register_task.done()):
            self.next_state = ThingState.BROKER_LOST
        MXLOG_DEBUG(f'{PrintTag.DISCONNECT} Disconnect from broker {self._host}:{self._port}')

    def _on_subscribe(self, client: MQTTClient, mid: int, qos, properties):
        subscriptions: List[Subscription] = self._mqtt_client.get_subscriptions_by_mid(mid)
        for sub in subscriptions:
            MXLOG_DEBUG(f'{PrintTag.SUBSCRIBE} {sub.topic}')

    def _on_unsubscribe(self, client: MQTTClient, mid: int, qos):
        subscriptions: List[Subscription] = self._mqtt_client.get_subscriptions_by_mid(mid)
        for sub in subscriptions:
            MXLOG_DEBUG(f'{PrintTag.UNSUBSCRIBE} {sub.topic}')

    # def _on_publish(self, client: MQTTClient, userdata: MQTTMessage, mid):
    #     pass

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
            MXProtocolType.Base.MT_EXECUTE,
            MXProtocolType.Base.MT_IN_EXECUTE,
            MXProtocolType.WebClient.ME_RESULT_HOME,
        ]:
            await self._receive_queue[protocol].put(msg)
        else:
            MXLOG_CRITICAL(f'[{get_current_function_name()}] Unexpected topic! topic: {topic}')

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
    def function_list(self) -> List[MXFunction]:
        return sorted(
            [service for service in self._thing_data.service_list if isinstance(service, MXFunction) and not service.name.startswith('__')],
            key=lambda x: x.name,
        )

    @property
    def value_list(self) -> List[MXValue]:
        return sorted([service for service in self._thing_data.service_list if isinstance(service, MXValue)], key=lambda x: x.name)

    @property
    def service_list(self) -> List[MXService]:
        return sorted(self._thing_data.service_list, key=lambda x: x.name)

    @property
    def name(self) -> str:
        return self._thing_data.name

    @property
    def nick_name(self) -> str:
        return self._thing_data.nick_name

    @property
    def desc(self) -> str:
        return self._thing_data.desc

    @property
    def version(self) -> str:
        return self._thing_data.version

    @property
    def category(self) -> str:
        return self._thing_data.category

    @property
    def device_type(self) -> str:
        return self._thing_data.device_type

    @property
    def middleware_name(self) -> str:
        return self._thing_data.middleware_name

    @property
    def last_alive_time(self) -> float:
        return self._thing_data.last_alive_time

    @property
    def alive_cycle(self) -> float:
        return self._thing_data.alive_cycle

    @property
    def subscribed_topic_set(self) -> Set[str]:
        return self._thing_data.subscribed_topic_set

    @property
    def is_super(self) -> bool:
        return self._thing_data.is_super

    @property
    def is_parallel(self) -> bool:
        return self._thing_data.is_parallel

    @property
    def is_ble_wifi(self) -> bool:
        return self._thing_data.is_ble_wifi

    @property
    def is_builtin(self) -> bool:
        return self._thing_data.is_builtin

    @property
    def is_manager(self) -> bool:
        return self._thing_data.is_manager

    @property
    def is_staff(self) -> bool:
        return self._thing_data.is_staff

    @property
    def is_matter(self) -> bool:
        return self._thing_data.is_matter

    @property
    def current_state(self):
        return self._state

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @name.setter
    def name(self, name: str) -> None:
        self._thing_data.name = name
        for service in self._thing_data.service_list:
            service.thing_name = name

    @nick_name.setter
    def nick_name(self, nick_name: str) -> None:
        self._thing_data.nick_name = nick_name

    @desc.setter
    def desc(self, desc: str) -> None:
        self._thing_data.desc = desc

    @version.setter
    def version(self, version: str) -> None:
        self._thing_data.version = version

    @category.setter
    def category(self, category: DeviceCategory) -> None:
        self._thing_data.category = category

    @device_type.setter
    def device_type(self, device_type: str) -> None:
        self._thing_data.device_type = device_type

    @middleware_name.setter
    def middleware_name(self, middleware_name: str) -> None:
        self._thing_data.middleware_name = middleware_name
        for service in self._thing_data.service_list:
            service.middleware_name = middleware_name

    @last_alive_time.setter
    def last_alive_time(self, last_alive_time: float) -> None:
        self._thing_data.last_alive_time = last_alive_time

    @alive_cycle.setter
    def alive_cycle(self, alive_cycle: int) -> None:
        self._thing_data.alive_cycle = alive_cycle

    @subscribed_topic_set.setter
    def subscribed_topic_set(self, subscribed_topic_set: Set[str]) -> None:
        self._thing_data.subscribed_topic_set = subscribed_topic_set

    @is_super.setter
    def is_super(self, is_super: bool) -> bool:
        self._thing_data.is_super = is_super

    @is_parallel.setter
    def is_parallel(self, is_parallel: bool) -> bool:
        self._thing_data.is_parallel = is_parallel

    @is_ble_wifi.setter
    def is_ble_wifi(self, is_ble_wifi: bool) -> bool:
        self._thing_data.is_ble_wifi = is_ble_wifi

    @is_builtin.setter
    def is_builtin(self, is_builtin: bool) -> bool:
        self._thing_data.is_builtin = is_builtin

    @is_manager.setter
    def is_manager(self, is_manager: bool) -> bool:
        self._thing_data.is_manager = is_manager

    @is_staff.setter
    def is_staff(self, is_staff: bool) -> bool:
        self._thing_data.is_staff = is_staff

    @is_matter.setter
    def is_matter(self, is_matter: bool) -> bool:
        self._thing_data.is_matter = is_matter

    @current_state.setter
    def next_state(self, state: ThingState):
        self._state = state
        MXLOG_DEBUG(f'Current state: {self._state}', 'cyan')
