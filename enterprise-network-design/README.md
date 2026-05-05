# Project title
Enterprise Network Design with VLANs, Inter-VLAN Routing, DHCP, NAT, and OSPF

## Step by step to complete 
1) Design the network first
Before touching Packet Tracer, decide the IP plan.
Example:
HR → 192.168.10.0/24
Finance → 192.168.20.0/24
IT → 192.168.30.0/24
Router links → 10.0.0.0/30 or 10.0.0.0/24

2) Build the topology in Packet Tracer
*Use:
1 router for inter-VLAN routing
1 or 2 switches
6–9 PCs
1 second router if you want OSPF
Optional cloud for “internet”
*A good beginner topology is:
Router 1 connected to Switch 1
Switch 1 connected to departments’ PCs
Router 1 connected to Router 2
Router 2 represents ISP or another site

3) Create VLANs on the switch
*Create these VLANs:
VLAN 10 → HR
VLAN 20 → Finance
VLAN 30 → IT
Assign switch ports to the correct VLANs.
*Example logic:
Ports for HR PCs → VLAN 10
Ports for Finance PCs → VLAN 20
Ports for IT PCs → VLAN 30
Also make the uplink port a trunk.

4) Configure router-on-a-stick
On the router connected to the switch, create subinterfaces.
*You will give each VLAN its own gateway IP:
192.168.10.1
192.168.20.1
192.168.30.1
Each subinterface must use 802.1Q encapsulation for the matching VLAN.

6) Configure DHCP
Make the router hand out IP addresses automatically.
*For each VLAN, configure:
network address
default gateway
excluded addresses for router and reserved devices
That way, PCs in each department get IPs without manual setup.

7) Configure OSPF
If you include a second router, use OSPF so the routers learn each other’s networks dynamically.
This adds real CCNA value because it shows routing knowledge beyond static routes.

8) Configure NAT
If you simulate internet access, configure NAT overload on the edge router.
That shows private IPs can reach an outside network through one public address.
This is a very good CCNA topic to include in your project.

9) Add basic security
Do a few simple hardening steps:
disable unused switch ports
set an enable secret
configure console and VTY passwords
optional port security on access ports
This makes the project feel more complete and realistic.

11) Test everything
You need proof that it works.
*Test:
PC to default gateway
PC to PC within same VLAN
PC to PC across VLANs
DHCP address assignment
OSPF neighbor status
NAT functionality if included
