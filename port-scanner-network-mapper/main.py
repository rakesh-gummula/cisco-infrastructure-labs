#!/usr/bin/env python3
"""Port Scanner & Network Mapper

Use only on networks and hosts you are authorized to test.

This script performs:
- subnet host discovery via TCP connect probes
- TCP port scanning on live hosts
- simple service-name mapping for common ports
- optional JSON / CSV export

It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from ipaddress import ip_network
from pathlib import Path
from time import perf_counter
from typing import Iterable


SERVICE_MAP = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPCBIND",
    123: "NTP",
    135: "MSRPC",
    139: "NETBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    500: "ISAKMP",
    587: "SUBMISSION",
    636: "LDAPS",
    873: "RSYNC",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "ORACLE",
    2049: "NFS",
    2375: "DOCKER",
    3306: "MYSQL",
    3389: "RDP",
    5432: "POSTGRESQL",
    5900: "VNC",
    6379: "REDIS",
    8080: "HTTP-PROXY",
    8443: "HTTPS-ALT",
}


@dataclass
class PortResult:
    port: int
    service: str


@dataclass
class HostResult:
    host: str
    open_ports: list[PortResult]


@dataclass
class ScanReport:
    subnet: str
    discovered_hosts: list[str]
    hosts: list[HostResult]
    duration_seconds: float


def parse_ports(port_spec: str) -> list[int]:
    """Parse a comma-separated port list with optional ranges.

    Examples:
        "22,80,443"
        "20-25,80,443"
    """
    ports: set[int] = set()
    for item in (p.strip() for p in port_spec.split(",")):
        if not item:
            continue
        if "-" in item:
            start_s, end_s = (x.strip() for x in item.split("-", 1))
            start, end = int(start_s), int(end_s)
            if start < 1 or end > 65535 or start > end:
                raise ValueError(f"Invalid port range: {item}")
            ports.update(range(start, end + 1))
        else:
            port = int(item)
            if port < 1 or port > 65535:
                raise ValueError(f"Invalid port: {port}")
            ports.add(port)
    if not ports:
        raise ValueError("No valid ports were provided.")
    return sorted(ports)


def get_service_name(port: int) -> str:
    return SERVICE_MAP.get(port, "UNKNOWN")


def tcp_probe(ip: str, port: int, timeout: float) -> bool:
    """Return True if a TCP connection can be established."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def discover_hosts(subnet: str, probe_port: int, timeout: float, max_workers: int) -> list[str]:
    """Discover hosts by probing a known TCP port on each address in the subnet.

    Note: This is a practical, standard-library-only approach. It does not use ICMP.
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
                # Treat all connection/OS errors as a non-response.
                pass

    live_hosts.sort(key=lambda s: tuple(int(x) for x in s.split(".")) if "." in s else s)
    return live_hosts


def scan_host_ports(ip: str, ports: Iterable[int], timeout: float, max_workers: int) -> list[PortResult]:
    open_ports: list[PortResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(tcp_probe, ip, port, timeout): port for port in ports}
        for future in as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    open_ports.append(PortResult(port=port, service=get_service_name(port)))
            except OSError:
                pass

    open_ports.sort(key=lambda x: x.port)
    return open_ports


def build_report(subnet: str, ports: list[int], timeout: float, discovery_port: int, workers: int) -> ScanReport:
    start = perf_counter()
    discovered = discover_hosts(subnet, discovery_port, timeout, workers)

    host_results: list[HostResult] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(scan_host_ports, host, ports, timeout, workers): host
            for host in discovered
        }
        for future in as_completed(futures):
            host = futures[future]
            try:
                open_ports = future.result()
                host_results.append(HostResult(host=host, open_ports=open_ports))
            except OSError:
                host_results.append(HostResult(host=host, open_ports=[]))

    host_results.sort(key=lambda item: tuple(int(x) for x in item.host.split(".")))
    duration = perf_counter() - start
    return ScanReport(subnet=subnet, discovered_hosts=discovered, hosts=host_results, duration_seconds=duration)


def print_report(report: ScanReport) -> None:
    print(f"\nSubnet: {report.subnet}")
    print(f"Discovered hosts: {len(report.discovered_hosts)}")
    print(f"Scan duration: {report.duration_seconds:.2f} seconds\n")

    if not report.hosts:
        print("No live hosts found.")
        return

    for host in report.hosts:
        print(f"Host: {host.host}")
        if not host.open_ports:
            print("  Open ports: none found")
            continue
        print("  Open ports:")
        for port_result in host.open_ports:
            print(f"    - {port_result.port}/tcp  {port_result.service}")
        print()


def export_json(report: ScanReport, path: Path) -> None:
    data = {
        "subnet": report.subnet,
        "duration_seconds": round(report.duration_seconds, 3),
        "discovered_hosts": report.discovered_hosts,
        "hosts": [
            {
                "host": host.host,
                "open_ports": [asdict(port) for port in host.open_ports],
            }
            for host in report.hosts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_csv(report: ScanReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "service"])
        for host in report.hosts:
            if not host.open_ports:
                writer.writerow([host.host, "", ""])
                continue
            for port_result in host.open_ports:
                writer.writerow([host.host, port_result.port, port_result.service])


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be > 0")
    return parsed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Port Scanner & Network Mapper (authorized-use only)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--subnet", required=True, help="Target subnet, e.g. 192.168.1.0/24")
    parser.add_argument(
        "--ports",
        default="22,80,443,445,3389",
        help="Comma-separated ports and/or ranges, e.g. 22,80,443 or 20-25,80",
    )
    parser.add_argument(
        "--probe-port",
        type=positive_int,
        default=443,
        help="TCP port used for host discovery probes",
    )
    parser.add_argument("--timeout", type=positive_float, default=0.5, help="Socket timeout in seconds")
    parser.add_argument("--workers", type=positive_int, default=100, help="Maximum worker threads")
    parser.add_argument(
        "--output",
        default="",
        help="Optional output file path. If provided, use --format json or csv.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "csv"),
        default="json",
        help="Output format for --output",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        # Validate subnet early.
        _ = ip_network(args.subnet, strict=False)
        ports = parse_ports(args.ports)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    report = build_report(
        subnet=args.subnet,
        ports=ports,
        timeout=args.timeout,
        discovery_port=args.probe_port,
        workers=args.workers,
    )

    print_report(report)

    if args.output:
        output_path = Path(args.output)
        try:
            if args.format == "json":
                export_json(report, output_path)
            else:
                export_csv(report, output_path)
            print(f"Saved report to: {output_path}")
        except OSError as exc:
            print(f"Failed to write output file: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
