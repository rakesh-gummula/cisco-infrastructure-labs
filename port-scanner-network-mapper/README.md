# Port Scanner & Network Mapper
A Python-based tool that discovers active hosts in a subnet and identifies open TCP ports on those hosts.

## Features
subnet scanning
live host detection
configurable port scanning
service name hints for common ports
JSON and CSV export
clean command-line output

## Use Case
Designed for authorized environments such as:
home labs
classroom exercises
internal networks you manage
CCNA practice environments

## Requirements
Python 3.10 or later
standard library modules only, or optional visualization libraries

## Installation
git clone https://rakesh-gummula.com/port-scanner-network-mapper.git
cd port-scanner-network-mapper
python -m venv venv
source venv/bin/activate
pip install -r requirements.

## Usage
python main.py --subnet 192.168.1.0/24 --ports 22,80,443,445,3389
Example
python main.py --subnet 10.0.0.0/24 --ports 21,22,23,80,443

## Output
The tool prints:
active hosts
open ports for each host
service labels
scan summary

It can also export results to:

results/scan.json
results/scan.csv

## Project Structure
port-scanner-network-mapper/
├── main.py
├── scanner/
│   ├── discovery.py
│   ├── ports.py
│   ├── services.py
│   └── report.py
├── results/
├── tests/
└── README.md

## Example Result
Host: 192.168.1.10
  Open Ports: 22 (SSH), 80 (HTTP)
Host: 192.168.1.15
  Open Ports: 443 (HTTPS)
  
## Safety Notice
Use only on networks and hosts you are authorized to test.

## Future Work
UDP support
banner collection
graph visualization
faster scan tuning
web interface

## License
MIT Opensource License
