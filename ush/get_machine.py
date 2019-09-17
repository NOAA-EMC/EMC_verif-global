##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Get machine that where verif_global is being run
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

from __future__ import (print_function, division)
import os
import re

print("BEGIN: "+os.path.basename(__file__))

hostname = os.environ['HOSTNAME']
if "machine" in os.environ:
    machine = os.environ['machine']
else:
    if "MACHINE" in os.environ:
        machine = os.environ['MACHINE']
    else:
        theia_match = re.match(re.compile(r"^tfe[0-9]{2}$"), hostname)
        hera_match = re.match(re.compile(r"^hfe[0-9]{2}$"), hostname)
        surge_match = re.match(re.compile(r"^slogin[0-9]{1}$"), hostname)
        luna_match = re.match(re.compile(r"^llogin[0-9]{1}$"), hostname)
        mars_match = re.match(re.compile(r"^m[0-9]{2}[a-z]{1}[0-9]{1}$"), hostname)
        venus_match = re.match(re.compile(r"^v[0-9]{2}[a-z]{1}[0-9]{1}$"), hostname)
        if theia_match:
            machine = 'THEIA'
        elif hera_match:
            machine = 'HERA'
        elif surge_match or luna_match:
            machine = 'WCOSS_C'
        elif mars_match or venus_match:
            machine = 'WCOSS_DELL_P3'
        else:
            print("Cannot find match for "+hostname)
            exit(1)
    with open('config.machine', 'a') as file:
        file.write('#!/bin/sh\n')
        file.write('echo "BEGIN: config.machine"\n')
        file.write('export machine='+'"'+machine+'"\n')
        file.write('echo "END: config.machine"')
print("Working "+hostname+" on "+machine)

print("END: "+os.path.basename(__file__))
