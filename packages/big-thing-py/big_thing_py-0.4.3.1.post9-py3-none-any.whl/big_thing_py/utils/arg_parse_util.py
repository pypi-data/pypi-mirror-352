from big_thing_py.core.device_model import MXDeviceCategory
from big_thing_py.core.device_model import Objects as DeviceCategory
from big_thing_py.utils import MXPrintMode
import argparse
from enum import Enum


def arg_parse_big_thing(device_category: MXDeviceCategory):
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', '-lang', action='store', type=str, required=False, default='ko', help='language')
    args, unknown = parser.parse_known_args()

    # default_nick_name = translate(DEVICE_CATEGORY.name, args.language)
    default_nick_name = device_category.name

    parser.add_argument('--name', '-n', action='store', type=str, required=False, default=device_category.name, help='thing name')
    parser.add_argument('--nick-name', '-N', action='store', type=str, required=False, default=default_nick_name, help='thing nick name')
    parser.add_argument('--host', '-H', action='store', type=str, required=False, default='127.0.0.1', help='host name')
    parser.add_argument('--port', '-p', action='store', type=int, required=False, default=1883, help='port')
    parser.add_argument('--alive-cycle', '-ac', action='store', type=int, required=False, default=60, help='alive cycle')
    parser.add_argument('--ca-path', '-ca', action='store', required=False, help='CA path')
    parser.add_argument('--cert-path', '-cert', action='store', required=False, help='cert path')
    parser.add_argument('--key-path', '-key', action='store', required=False, help='key path')

    parser.add_argument('--log', action='store_true', required=False, help='log enable')
    parser.add_argument('--log-mode', action='store', type=str, required=False, default=MXPrintMode.ABBR.value, help='log mode')
    parser.add_argument('--log-path', action='store', type=str, required=False, default='/tmp/joi_thing/', help='log path')
    parser.add_argument('--async-log', action='store_true', required=False, default=False, help='')
    parser.add_argument('--append-mac', '-am', action='store_false', required=False, help='append mac address to thing name')
    parser.add_argument('--ble-wifi', '-bw', action='store_true', required=False, help='run thing with ble-wifi mode')
    parser.add_argument('--builtin', '-btin', action='store_true', required=False, help='run thing with built-in mode')
    parser.add_argument('--no-wait-request-register', '-no-wait', action='store_true', required=False, help='run thing with no wait request register')
    parser.add_argument(
        '--kvs-storage-path', '-KVS', action='store', type=str, default='/tmp/joi_thing/', required=False, help='KV store storage path'
    )
    parser.add_argument('--reset-kvs', '-rst', action='store_true', required=False, help='Reset KV store storage')
    args, unknown = parser.parse_known_args()

    return args


def arg_parse_manager_thing(manager_name: str = None):
    device_category = DeviceCategory.ManagerThing

    parser = argparse.ArgumentParser()
    parser.add_argument("--language", '-lang', action='store', type=str, required=False, default='ko', help="language")
    args, unknown = parser.parse_known_args()

    # default_nick_name = translate(DEVICE_CATEGORY.name, args.language)
    default_nick_name = device_category.name

    parser.add_argument(
        "--name", '-n', action='store', type=str, required=False, default=manager_name if manager_name else device_category.name, help="thing name"
    )
    parser.add_argument("--nick-name", '-N', action='store', type=str, required=False, default=default_nick_name, help="thing nick name")
    parser.add_argument("--host", '-H', action='store', type=str, required=False, default='127.0.0.1', help="host name")
    parser.add_argument("--port", '-p', action='store', type=int, required=False, default=1883, help="port")
    parser.add_argument("--alive-cycle", '-ac', action='store', type=int, required=False, default=60, help="alive cycle")
    parser.add_argument("--ca-path", '-ca', action='store', required=False, help="CA path")
    parser.add_argument("--cert-path", '-cert', action='store', required=False, help="cert path")
    parser.add_argument("--key-path", '-key', action='store', required=False, help="key path")

    parser.add_argument("--log", action='store_true', required=False, help="log enable")
    parser.add_argument("--log-mode", action='store', type=str, required=False, default=MXPrintMode.ABBR.value, help="log mode")
    parser.add_argument('--log-path', action='store', type=str, required=False, default='/tmp/joi_thing/', help='log path')
    parser.add_argument("--async-log", action='store_true', required=False, default=False, help="")
    parser.add_argument("--append-mac", '-am', action='store_false', required=False, help="append mac address to thing name")
    parser.add_argument("--ble-wifi", '-bw', action='store_true', required=False, help="run thing with ble-wifi mode")
    parser.add_argument("--builtin", '-btin', action='store_true', required=False, help="run thing with built-in mode")
    parser.add_argument('--no-wait-request-register', '-no-wait', action='store_true', required=False, help='run thing with no wait request register')
    parser.add_argument("--config", '-c', action='store', type=str, required=False, default='config.json', help="config file path")
    parser.add_argument("--config-select", '-s', action='store', type=str, required=False, default='', help="config select")
    parser.add_argument(
        '--kvs-storage-path', '-KVS', action='store', type=str, default='/tmp/joi_thing/', required=False, help='KV store storage path'
    )
    parser.add_argument('--reset-kvs', '-rst', action='store_true', required=False, help='Reset KV store storage')
    args, unknown = parser.parse_known_args()

    return args


