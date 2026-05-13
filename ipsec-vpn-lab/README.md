# Site-to-Site IPsec VPN Lab

## Objective
Build and verify a site-to-site IPsec VPN between two Cisco routers so traffic between two LANs is encrypted.

## Topology
- Site A LAN: 192.168.1.0/24
- Site B LAN: 192.168.2.0/24
- WAN Link: 10.0.0.0/30

## IP Addressing
| Device | Interface | IP Address | Mask |
|--------|-----------|------------|------|
| R1 | G0/0 | 192.168.1.1 | 255.255.255.0 |
| R1 | G0/1 | 10.0.0.1 | 255.255.255.252 |
| R2 | G0/0 | 192.168.2.1 | 255.255.255.0 |
| R2 | G0/1 | 10.0.0.2 | 255.255.255.252 |
| PC1 | NIC | 192.168.1.10 | 255.255.255.0 |
| PC2 | NIC | 192.168.2.10 | 255.255.255.0 |

## VPN Type
- Site-to-site IPsec
- IKEv1
- Pre-shared key authentication
- AES 256 encryption
- SHA hashing

## Verification
- `show crypto isakmp sa`
- `show crypto ipsec sa`
- Ping from PC1 to PC2

## Result
Traffic between the two LANs is encrypted successfully through the VPN tunnel.
