from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any


def print_report(report: Any) -> None:
    """
    Print a readable scan report.

    Expects an object with:
    - subnet
    - discovered_hosts
    - hosts
    - duration_seconds
    """
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


def export_json(report: Any, path: str | Path) -> None:
    """Export the report to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

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

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_csv(report: Any, path: str | Path) -> None:
    """Export the report to a CSV file."""
    path = Path(path)
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