def arg_parse_super_thing(device_category: MXDeviceCategory):
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", '-lang', action='store', type=str, required=False, default='ko', help="language")
    args, unknown = parser.parse_known_args()

    # default_nick_name = translate(DEVICE_CATEGORY.name, args.language)
    default_nick_name = device_category.name

    parser.add_argument("--name", '-n', action='store', type=str, required=False, default=device_category.name, help="thing name")
    parser.add_argument("--nick-name", '-N', action='store', type=str, required=False, default=default_nick_name, help="thing nick name")
    parser.add_argument("--host", '-H', action='store', type=str, required=False, default='127.0.0.1', help="host name")
    parser.add_argument("--port", '-p', action='store', type=int, required=False, default=1883, help="port")
    parser.add_argument("--alive-cycle", '-ac', action='store', type=int, required=False, default=60, help="alive cycle")
    parser.add_argument("--refresh-cycle", '-rc', action='store', type=int, required=False, default=60, help="refresh cycle")
    parser.add_argument("--ca-path", '-ca', action='store', required=False, help="CA path")
    parser.add_argument("--cert-path", '-cert', action='store', required=False, help="cert path")
    parser.add_argument("--key-path", '-key', action='store', required=False, help="key path")

    parser.add_argument("--log", action='store_true', required=False, help="log enable")
    parser.add_argument("--log-mode", action='store', type=str, required=False, default=MXPrintMode.ABBR.value, help="log mode")
    parser.add_argument('--log-path', action='store', type=str, required=False, default='/tmp/joi_thing/', help='log path')
    parser.add_argument("--async-log", action='store_true', required=False, default=False, help="")
    parser.add_argument("--append-mac", '-am', action='store_false', required=False, help="append mac address to thing name")
    parser.add_argument("--ble-wifi", '-bw', action='store_true', required=False, help="run thing with ble-wifi mode")
    parser.add_argument("--builtin", '-btin', action='store_true', required=False, help="run thing with built-in mode")
    parser.add_argument('--no-wait-request-register', '-no-wait', action='store_true', required=False, help='run thing with no wait request register')
    parser.add_argument(
        '--kvs-storage-path', '-KVS', action='store', type=str, default='/tmp/joi_thing/', required=False, help='KV store storage path'
    )
    parser.add_argument('--reset-kvs', '-rst', action='store_true', required=False, help='Reset KV store storage')
    args, unknown = parser.parse_known_args()

    return args


def generate_big_thing_args(args: argparse.Namespace) -> dict:
    return dict(
        name=args.name,
        nick_name=args.nick_name,
        # category=device_category,
        ip=args.host,
        port=args.port,
        alive_cycle=args.alive_cycle,
        log_mode=MXPrintMode.get(args.log_mode),
        log_path=args.log_path,
        ssl_ca_path=args.ca_path,
        ssl_cert_path=args.cert_path,
        ssl_key_path=args.key_path,
        append_mac_address=args.append_mac,
        no_wait_request_register=args.no_wait_request_register,
        # service_list=service_list,
        is_ble_wifi=args.ble_wifi,
        is_builtin=args.builtin,
        is_parallel=True,
        kvs_storage_path=args.kvs_storage_path,
        reset_kvs=args.reset_kvs,
    )


def generate_super_thing_args(args: argparse.Namespace) -> dict:
    return dict(
        name=args.name,
        nick_name=args.nick_name,
        # category=device_category,
        ip=args.host,
        port=args.port,
        alive_cycle=args.alive_cycle,
        refresh_cycle=args.refresh_cycle,
        log_mode=MXPrintMode.get(args.log_mode),
        log_path=args.log_path,
        ssl_ca_path=args.ca_path,
        ssl_cert_path=args.cert_path,
        ssl_key_path=args.key_path,
        append_mac_address=args.append_mac,
        no_wait_request_register=args.no_wait_request_register,
        # service_list=service_list,
        is_ble_wifi=args.ble_wifi,
        is_builtin=args.builtin,
        is_parallel=True,
        kvs_storage_path=args.kvs_storage_path,
        reset_kvs=args.reset_kvs,
    )


def generate_manager_thing_args(args: argparse.Namespace) -> dict:
    return dict(
        name=args.name,
        nick_name=args.nick_name,
        ip=args.host,
        port=args.port,
        alive_cycle=args.alive_cycle,
        log_mode=MXPrintMode.get(args.log_mode),
        ssl_ca_path=args.ca_path,
        ssl_cert_path=args.cert_path,
        ssl_key_path=args.key_path,
        append_mac_address=args.append_mac,
        no_wait_request_register=args.no_wait_request_register,
        service_list=[],
        kvs_storage_path=args.kvs_storage_path,
        reset_kvs=args.reset_kvs,
        conf_file_path=args.config,
        conf_select=args.config_select,
    )
