# VLAN & STP Troubleshooting Lab

A hands-on CCNA-level troubleshooting lab focused on VLAN segmentation, trunking, and Spanning Tree Protocol (STP) behavior.

## Overview

This lab is designed to help you practice identifying and fixing common Layer 2 issues in a small switched network. The scenario includes intentional misconfigurations related to:

* VLAN assignment
* Trunk negotiation
* Native VLAN mismatch
* Allowed VLAN pruning
* STP root bridge placement
* PortFast and edge-port behavior
* Errdisabled or blocked connectivity symptoms

## Lab Goals

By the end of this lab, you should be able to:

* Verify VLAN membership on access ports
* Confirm trunk links and allowed VLANs
* Detect and correct native VLAN mismatches
* Examine STP topology and root bridge selection
* Use CLI show commands to isolate Layer 2 faults
* Document findings like a network engineer

## Topology

Use the following logical topology:

```text
PC1 --- SW1 --- SW2 --- SW3 --- PC2
          \             /
           \--- SW4 ----/
```

### Device Roles

* SW1: Distribution switch / intended STP root for VLAN 10
* SW2: Access switch
* SW3: Access switch
* SW4: Redundant Layer 2 switch
* PC1: VLAN 10 host
* PC2: VLAN 20 host

## VLAN Plan

| VLAN | Name             | Purpose                     |
| ---- | ---------------- | --------------------------- |
| 10   | USERS            | User endpoint VLAN          |
| 20   | VOICE            | Voice / alternate host VLAN |
| 99   | MANAGEMENT       | Switch management           |
| 999  | NATIVE-BLACKHOLE | Native VLAN for trunks      |

## IP Addressing Plan

| Device | Interface / VLAN | IP Address     | Default Gateway |
| ------ | ---------------- | -------------- | --------------- |
| PC1    | NIC              | 10.10.10.10/24 | 10.10.10.1      |
| PC2    | NIC              | 10.10.20.20/24 | 10.10.20.1      |
| SW1    | VLAN 99          | 10.10.99.11/24 | 10.10.99.1      |
| SW2    | VLAN 99          | 10.10.99.12/24 | 10.10.99.1      |
| SW3    | VLAN 99          | 10.10.99.13/24 | 10.10.99.1      |
| SW4    | VLAN 99          | 10.10.99.14/24 | 10.10.99.1      |

## Lab Scenario

The network is experiencing intermittent or complete loss of connectivity between users in the same VLAN and across the switched domain. Some ports appear up, but traffic does not pass correctly. Your job is to identify the root causes and restore full connectivity.

## Intentional Faults

Use the following misconfigurations in the lab image or prebuilt Packet Tracer/GNS3/physical setup:

1. One access port on SW2 is assigned to the wrong VLAN.
2. One trunk link between SW1 and SW3 does not allow VLAN 20.
3. A native VLAN mismatch exists between SW1 and SW4.
4. SW4 is incorrectly acting as the STP root for VLAN 10.
5. One access port has PortFast disabled, causing delayed host connectivity.

## Tasks

### Task 1: Discover the VLAN problem

* Identify which access port is in the wrong VLAN.
* Move it to the correct VLAN.
* Verify host connectivity.

### Task 2: Fix trunking

* Inspect trunk status on all switch interlinks.
* Find the trunk that is missing VLAN 20.
* Allow the correct VLANs across the trunk.

### Task 3: Resolve native VLAN mismatch

* Detect the mismatch using CDP or interface output.
* Set the same native VLAN on both sides of the trunk.
* Confirm the warning disappears.

### Task 4: Correct STP root placement

* Check the STP root bridge for VLAN 10 and VLAN 20.
* Make SW1 the primary root for VLAN 10.
* Make SW1 or SW2 the secondary root, depending on your design.

### Task 5: Validate edge-port behavior

* Ensure user-facing ports use PortFast.
* Confirm end hosts come up quickly after link-up.

## Useful Verification Commands

### VLAN and Trunking

```bash
show vlan brief
show interfaces trunk
show interfaces switchport
show cdp neighbors detail
```

### STP

```bash
show spanning-tree
show spanning-tree vlan 10
show spanning-tree vlan 20
show spanning-tree root
show spanning-tree interface <interface-id> detail
```

### Interface Status

```bash
show ip interface brief
show interfaces status
show interfaces <interface-id> counters
show logging
```

## Example Troubleshooting Flow

1. Check whether the PC can ping its default gateway.
2. Verify the PC is in the correct VLAN.
3. Check whether the uplink is a trunk.
4. Confirm the correct VLANs are allowed on the trunk.
5. Compare native VLAN settings on both ends.
6. Inspect STP root bridge election for each VLAN.
7. Re-test connectivity after each change.

## Expected Fixes

### Example Access Port Correction

```bash
interface fa0/3
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
```

### Example Trunk Fix

```bash
interface gi0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99,999
```

### Example STP Root Configuration

```bash
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root primary
```

Or use explicit priority:

```bash
spanning-tree vlan 10 priority 4096
spanning-tree vlan 20 priority 4096
```

## Validation Checklist

* PC1 can ping its gateway.
* PC2 can ping its gateway.
* PC1 and PC2 can ping each other if inter-VLAN routing is present.
* All intended VLANs appear on the trunk.
* No native VLAN mismatch warnings remain.
* SW1 is the STP root for the chosen VLANs.
* User-facing ports forward quickly after link-up.

## Troubleshooting Notes

Use this section to document what you found and how you fixed it.

| Symptom                              | Root Cause                | Fix                                  |
| ------------------------------------ | ------------------------- | ------------------------------------ |
| PC cannot ping gateway               | Access port in wrong VLAN | Reassign port to correct VLAN        |
| Host-to-host failure across switches | Trunk missing VLAN        | Add VLAN to allowed list             |
| CDP native VLAN warning              | Native VLAN mismatch      | Match native VLAN on both sides      |
| Unexpected blocked port              | Wrong STP root bridge     | Adjust STP priority or root settings |

## Suggested GitHub Repository Structure

```text
vlan-stp-troubleshooting-lab/
├── README.md
├── topology.png
├── configs/
│   ├── sw1.txt
│   ├── sw2.txt
│   ├── sw3.txt
│   └── sw4.txt
└── notes/
    └── troubleshooting-log.md
```

## Summary

This lab demonstrates how to diagnose and repair VLAN and STP issues in a small switched network. It is intended for CCNA learners who want hands-on experience with Layer 2 troubleshooting, root bridge selection, and trunk validation.

## Optional

* Add a second STP instance and compare root placement.
* Introduce EtherChannel and troubleshoot a misbundled link.
* Create an SVI management-only design and test remote access.
* Add a rogue trunk and secure it with DTP off and explicit trunking.

---

## License

MIT Opensource Licensing
