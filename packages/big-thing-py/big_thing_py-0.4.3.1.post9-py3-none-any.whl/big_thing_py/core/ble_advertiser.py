import asyncio
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

from big_thing_py.utils import *


class BLEErrorCode(Enum):
    NO_ERROR = 0
    FAIL = -1
    WIFI_PASSWORD_ERROR = -2
    WIFI_CONNECT_TIMEOUT = -3
    ALREADY_CONNECTED = -4
    WIFI_NOT_FOUND = -5
    WIFI_CREDENTIAL_NOT_SET = -6
    BROKER_NOT_SET = -7


class Characteristic:
    def __init__(self, uuid: str, properties: GATTCharacteristicProperties, permissions: GATTAttributePermissions, value: bytearray = None):
        self.uuid = uuid
        self.properties = properties
        self.permissions = permissions
        self.value = value


class Service:
    def __init__(self, uuid: str, characteristics: List[Characteristic]):
        self.uuid = uuid
        self.characteristics = characteristics


class DeviceWifiService(Service):
    UUID = '640F0000-0000-0000-0000-000000000000'

    class SetWifiSSIDCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0001-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.write,
                permissions=GATTAttributePermissions.writeable,
            )

    class SetWifiPWCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0002-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.write,
                permissions=GATTAttributePermissions.writeable,
            )

    class SetBrokerInfoCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0003-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.write,
                permissions=GATTAttributePermissions.writeable,
            )

    class ConnectWifiCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0004-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.write,
                permissions=GATTAttributePermissions.writeable,
            )

    class ThingIDCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0005-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.read,
                permissions=GATTAttributePermissions.readable,
            )

    class ErrorCodeCharacteristic(Characteristic):
        def __init__(self):
            super().__init__(
                uuid='640F0006-0000-0000-0000-000000000000',
                properties=GATTCharacteristicProperties.read,
                permissions=GATTAttributePermissions.readable,
            )

    def __init__(self):
        characteristics = [
            self.SetWifiSSIDCharacteristic(),
            self.SetWifiPWCharacteristic(),
            self.SetBrokerInfoCharacteristic(),
            self.ConnectWifiCharacteristic(),
            # self.ThingIDCharacteristic(), # this characteristic should be added, after thing id is set
            self.ErrorCodeCharacteristic(),
        ]
        super().__init__(DeviceWifiService.UUID, characteristics)


