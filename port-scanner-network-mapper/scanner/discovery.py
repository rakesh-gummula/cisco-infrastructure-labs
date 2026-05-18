from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_network


def tcp_probe(ip: str, port: int, timeout: float) -> bool:
    """Return True if a TCP connection can be established."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def discover_hosts(subnet: str, probe_port: int = 443, timeout: float = 0.5, max_workers: int = 100) -> list[str]:
    """
    Discover live hosts in a subnet by probing a TCP port on each address.

    This is a standard-library-only approach and does not use ICMP.
    """
    network = ip_network(subnet, strict=False)
    candidates = [str(ip) for ip in network.hosts()]

    if not candidates:
        return []

    live_hosts: list[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(tcp_probe, ip, probe_port, timeout): ip for ip in candidates}
        for future in as_completed(futures):
            ip = futures[future]
            try:
                if future.result():
                    live_hosts.append(ip)
            except OSError:
                pass

    live_hosts.sort(key=lambda s: tuple(int(x) for x in s.split(".")))
    return live_hosts
