# aws-to-fortigate-ipsec
Script to generate FortiGate CLI commands to create IPsec tunnel based on AWS config file.

## Installation
Clone the repository into your local machine

```bash
git clone https://github.com/fernandocastrovilar/aws-to-fortigate-ipsec.git
```

## Usage
Script is meant to be interactive, and will ask you for all the data needed to generate the final config file

It's important first get all the needed data from your FortiGate unit and from your aws account:

- FortiGate public interface name
- FortiGate public IP address
- FortiGate local interface name
- Local subnet IP/Name (if address already created use name, if not use ip subnet to create new entry)
- AWS subnet IP/name (if address already created use name, if not use ip subnet to create new entry)

The config file should be downloaded from AWS with the format of FortiOS 6.4.4+ (GUI)

```bash
./aws-to-fortigate-ipsec.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

DISCLAIMER
----------

**Tested on:**
- Python 3.9
- FortiOS v7.0.5

Please note: all tools/ scripts in this repo are released for use "AS IS" **without any warranties of any kind**,
including, but not limited to their installation, use, or performance.  We disclaim any and all warranties, either 
express or implied, including but not limited to any warranty of noninfringement, merchantability, and/ or fitness 
for a particular purpose.  We do not warrant that the technology will meet your requirements, that the operation 
thereof will be uninterrupted or error-free, or that any errors will be corrected.

Any use of these scripts and tools is **at your own risk**.  There is no guarantee that they have been through 
thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with 
their use.

You are responsible for reviewing and testing any scripts you run *thoroughly* before use in any non-testing 
environment.
