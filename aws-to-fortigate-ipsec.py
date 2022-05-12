#!/usr/bin/python
import os
import sys
import re

# Basic data input
ipsec_name = input("Enter tunnel name: ")
aws_file = input("Enter aws config file path: ")
public_interface = input("Enter FortiGate public interface name: ")
public_gw = input("Enter FortiGate public ip (ip on interface {0}): ".format(public_interface))
local_interface = input("Enter FortiGate local interface name: ")

# Set files and directories
pwd = os.getcwd()
out_file = ipsec_name + "_config.txt"
file_path = pwd + "/" + out_file


# Ask yes/no
def question():
    i = 0
    answer = None
    while i < 2:
        answer = input("(yes or no): ")
        if any(answer.lower() == f for f in ["yes", 'y', '1', 'ye']):
            answer = "yes"
            break
        elif any(answer.lower() == f for f in ['no', 'n', '0']):
            answer = "no"
            break
        else:
            i += 1
            if i < 2:
                print('Please enter yes or no')
            else:
                answer = "ko"
                print("Nothing done")
    return answer


# Check if file already exist
if os.path.isfile(file_path):
    print("\nFile {0} already exist and will be overwrite.".format(file_path))
    print("Do you want to proceed?".format(file_path))
    out = question()
    if out == "yes":
        os.remove(file_path)
    elif out == "no":
        print("Please, enter another tunnel name, file exists and cannot be overwritten")
        sys.exit(1)
    else:
        print("ERROR")
        sys.exit(1)


# Define variables from AWS config file
print("\nReading data from aws config file {0}\n...".format(aws_file))
try:
    with open(aws_file) as aws_config:
        comment = None
        tun1_aws_ip = None
        tun1_aws_psk = None
        tun1_aws_phase2_name = None
        tun2_aws_ip = None
        tun2_aws_psk = None
        tun2_aws_phase2_name = None
        for line in aws_config:
            # Tunnel comment
            if line.startswith("! Your VPN Connection ID"):
                comment = line.split(":")[1].replace(" ", "").replace("\n", "")

            # Tunnel IP
            if line.startswith("c. IP address:"):
                if not tun1_aws_ip:
                    tun1_aws_ip = re.findall(r'\d+(?:\.\d+){3}', line)
                    tun1_aws_ip = str(tun1_aws_ip).replace("['", "").replace("']", "")
                else:
                    tun2_aws_ip = re.findall(r'\d+(?:\.\d+){3}', line)
                    tun2_aws_ip = str(tun2_aws_ip).replace("['", "").replace("']", "")

            # Pre-shared key
            if line.startswith("h. Pre-Shared Key:"):
                if not tun1_aws_psk:
                    tun1_aws_psk = line.split(": ")[1].replace(" ", "").replace("\n", "")
                else:
                    tun2_aws_psk = line.split(": ")[1].replace(" ", "").replace("\n", "")

            # Phase2 name
            if line.startswith("a.\tName:"):
                if not tun1_aws_phase2_name:
                    tun1_aws_phase2_name = line.split(": ")[1].replace(" ", "").replace("\n", "")
                else:
                    tun2_aws_phase2_name = line.split(": ")[1].replace(" ", "").replace("\n", "")
    print("Data successfully dumped from aws config file")
except Exception as err:
    print("Failed to read data from aws config file", err)
    sys.exit(err)


# Read template blocks
try:
    with open('template.txt', 'r') as file:
        template = file.read()
        ipsec_block = template.split("## START ipsec phases")[1].split("## END ipsec phases")[0]
        ipsec_aggregate_block = template.split("## START ipsec-aggregate")[1].split("## END ipsec-aggregate")[0]
        static_route_block = template.split("## START static route")[1].split("## END static route")[0]
        firewall_policy_block = template.split("## START firewall policies")[1].split("## END firewall policies")[0]
        create_address_block = template.split("## START create address subnet")[1].split("## END create address subnet")[0]
except Exception as err:
    print("\nFailed to read data from template", err)
    sys.exit(err)

# Ask for subnets info
print("\nSource and destination net are needed to create tunnel,")
print("have you already defined addresses at FortiGate?")
print("(If no, you will be asked after for the data to generate new nets addresses)")
out = question()
create_subnets_block = False
if out == "yes":
    source_net_name = None
    aws_net_name = None
    aws_address_subnet = None
    while not source_net_name:
        source_net_name = input("Please, enter source net name (defined at FortiGate 'Addresses' section): ")
    while not aws_net_name:
        aws_net_name = input("Please, enter destination net name (defined at FortiGate): ")
    while not aws_address_subnet:
        aws_address_subnet = input("Please, enter destination subnet ip (format: 192.168.1.0 255.255.255.0): ")
elif out == "no":
    create_subnets_block = True
    print("Commands to create subnets addresses will be generated\n")
    source_address_subnet = None
    aws_address_subnet = None
    while not source_address_subnet:
        source_address_subnet = input("Please, enter source subnet (format: 192.168.1.0 255.255.255.0: ")
    while not aws_address_subnet:
        aws_address_subnet = input("Please, enter destination aws subnet (format: 192.168.1.0 255.255.255.0: ")
    source_net_name = "IPSEC_{0}_subnet_local".format(ipsec_name)
    aws_net_name = "IPSEC_{0}_subnet_aws".format(ipsec_name)
    create_address_block = create_address_block.format(source_net_name, source_address_subnet, aws_net_name,
                                                       aws_address_subnet)


# Define blocks with variables
ipsec_block = ipsec_block.format(ipsec_name, comment, tun1_aws_ip, tun1_aws_psk, tun2_aws_ip, tun2_aws_psk,
                                 tun1_aws_phase2_name, tun2_aws_phase2_name, public_interface, public_gw,
                                 source_net_name, aws_net_name)
ipsec_aggregate_block = ipsec_aggregate_block.format(ipsec_name)
static_route_block = static_route_block.format(aws_address_subnet, ipsec_name)
firewall_policy_block = firewall_policy_block.format(ipsec_name, local_interface)


# Write data to file
print("Generating file with CLI commands to create tunnel at FortiGate...")
try:
    with open(out_file, 'w') as outfile:
        # Write subnet creation commands if defined
        if create_subnets_block:
            outfile.write(create_address_block)
        # Write common config
        outfile.write(ipsec_block)
        outfile.write(ipsec_aggregate_block)
        outfile.write(static_route_block)
        outfile.write(firewall_policy_block)
    print("\nFile successfully created! You can copy content from {0}".format(file_path))
except Exception as err:
    print("Something went wrong...")
    sys.exit(err)
