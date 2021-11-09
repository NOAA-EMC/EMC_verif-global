'''
Program Name: get_machine.py
Contact(s): Mallory Row
Abstract: This script is run by set_up_verif_global.sh.
          It gets the name of the name of the machine being
          run on by checking environment variables "machine"
          or "MACHINE". If not does matching based on environment
          variable "HOSTNAME" or output from hostname executable.
'''

import sys
import os
import re
import subprocess

print("BEGIN: "+os.path.basename(__file__))

EMC_verif_global_machine_list = [
    'HERA', 'ORION', 'WCOSS_C', 'WCOSS_DELL_P3', 'S4', 'JET'
]

# Read in environment variables
if not 'HOSTNAME' in list(os.environ.keys()):
    hostname = subprocess.check_output(
        'hostname', shell=True, encoding='UTF-8'
    ).replace('\n', '')
else:
    hostname = os.environ['HOSTNAME']

# Get machine name
for env_var in ['machine', 'MACHINE']:
    if env_var in os.environ:
        if os.environ[env_var] in EMC_verif_global_machine_list:
            print("Found environment variable "
                  +env_var+"="+os.environ[env_var])
            machine = os.environ[env_var]
            break
if 'machine' not in vars():
    hera_match = re.match(re.compile(r"^hfe[0-9]{2}$"), hostname)
    orion_match = re.match(
        re.compile(r"^Orion-login-[0-9]{1}.HPC.MsState.Edu$"), hostname
    )
    surge_match = re.match(re.compile(r"^slogin[0-9]{1}$"), hostname)
    luna_match = re.match(re.compile(r"^llogin[0-9]{1}$"), hostname)
    mars_match = re.match(re.compile(r"^m[0-9]{2,3}[a-z]{1}[0-9]{1}$"),
                          hostname)
    mars_match2 = re.match(
        re.compile(r"^m[0-9]{2,3}[a-z]{1}[0-9]{1,3}[a-z]{1}$"), hostname
    )
    venus_match = re.match(re.compile(r"^v[0-9]{2,3}[a-z]{1}[0-9]{1}$"),
                           hostname)
    venus_match2 = re.match(
        re.compile(r"^v[0-9]{2,3}[a-z]{1}[0-9]{1,3}[a-z]{1}$"), hostname
    )
    s4_match = re.match(re.compile(r"s4-submit.ssec.wisc.edu"), hostname)
    jet_match = re.match(re.compile(r"^fe[0-9]{1}"), hostname)
    if hera_match:
        machine = 'HERA'
    elif orion_match:
        machine = 'ORION'
    elif surge_match or luna_match:
        machine = 'WCOSS_C'
    elif mars_match or venus_match or mars_match2 or venus_match2:
        machine = 'WCOSS_DELL_P3'
    elif s4_match:
        machine = 'S4'
    elif jet_match:
        machine = 'JET'
    else:
        print("Cannot find match for "+hostname)
        sys.exit(1)

# Write to machine config file
if not os.path.exists('config.machine'):
    with open('config.machine', 'a') as file:
        file.write('#!/bin/sh\n')
        file.write('echo "BEGIN: config.machine"\n')
        file.write('echo "Setting machine='+'"'+machine+'""\n')
        file.write('export machine='+'"'+machine+'"\n')
        file.write('echo "END: config.machine"')

print("Working "+hostname+" on "+machine)

print("END: "+os.path.basename(__file__))