class BLEAdvertiser:
    def __init__(self, server_name: str) -> None:
        self._server_name = server_name
        self._server: BlessServer = None
        self._trigger = asyncio.Event()
        self._is_initialized = False

    def _read_request(self, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
        MXLOG_DEBUG(f'Reading {characteristic.uuid} {characteristic.value}')
        return characteristic.value

    def _write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
        try:
            characteristic.value = value
            uuid = characteristic.uuid.upper()
            if uuid == DeviceWifiService.SetWifiSSIDCharacteristic().uuid:
                MXLOG_DEBUG(f'WiFi SSID set: {self._server.get_characteristic(DeviceWifiService.SetWifiSSIDCharacteristic().uuid).value}')
            elif uuid == DeviceWifiService.SetWifiPWCharacteristic().uuid:
                MXLOG_DEBUG(f'WiFi PW set: {self._server.get_characteristic(DeviceWifiService.SetWifiPWCharacteristic().uuid).value}')
            elif uuid == DeviceWifiService.SetBrokerInfoCharacteristic().uuid:
                MXLOG_DEBUG(f'Broker Info set: {self._server.get_characteristic(DeviceWifiService.SetBrokerInfoCharacteristic().uuid).value}')
            elif uuid == DeviceWifiService.ConnectWifiCharacteristic().uuid:
                ssid = self._server.get_characteristic(DeviceWifiService.SetWifiSSIDCharacteristic().uuid).value
                pw = self._server.get_characteristic(DeviceWifiService.SetWifiPWCharacteristic().uuid).value
                broker = self._server.get_characteristic(DeviceWifiService.SetBrokerInfoCharacteristic().uuid).value
                if ssid is None or pw is None:
                    MXLOG_DEBUG(f'WiFi credentials not set... ssid: {ssid}, pw: {pw}')
                    self._server.update_value(
                        DeviceWifiService.ErrorCodeCharacteristic().uuid, BLEErrorCode.WIFI_CREDENTIAL_NOT_SET.value.to_bytes(2, 'little')
                    )
                    return
                elif broker is None:
                    MXLOG_DEBUG(f'Broker info not set... broker: {broker}')
                    self._server.update_value(
                        DeviceWifiService.ErrorCodeCharacteristic().uuid, BLEErrorCode.BROKER_NOT_SET.value.to_bytes(2, 'little')
                    )
                    return
                else:
                    MXLOG_DEBUG('wifi credentials & broker info is set!', 'green')
                    self._trigger.set()
        except Exception as e:
            MXLOG_DEBUG(f'Error occurred while writing characteristic: {e}', 'red')
            self._server.update_value(DeviceWifiService.ErrorCodeCharacteristic().uuid, BLEErrorCode.FAIL.value.to_bytes(2, 'little'))

    async def _add_service(self, service: Service):
        await self._server.add_new_service(service.uuid)
        for char in service.characteristics:
            await self._server.add_new_characteristic(service.uuid, char.uuid, char.properties, char.value, char.permissions)

    async def _add_thing_id_characteristic(self, thing_id: str):
        await self._server.add_new_characteristic(
            service_uuid=DeviceWifiService.UUID,
            char_uuid=DeviceWifiService.ThingIDCharacteristic().uuid,
            properties=GATTCharacteristicProperties.read,
            value=bytearray(thing_id.encode()),
            permissions=GATTAttributePermissions.readable,
        )

    async def init(self, thing_id: str):
        self._server = BlessServer(name=self._server_name)
        self._server.read_request_func = self._read_request
        self._server.write_request_func = self._write_request

        await self._add_service(DeviceWifiService())
        await self._add_thing_id_characteristic(thing_id)
        self._is_initialized = True
        MXLOG_DEBUG('BLE Advertiser initialized...')

    async def start(self):
        MXLOG_DEBUG('Starting BLE advertiser...')
        self._trigger.clear()

        await self._server.start()
        MXLOG_DEBUG(f'BLE Advertising started with name {self._server_name}...')

    async def stop(self):
        try:
            await self._server.stop()
        except Exception as e:
            pass
        MXLOG_DEBUG('BLE Advertising stopped...')

    async def is_connected(self):
        return await self._server.is_connected()

    async def is_advertising(self) -> bool:
        if self._server is None:
            return False

        return await self._server.is_advertising()

    def read_characteristic(self, uuid: str) -> bytearray:
        char = self._server.get_characteristic(uuid)
        return char.value

    def write_characteristic(self, uuid: str, value: bytearray) -> None:
        char = self._server.get_characteristic(uuid)
        char.value = value

    async def wait_until_wifi_credentials_set(self, timeout: float = 30) -> Tuple[str, str, str, BLEErrorCode]:

        async def wrapper() -> Tuple[str, str, str, BLEErrorCode]:
            await self._trigger.wait()
            ssid = self._server.get_characteristic(DeviceWifiService.SetWifiSSIDCharacteristic().uuid).value.decode()
            pw = self._server.get_characteristic(DeviceWifiService.SetWifiPWCharacteristic().uuid).value.decode()
            broker = self._server.get_characteristic(DeviceWifiService.SetBrokerInfoCharacteristic().uuid).value.decode()
            # error_code = BLEErrorCode(
            #     int.from_bytes(self._server.get_characteristic(DeviceWifiService.ErrorCodeCharacteristic().uuid).value, 'little')
            # )
            error_code = BLEErrorCode.NO_ERROR
            return (ssid, pw, broker, error_code)

        try:
            ssid, pw, broker, error_code = await asyncio.wait_for(wrapper(), timeout)
            return (ssid, pw, broker, error_code)
        except asyncio.TimeoutError:
            return ('', '', '', BLEErrorCode.WIFI_CONNECT_TIMEOUT)

    @property
    def is_initialized(self):
        return self._is_initialized


if __name__ == '__main__':
    MXLogger(logger_type=LoggerType.ALL, logging_mode=LogLevel.DEBUG).start()

    async def run():
        ble_advertiser = BLEAdvertiser(server_name=f'JOI SD {get_mac_address()[6:]}')
        await ble_advertiser.start()
        ssid, pw, broker, error_code = await ble_advertiser.wait_until_wifi_credentials_set()
        MXLOG_DEBUG(f'WiFi credentials set: ssid: {ssid}, pw: {pw}, broker: {broker}, error_code: {error_code}')
        await ble_advertiser.stop()

    async def test_smart_device(server_name: str = f'JOI SD {get_mac_address()[6:]}'):
        '''
        NOTE: this test function should be run on a separate device
        '''
        from bleak import BleakClient, BleakScanner

        device_address = None

        devices = await BleakScanner.discover()
        for device in devices:
            if device.name == server_name:
                print(f'Found BLE server! name: {device.name}, address: {device.address}')
                device_address = device.address
                break
        else:
            print(f"Cannot find {server_name}")
            return

        ssid_characteristic_uuid = DeviceWifiService.SetWifiSSIDCharacteristic().uuid
        pw_characteristic_uuid = DeviceWifiService.SetWifiPWCharacteristic().uuid
        broker_characteristic_uuid = DeviceWifiService.SetBrokerInfoCharacteristic().uuid
        connect_wifi_characteristic_uuid = DeviceWifiService.ConnectWifiCharacteristic().uuid

        ssid_value = b"SSID"
        pw_value = b"PASSWORD"
        broker_value = b"localhost:8883"

        async with BleakClient(device_address) as client:
            if client.is_connected:
                print(f"Connected to {device_address}")

                await client.write_gatt_char(ssid_characteristic_uuid, ssid_value)
                print("WiFi SSID set")

                await client.write_gatt_char(pw_characteristic_uuid, pw_value)
                print("WiFi password set")

                await client.write_gatt_char(broker_characteristic_uuid, broker_value)
                print("Broker info set")

                await client.write_gatt_char(connect_wifi_characteristic_uuid, bytearray([0x00]))
                print("WiFi connection attempt")

    asyncio.run(test_smart_device())
