import ipaddress
import argparse
import sys

def wildcard_to_network(ip_str, wildcard_str="0.0.0.0"):
    """Converts a Cisco IP and Wildcard Mask into a standard network object."""
    if ip_str.lower() == "any":
        return ipaddress.IPv4Network("0.0.0.0/0")
        
    wildcard_octets = wildcard_str.split('.')
    subnet_octets = [str(255 - int(octet)) for octet in wildcard_octets]
    subnet_mask = '.'.join(subnet_octets)
    
    network_string = f"{ip_str}/{subnet_mask}"
    return ipaddress.IPv4Network(network_string, strict=False)

def parse_acl_file(filepath):
    """Reads a text file and extracts the ACL rules into a list of dictionaries."""
    rules = []
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                # Skip blank lines and Cisco-style comments
                if not line or line.startswith('!') or line.startswith('#'):
                    continue 
                
                parts = line.split()
                # Ensure the line has enough parts to be a valid rule
                if len(parts) >= 3:
                    action = parts[0].lower()
                    
                    # Handle the 'any' keyword for source IP
                    if parts[2].lower() == 'any':
                        src_ip = 'any'
                        src_wild = 'any'
                    else:
                        src_ip = parts[2]
                        src_wild = parts[3]
                        
                    rules.append({
                        "raw_rule": line,
                        "action": action,
                        "src_ip": src_ip,
                        "src_wildcard": src_wild
                    })
    except FileNotFoundError:
        print(f"[-] Error: Could not find the file '{filepath}'.")
        sys.exit(1)
        
    return rules

def test_packet(acl_rules, source_ip):
    """Evaluates the test IP against the parsed rules top-down."""
    try:
        packet_src = ipaddress.IPv4Address(source_ip)
    except ValueError:
        return {"status": "ERROR", "reason": "Invalid IP address format."}

    for line_number, rule in enumerate(acl_rules, start=1):
        action = rule['action']
        src_network = wildcard_to_network(rule['src_ip'], rule['src_wildcard'])
        
        # The core check: Is the packet inside this rule's subnet?
        if packet_src in src_network:
            return {
                "status": action.upper(),
                "reason": f"Matched Rule {line_number} -> '{rule['raw_rule']}'"
            }
            
    # Implicit Deny if no rules match
    return {
        "status": "DENY",
        "reason": "Implicit Deny (No rules matched)"
    }

if __name__ == "__main__":
    # Setup the command line interface
    parser = argparse.ArgumentParser(description="ACL Firewall Rule Tester")
    parser.add_argument("-f", "--file", required=True, help="Path to the ACL text file")
    parser.add_argument("-ip", "--source_ip", required=True, help="The Source IP to test")
    
    args = parser.parse_args()

    # 1. Parse the rules
    print(f"[*] Loading ACL rules from {args.file}...")
    rules = parse_acl_file(args.file)
    print(f"[*] Loaded {len(rules)} active rules.\n")

    # 2. Test the packet
    print(f"[*] Testing Source IP: {args.source_ip}")
    result = test_packet(rules, args.source_ip)

    # 3. Print the result
    if result['status'] == 'PERMIT':
        print(f"\n[+] RESULT: {result['status']}")
        print(f"[+] REASON: {result['reason']}")
    else:
        print(f"\n[-] RESULT: {result['status']}")
        print(f"[-] REASON: {result['reason']}")
