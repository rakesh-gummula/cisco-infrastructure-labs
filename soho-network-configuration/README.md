# Project Overview
SOHO (Small Office Home Office) Network Configuration

Step 1: Network Planning and Addressing
Before plugging anything in, a network engineer plans the topology.
*Identify Devices: Count the number of wired devices (servers, desktop PCs, printers) and wireless devices (laptops, phones, IoT devices).
*Choose an IP Subnet: Select a private IP address range (RFC 1918). For a SOHO, a /24 subnet is standard.
Example: 192.168.10.0/24.
Static vs. Dynamic: Decide which devices need Static IPs (e.g., printers, NAS drives) and which will use DHCP (e.g., phones, laptops).

Step 2: Initial Device Access and Base Security
Never leave a router on its factory defaults.
*Connect: Connect a PC directly to one of the router's LAN ports via an Ethernet cable. The PC will automatically pull a default DHCP address (usually 192.168.1.x).
*Access the Web GUI/CLI: Open a browser and navigate to the default gateway (e.g., 192.168.1.1).
*Change Default Credentials: Immediately change the default admin/admin username and password to a strong, unique password.
*Update Firmware: Check the manufacturer's website and update the router to the latest firmware to patch any known security vulnerabilities.

Step 3: WAN (Internet) Configuration
This step connects your SOHO network to the outside world via the ISP (Internet Service Provider).
Connect to the Modem: Plug the cable from the ISP's modem into the router's designated WAN/Internet port.
*Configure the WAN Interface: Depending on the ISP, you will set the WAN port to:
*DHCP (Dynamic): The router automatically requests a public IP from the ISP (most common for cable/fiber internet).
*PPPoE: Requires a username and password provided by the ISP (common for DSL).
*Static IP: You manually enter the public IP, Subnet Mask, and Gateway provided by the ISP (common for business-tier internet).

Step 4: LAN and DHCP Configuration
Now, you configure the internal side of the network.
Set the Router's LAN IP: Change the router's internal IP address to match your planned subnet (e.g., change it from 192.168.1.1 to 192.168.10.1). This will be the Default Gateway for all internal devices.
Configure the DHCP Scope: Set up the pool of addresses the router will hand out.

Example Range: 192.168.10.100 to 192.168.10.200. (Leaving .2 to .99 available for static device assignment).
Set DNS Servers: Configure the DHCP server to hand out fast, reliable DNS servers to clients, such as Google (8.8.8.8) or Cloudflare (1.1.1.1).

Step 5: Wireless (WLAN) Configuration
Setting up the Wi-Fi requires balancing performance with security.
*Configure the SSID (Network Name): Create a clear name for your network. It is usually best practice to split the 2.4GHz and 5GHz bands into two separate SSIDs (e.g., MyNetwork_2G and MyNetwork_5G) so users can force their devices onto the faster 5GHz band.
*Wireless Security: Select WPA3 if all your devices support it, or WPA2-AES (never use WEP or TKIP, as they are highly vulnerable). Set a strong Wi-Fi passphrase.
*Channel Selection: Leave channel selection on "Auto", or use a Wi-Fi analyzer app to find the least congested channels in your area. For 2.4GHz, only use non-overlapping channels: 1, 6, or 11.
*Guest Network (Optional): Enable a Guest SSID. This uses a feature called "Client Isolation" to give visitors internet access while completely blocking them from communicating with your internal network (like your private NAS or printer).

Step 6: Advanced Security and Firewall (NAT/PAT)
*NAT (Network Address Translation): SOHO routers use PAT (Port Address Translation) by default to masquerade all your internal private IPs behind your single public ISP address. Ensure NAT is enabled.
*Disable UPnP (Universal Plug and Play): UPnP allows internal devices to automatically open firewall ports. This is a massive security risk and should generally be disabled.
*Port Forwarding: If you have an internal server (like a web server or a security camera NVR) that needs to be accessible from the internet, you must configure Port Forwarding to map external traffic on a specific port (e.g., Port 80) to the internal Static IP of that server.

Step 7: Verification and Testing
Once configured, prove the network works.
*Check IP Assignment: Run ipconfig (Windows) or ifconfig (Mac/Linux) on a client device to ensure it received the correct IP, Subnet Mask, and Gateway from your new DHCP scope.
*Ping Tests: Ping the default gateway (ping 192.168.10.1) to test LAN connectivity, then ping the internet (ping 8.8.8.8) to verify routing and NAT are functioning

You can add a lot of end point devices and configure them directly.
