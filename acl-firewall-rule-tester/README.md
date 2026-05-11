# ACL(Access Control List) Firewall Rule Tester
## Project Overview
Goal:
Build a networking project that simulates how ACL (Access Control List) firewall rules work in routers and firewalls.
 -Accept firewall/ACL rules
 -Accept packet details
 -Determine whether the packet is PERMITTED or DENIED
 -Show which rule matched
 -Simulate real Cisco-style ACL behavior

 ## Tech Stack to use
 Backend: Python
 Libraries:
 -ipaddress (built-in)
 -Flask (optional for web version)
 -Rich (for colorful CLI)
 -pytest (testing)

 Frontend Optional:
 -Option A: Command Line Interface
 -Option B: React frontend + Flask Backend

 ## Step by Step Implementation Statergy
Step 1: The Parser
You need to convert a string like permit tcp 192.168.1.0 0.0.0.255 any eq 80 into data your code can understand.
Write a function that splits this string into variables: action, protocol, src_ip, src_mask, dst_ip, dst_mask, port.
Tip: Convert Cisco wildcard masks (e.g., 0.0.0.255) to standard CIDR notation (/24) using Python's ipaddress library to make the math easier.

Step 2: The Evaluator (The Core Logic)
Write the logic that compares a test packet against your parsed rules.
Match Protocol: Is the packet TCP, UDP, or IP?
Match Source/Dest: Is the packet's IP inside the rule's defined subnet? ipaddress.ip_address('192.168.1.5') in ipaddress.ip_network('192.168.1.0/24') will do the heavy lifting here.
Match Port: Does it match the eq (equal), gt (greater than), or lt (less than) port rules?

Step 3: Top-Down Execution
Create a loop that iterates through your parsed ACL list.
The moment a packet matches a rule, break the loop, return the action (Permit/Deny), and log the line number.
If the loop finishes and no rules match, return Deny (simulating the implicit deny at the end of all ACLs).
