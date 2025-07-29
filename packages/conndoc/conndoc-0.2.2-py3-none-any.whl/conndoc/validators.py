import ssl
import socket
import datetime
import subprocess
import httpx

from conndoc.utils import *

from conndoc.constants import (
    DEFAULT_TIMEOUT_SECOND
)

def validate_ping(host: str, timeout: float = DEFAULT_TIMEOUT_SECOND):
    cmd = build_ping_command(host, timeout)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

def validate_dns(host: str):
    if is_ip(host):
        return
    return socket.getaddrinfo(host, None)

def validate_ssl(host: str, port: int, timeout: float = DEFAULT_TIMEOUT_SECOND):
    if is_ip(host):
        raise ValueError("SSL check requires a domain name, not an IP address")

    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            return ssock.getpeercert()

def validate_http(host: str):
    url = host if host.startswith("http") else f"http://{host}"
    response = httpx.get(url, follow_redirects=True, timeout=DEFAULT_TIMEOUT_SECOND)
    if response.status_code >= 400:
        raise ValueError(f"HTTP status {response.status_code}")
    return response

def validate_tcp(host: str, port: int, timeout: float = DEFAULT_TIMEOUT_SECOND):
    socket.create_connection((host, port), timeout=timeout)