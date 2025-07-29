import platform
import ipaddress

from conndoc.constants import (
    DEFAULT_TIMEOUT_SECOND
)

def is_ip(address: str) -> bool:
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

def build_ping_command(host: str, timeout: float = DEFAULT_TIMEOUT_SECOND) -> list[str]:
    system = platform.system()
    count = 3
    if system == "Windows":
        return ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
    else:
        return ["ping", "-c", str(count), "-W", str(int(timeout)), host]