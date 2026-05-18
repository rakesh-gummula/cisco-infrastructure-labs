# NetVigil-C 🕵️‍♂️ 

![C](https://img.shields.io/badge/Language-C-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**NetVigil-C** is a high-performance, raw-socket network packet sniffer and protocol analyzer written entirely in C. Developed to bridge the gap between network engineering (CCNA) and low-level Linux systems programming, this tool captures traffic directly at Layer 2 (Data Link) and decapsulates network frames up to Layer 4 (Transport).

## 🚀 Key Features

* **Layer 2 Raw Socket Capture:** Bypasses standard OS network stacks using `AF_PACKET` to capture native Ethernet frames before the kernel processes them.
* **Deep Packet Inspection:** Manually decapsulates and parses `Ethernet`, `IPv4`, `TCP`, `UDP`, and `ICMP` headers using C data structures.
* **PCAP Export:** Writes raw captured bytes to a standard `.pcap` file format with global and packet-level headers, allowing seamless integration with **Wireshark**.
* **Interface Binding:** Allows targeting specific Network Interface Cards (NICs) or listening globally.
* **Zero External Dependencies:** Built entirely using standard POSIX and Linux kernel networking libraries (`<sys/socket.h>`, `<netinet/ip.h>`, etc.).

## 🧠 Architecture Concept

Standard applications interact with the network at Layer 7, relying on the OS to handle TCP/IP encapsulation.
NetVigil-C hooks directly into the **Data Link Layer**. 

When a frame hits the NIC, NetVigil reads the raw bytes.
It then mathematically maps C-structs over memory buffers to identify the boundaries of MAC addresses, IP addresses, and Port numbers without altering the underlying payload.

## 🛠️ Installation & Compilation

Since this tool utilizes raw sockets, it must be compiled and executed on a Linux environment.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rakesh-gummula/netvigil-c.git](https://github.com/rakesh-gummula/netvigil-c.git)
   cd NetVigil-C

2. Verbose Mode (Live terminal dissection of layers)

Bash
sudo ./netvigil -v
3. Bind to a Specific Interface (e.g., eth0 or wlan0)

Bash
sudo ./netvigil -i eth0 -v
4. Export to Wireshark (Save capture to a .pcap file)

Bash
sudo ./netvigil -w capture.pcap
(You can then open capture.pcap directly in Wireshark for deep graphical analysis).

⚠️ Disclaimer
This tool was created strictly for educational purposes, network diagnostics, and demonstrating proficiency in network protocol structures (CCNA concepts).
Ensure you have explicit permission to monitor traffic on any network where you run this software.
