# Project Overview
This an Network Simulator Software.
It allows users to place nodes (PCs, Switches, Routers) on Canvas connect them, assign IP addresses, and visually simulate a basic network function, like a ping (ICMP request/reply).

## Core Features
  1. Drag and Drop Canvas
  2. Cable Connections
  3. Device Configuration
  4. Basic Validation
  5. The "Ping" Simulation

## Technologies used
  1. Python and Libraries
  2. Django Framework
  3. Matplotlib

## Step by Step Implementation Guide
1. The Core Architecture (The Python Logic Engine)
Before we draw any visual elements on a screen, the "brain" of your simulator must work. It needs to understand IP math, subnets, and forwarding logic.

We can design the data structures like this:
*Node Base Class: Represents any device on the network. It holds a hostname, an MAC address, and a routing/ARP table.
 *Host (Child Class): Inherits from Node. Represents a PC. Contains an IP address, Subnet Mask, and Default Gateway.
 *Switch (Child Class): Inherits from Node. Maintains a CAM (MAC Address) table and floods unknown unicast frames.
 *Router (Child Class): Inherits from Node. Has multiple interfaces (each with an IP/Subnet) and routes packets between them.

*Link Class: Represents the physical cable connecting two node interfaces.

*Packet / Frame Class: Represents the data structure moving across the links (containing Source IP, Dest IP, Source MAC, Dest MAC, and Payload).

2. The Functional MVP: Python Simulation Engine
Here is a functional, foundational script to get you started.
It uses Python's built-in ipaddress module (which handles all the complex binary math for subnets) to simulate a PC checking if another PC is on the same subnet, and then sending an ICMP Ping.


3. Building the Visual Interface (GUI)
Once your backend logic is robust enough to handle switches, MAC learning, and routers routing between different subnets, you need a way to visualize it.
*Tkinter(Beginner Friendly)
*PyQt or pySide6(Top Grade Desktop App)
*NetworkX + Matplotlib (Academic/Data Focus)

You can add even more features later to the source code and extend its functionality..
