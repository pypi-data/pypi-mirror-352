from big_thing_py.utils import *
import subprocess
import socket
import time
import asyncio
from typing import List, Optional


def validate_ip(ip: str) -> bool:
    '''Validate IPv4 format (0-255.0-255.0-255.0-255).'''
    try:
        socket.inet_aton(ip)
        return True
    except OSError:
        return False


def parse_ip_from_ip_addr(raw: str) -> Optional[str]:
    """Extract one IPv4 from the result of `ip -4 -o addr show dev <iface>`."""
    m = re.search(r'\binet\s+(\d+\.\d+\.\d+\.\d+)/', raw)
    return m.group(1) if m else None


class EthernetManager:
    '''
    - Support for DHCP or Static IP configuration
    - Check link status, IP address, gateway, and DNS
    - Check network reachability with ping / TCP socket
    '''

    def __init__(
        self,
        interface: str | None = None,
        use_dhcp: bool = True,
        static_ip: str = '',
        gateway: str = '',
        dns: Optional[List[str]] = None,
    ):
        self._interface = interface
        self._use_dhcp = use_dhcp
        self._static_ip = static_ip
        self._gateway = gateway
        self._dns = dns or []

        def _exists(iface: str) -> bool:
            return iface and os.path.exists(f'/sys/class/net/{iface}')

        chosen_iface = interface if _exists(interface or '') else None

        # 2) If not found, automatically detect currently connected ethernet interface
        if chosen_iface is None:
            chosen_iface = self.get_current_ethernet()

        # 3) If still not found, raise error
        if not _exists(chosen_iface or ''):
            raise ValueError(f'Ethernet interface "{interface}" not found, ' 'and no connected Ethernet device could be detected.')

        self._interface = chosen_iface

    # ────────────────────── Basic Properties ──────────────────────
    @property
    def interface(self) -> str:
        return self._interface

    @interface.setter
    def interface(self, interface: str) -> None:
        self._interface = interface

    @property
    def use_dhcp(self) -> bool:
        return self._use_dhcp

    @use_dhcp.setter
    def use_dhcp(self, flag: bool) -> None:
        self._use_dhcp = flag

    # ────────────────────── Internal Utils ──────────────────────
    def _nmcli(self, *args: str) -> subprocess.CompletedProcess:
        '''nmcli wrapper (returns stdout string).'''
        cmd = ['nmcli', *args]
        return subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # ────────────────────── Status Queries ──────────────────────
    def get_current_ethernet(self) -> str | None:
        """
        First search for NIC with STATE=connected using nmcli -> if not found,
        search for NIC with operstate=up (ethernet type) -> if still not found, return None
        """
        # ① Find 'connected' NIC from nmcli output (DEVICE:TYPE:STATE)
        res = self._nmcli('-t', '-f', 'DEVICE,TYPE,STATE', 'device', 'status')
        stdout: str = res.stdout
        stderr: str = res.stderr
        
        if res.returncode == 0:
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                dev, dtype, state = line.split(':', 2)
                if dtype == 'ethernet' and state == 'connected':
                    return dev

            # ② Find 'unmanaged' NICs with physical link up
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                dev, dtype, _ = line.split(':', 2)
                if dtype != 'ethernet':
                    continue
                try:
                    with open(f'/sys/class/net/{dev}/operstate') as f:
                        if f.read().strip() == 'up':
                            return dev
                except FileNotFoundError:
                    pass

        # ③ Scan all NICs in sysfs (last safety net)
        for iface in os.listdir('/sys/class/net'):
            try:
                with open(f'/sys/class/net/{iface}/type') as f:
                    if f.read().strip() != '1':        # 1 == ARPHRD_ETHER
                        continue
                with open(f'/sys/class/net/{iface}/operstate') as f:
                    if f.read().strip() == 'up':
                        return iface
            except FileNotFoundError:
                pass

        MXLOG_DEBUG('No connected Ethernet interface found.')
        return None

    def link_up(self) -> bool:
        '''Check if interface physical link is up (cat /sys/class/net/{iface}/operstate).'''
        try:
            with open(f'/sys/class/net/{self._interface}/operstate') as f:
                return f.read().strip() == 'up'
        except FileNotFoundError:
            MXLOG_DEBUG(f'Interface {self._interface} not found.')
            return False

    def get_current_ip(self) -> Optional[str]:
        """
        ① Query IPv4 with nmcli -> if failed,
        ② Parse ip addr output -> if not found, return None
        """
        # ① Try nmcli (Managed environment)
        res = self._nmcli('-t', '-f', 'IP4.ADDRESS', 'device', 'show', self._interface)
        stdout: str = res.stdout
        stderr: str = res.stderr
        
        if res.returncode == 0:
            for line in stdout.splitlines():
                if line.startswith('IP4.ADDRESS'):
                    return line.split(':', 1)[1].split('/')[0]

        # ② unmanaged / Fallback: ip addr
        proc: subprocess.CompletedProcess = subprocess.run(
            ['ip', '-4', '-o', 'addr', 'show', 'dev', self._interface],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout: str = proc.stdout
        
        if proc.returncode == 0:
            ip = parse_ip_from_ip_addr(stdout)
            if ip:
                return ip

        MXLOG_DEBUG(f'Cannot get IP for {self._interface}: unmanaged or no address.')
        return None

    def is_connected(self) -> bool:
        '''Check if both link and IP are available.'''
        return self.link_up() and (self.get_current_ip() is not None)

    # ────────────────────── Connection / Configuration ──────────────────────
    async def set_dhcp(self) -> bool:
        '''
        Switch to DHCP mode and restart the interface.
        '''
        cmd = [
            'sudo',
            'nmcli',
            'connection',
            'modify',
            self._interface,
            'ipv4.method',
            'auto',
            'ipv6.method',
            'auto',
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, err = await proc.communicate()
        if proc.returncode != 0:
            MXLOG_DEBUG(f'Failed to set DHCP: {err.decode().strip()}')
            return False
        return await self._bring_up()

    async def set_static(self, ip: Optional[str] = None, gateway: Optional[str] = None, dns: Optional[List[str]] = None) -> bool:
        '''
        Configure Static IP and restart the interface.
        '''
        ip = ip or self._static_ip
        gateway = gateway or self._gateway
        dns = dns or self._dns

        if not (validate_ip(ip) and validate_ip(gateway)):
            MXLOG_DEBUG('Invalid IP or gateway.')
            return False

        dns_str = ','.join(dns) if dns else ''

        modify_cmd = [
            'sudo',
            'nmcli',
            'connection',
            'modify',
            self._interface,
            'ipv4.method',
            'manual',
            'ipv4.addresses',
            ip,
            'ipv4.gateway',
            gateway,
            'ipv4.dns',
            dns_str,
        ]
        proc = await asyncio.create_subprocess_exec(*modify_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, err = await proc.communicate()
        if proc.returncode != 0:
            MXLOG_DEBUG(f'Failed to set static IP: {err.decode().strip()}')
            return False

        return await self._bring_up()

    async def _bring_up(self) -> bool:
        '''Restart interface (down → up).'''
        down = await asyncio.create_subprocess_exec(
            'sudo', 'nmcli', 'device', 'disconnect', self._interface, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await down.communicate()
        up = await asyncio.create_subprocess_exec(
            'sudo', 'nmcli', 'device', 'connect', self._interface, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, err = await up.communicate()
        if up.returncode == 0:
            MXLOG_DEBUG(f'{self._interface} reconnected.')
            return True
        MXLOG_DEBUG(f'Failed to reconnect {self._interface}: {err.decode().strip()}')
        return False

    async def connect(self) -> bool:
        '''
        Connect interface according to the configured mode (DHCP/Static) and return the result.
        '''
        if self._use_dhcp:
            return await self.set_dhcp()
        else:
            return await self.set_static()

    # ────────────────────── Network Reachability Check ──────────────────────
    def network_reachable(self, host: str = '8.8.8.8', port: int = 53, retry: int = 3, delay: float = 0.5) -> bool:
        '''Check connectivity using TCP socket.'''
        attempt = 0
        while attempt < retry:
            try:
                socket.create_connection((host, port), timeout=1)
                return True
            except OSError:
                attempt += 1
                if attempt < retry:
                    time.sleep(delay)
        return False


# ────────────────────── Simple Example ──────────────────────
if __name__ == '__main__':
    import asyncio

    MXLogger(logger_type=LoggerType.ALL, logging_mode=LogLevel.DEBUG).start()

    async def main():
        # 1) DHCP
        eth = EthernetManager(interface='eth0', use_dhcp=True)
        if eth.is_connected():
            MXLOG_DEBUG(f'Link up? {eth.link_up()}, IP: {eth.get_current_ip()}')

        # 2) Static IP Example
        # eth_static = EthernetManager(
        #     interface='eth0',
        #     use_dhcp=False,
        #     static_ip='10.0.0.50/24',
        #     gateway='10.0.0.1',
        #     dns=['8.8.8.8', '1.1.1.1'],
        # )
        # await eth_static.connect()

    asyncio.run(main())
