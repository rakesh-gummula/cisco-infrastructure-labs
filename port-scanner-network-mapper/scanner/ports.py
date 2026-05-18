from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from .services import get_service_name


def check_port(ip: str, port: int, timeout: float) -> bool:
    """Return True if the given TCP port is open."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def scan_host_ports(ip: str, ports: list[int], timeout: float = 0.5, max_workers: int = 100) -> list[dict]:
    """
    Scan a host for open TCP ports.

    Returns a list of dictionaries like:
    [
        {"port": 22, "service": "SSH"},
        {"port": 80, "service": "HTTP"},
    ]
    """
    open_ports: list[dict] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_port, ip, port, timeout): port for port in ports}
        for future in as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    open_ports.append(
                        {
                            "port": port,
                            "service": get_service_name(port),
                        }
                    )
            except OSError:
                pass

    open_ports.sort(key=lambda item: item["port"])
    return open_ports
