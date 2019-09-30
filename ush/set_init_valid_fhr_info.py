##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Set up valid, initialization, and forecast hour information
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

from __future__ import (print_function, division)
import os
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
env_var_dict = {}

if RUN == 'grid2grid_step1':
    fhr_min = float(os.environ['g2g1_fhr_min'])
    fhr_max = float(os.environ['g2g1_fhr_max'])
    fcyc_list = os.environ['g2g1_fcyc_list'].split(' ')
    vhr_list = os.environ['g2g1_vhr_list'].split(' ')

    nfcyc = len(fcyc_list)
    nvhr = len(vhr_list)
    if nfcyc > nvhr:
        fhr_intvl = int(24/nfcyc)
    else:
        fhr_intvl = int(24/nvhr)
    nfhr = fhr_max/fhr_intvl
    fhr_max = int(nfhr*fhr_intvl)
    fhr_list = []
    fhr = fhr_min
    while fhr <= fhr_max:
        fhr_list.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl

    valid_hr_beg = vhr_list[0]
    valid_hr_end = vhr_list[-1]
    valid_hr_inc = int((24/nvhr)*3600)
    init_hr_beg = fcyc_list[0]
    init_hr_end = fcyc_list[-1]
    init_hr_inc = int((24/nfcyc)*3600)

    env_var_dict['g2g1_fhr_list'] = ' '.join(fhr_list).replace(' ', ', ')
    env_var_dict['g2g1_valid_hr_beg'] = str(valid_hr_beg).zfill(2)
    env_var_dict['g2g1_valid_hr_end'] = str(valid_hr_end).zfill(2)
    env_var_dict['g2g1_valid_hr_inc'] = str(valid_hr_inc)
    env_var_dict['g2g1_init_hr_beg'] = str(init_hr_beg).zfill(2)
    env_var_dict['g2g1_init_hr_end'] = str(init_hr_end).zfill(2)
    env_var_dict['g2g1_init_hr_inc'] = str(init_hr_inc)

elif RUN == 'grid2grid_step2':
    fhr_min = float(os.environ['g2g2_fhr_min'])
    fhr_max = float(os.environ['g2g2_fhr_max'])
    fcyc_list = os.environ['g2g2_fcyc_list'].split(' ')
    vhr_list = os.environ['g2g2_vhr_list'].split(' ')

    nfcyc = len(fcyc_list)
    nvhr = len(vhr_list)
    if nfcyc > nvhr:
        fhr_intvl = int(24/nfcyc)
    else:
        fhr_intvl = int(24/nvhr)
    nfhr = fhr_max/fhr_intvl
    fhr_max = int(nfhr*fhr_intvl)
    fhr_list = []
    fhr = fhr_min
    while fhr <= fhr_max:
        fhr_list.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl

    valid_hr_beg = vhr_list[0]
    valid_hr_end = vhr_list[-1]
    valid_hr_inc = int((24/nvhr)*3600)
    init_hr_beg = fcyc_list[0]
    init_hr_end = fcyc_list[-1]
    init_hr_inc = int((24/nfcyc)*3600)

    env_var_dict['g2g2_fhr_list'] = ' '.join(fhr_list).replace(' ', ', ')
    env_var_dict['g2g2_valid_hr_beg'] = str(valid_hr_beg).zfill(2)
    env_var_dict['g2g2_valid_hr_end'] = str(valid_hr_end).zfill(2)
    env_var_dict['g2g2_valid_hr_inc'] = str(valid_hr_inc)
    env_var_dict['g2g2_init_hr_beg'] = str(init_hr_beg).zfill(2)
    env_var_dict['g2g2_init_hr_end'] = str(init_hr_end).zfill(2)
    env_var_dict['g2g2_init_hr_inc'] = str(init_hr_inc)

elif RUN == 'grid2obs_step1':
    fcyc_list = os.environ['g2o1_fcyc_list'].split(' ')
    fhr_min = float(os.environ['g2o1_fhr_min'])
    fhr_max = float(os.environ['g2o1_fhr_max']) 
    vhr_list_upper_air = os.environ['g2o1_vhr_list_upper_air'].split(' ')
    vhr_list_conus_sfc = os.environ['g2o1_vhr_list_conus_sfc'].split(' ')
    
    nfcyc = len(fcyc_list)

    nvhr_upper_air = len(vhr_list_upper_air)
    if nfcyc > nvhr_upper_air:
        fhr_intvl_upper_air = int(24/nfcyc)
    else:
        fhr_intvl_upper_air = int(24/nvhr_upper_air)
    nfhr_upper_air = fhr_max/fhr_intvl_upper_air
    fhr_max_upper_air = int(nfhr_upper_air*fhr_intvl_upper_air)
    fhr_list_upper_air = []
    fhr = fhr_min
    while fhr <= fhr_max_upper_air:
        fhr_list_upper_air.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl_upper_air
    nvhr_conus_sfc = len(vhr_list_conus_sfc)
    if nfcyc > nvhr_conus_sfc:
        fhr_intvl_conus_sfc = int(24/nfcyc)
    else:
        fhr_intvl_conus_sfc = int(24/nvhr_conus_sfc)
    nfhr_conus_sfc = fhr_max/fhr_intvl_conus_sfc
    fhr_max_conus_sfc = int(nfhr_conus_sfc*fhr_intvl_conus_sfc)
    fhr_list_conus_sfc = []
    fhr = fhr_min
    while fhr <= fhr_max_conus_sfc:
        fhr_list_conus_sfc.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl_conus_sfc
 
    valid_hr_beg_upper_air = vhr_list_upper_air[0]
    valid_hr_end_upper_air = vhr_list_upper_air[-1]
    valid_hr_inc_upper_air = int((24/nvhr_upper_air)*3600)
    valid_hr_beg_conus_sfc = vhr_list_conus_sfc[0]
    valid_hr_end_conus_sfc = vhr_list_conus_sfc[-1]
    valid_hr_inc_conus_sfc = int((24/nvhr_conus_sfc)*3600)
    init_hr_beg = fcyc_list[0]
    init_hr_end = fcyc_list[-1]
    init_hr_inc = int((24/nfcyc)*3600)

    env_var_dict['g2o1_fhr_list_upper_air'] = ' '.join(fhr_list_upper_air) \
        .replace(' ', ', ')
    env_var_dict['g2o1_fhr_list_conus_sfc'] = ' '.join(fhr_list_conus_sfc) \
        .replace(' ', ', ')
    env_var_dict['g2o1_valid_hr_beg_upper_air'] = str(valid_hr_beg_upper_air).zfill(2)
    env_var_dict['g2o1_valid_hr_end_upper_air'] = str(valid_hr_end_upper_air).zfill(2)
    env_var_dict['g2o1_valid_hr_inc_upper_air'] = str(valid_hr_inc_upper_air)
    env_var_dict['g2o1_valid_hr_beg_conus_sfc'] = str(valid_hr_beg_conus_sfc).zfill(2)
    env_var_dict['g2o1_valid_hr_end_conus_sfc'] = str(valid_hr_end_conus_sfc).zfill(2)
    env_var_dict['g2o1_valid_hr_inc_conus_sfc'] = str(valid_hr_inc_conus_sfc)
    env_var_dict['g2o1_init_hr_beg'] = str(init_hr_beg).zfill(2)
    env_var_dict['g2o1_init_hr_end'] = str(init_hr_end).zfill(2)
    env_var_dict['g2o1_init_hr_inc'] = str(init_hr_inc).zfill(2)

elif RUN == 'grid2obs_step2':
    fcyc_list = os.environ['g2o2_fcyc_list'].split(' ')
    fhr_min = float(os.environ['g2o2_fhr_min'])
    fhr_max = float(os.environ['g2o2_fhr_max'])
    vhr_list_upper_air = os.environ['g2o2_vhr_list_upper_air'].split(' ')
    vhr_list_conus_sfc = os.environ['g2o2_vhr_list_conus_sfc'].split(' ')

    nfcyc = len(fcyc_list)

    nvhr_upper_air = len(vhr_list_upper_air)
    if nfcyc > nvhr_upper_air:
        fhr_intvl_upper_air = int(24/nfcyc)
    else:
        fhr_intvl_upper_air = int(24/nvhr_upper_air)
    nfhr_upper_air = fhr_max/fhr_intvl_upper_air
    fhr_max_upper_air = int(nfhr_upper_air*fhr_intvl_upper_air)
    fhr_list_upper_air = []
    fhr = fhr_min
    while fhr <= fhr_max_upper_air:
        fhr_list_upper_air.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl_upper_air
    nvhr_conus_sfc = len(vhr_list_conus_sfc)
    if nfcyc > nvhr_conus_sfc:
        fhr_intvl_conus_sfc = int(24/nfcyc)
    else:
        fhr_intvl_conus_sfc = int(24/nvhr_conus_sfc)
    nfhr_conus_sfc = fhr_max/fhr_intvl_conus_sfc
    fhr_max_conus_sfc = int(nfhr_conus_sfc*fhr_intvl_conus_sfc)
    fhr_list_conus_sfc = []
    fhr = fhr_min
    while fhr <= fhr_max_conus_sfc:
        fhr_list_conus_sfc.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl_conus_sfc

    valid_hr_beg_upper_air = vhr_list_upper_air[0]
    valid_hr_end_upper_air = vhr_list_upper_air[-1]
    valid_hr_inc_upper_air = int((24/nvhr_upper_air)*3600)
    valid_hr_beg_conus_sfc = vhr_list_conus_sfc[0]
    valid_hr_end_conus_sfc = vhr_list_conus_sfc[-1]
    valid_hr_inc_conus_sfc = int((24/nvhr_conus_sfc)*3600)
    init_hr_beg = fcyc_list[0]
    init_hr_end = fcyc_list[-1]
    init_hr_inc = int((24/nfcyc)*3600)

    env_var_dict['g2o2_fhr_list_upper_air'] = (
        ' '.join(fhr_list_upper_air).replace(' ', ', ')
    )
    env_var_dict['g2o2_fhr_list_conus_sfc'] = (
        ' '.join(fhr_list_conus_sfc).replace(' ', ', ')
    )
    env_var_dict['g2o2_valid_hr_beg_upper_air'] = (
        str(valid_hr_beg_upper_air).zfill(2)
    )
    env_var_dict['g2o2_valid_hr_end_upper_air'] = (
        str(valid_hr_end_upper_air).zfill(2)
    )
    env_var_dict['g2o2_valid_hr_inc_upper_air'] = str(valid_hr_inc_upper_air)
    env_var_dict['g2o2_valid_hr_beg_conus_sfc'] = (
        str(valid_hr_beg_conus_sfc).zfill(2)
    )
    env_var_dict['g2o2_valid_hr_end_conus_sfc'] = (
        str(valid_hr_end_conus_sfc).zfill(2)
    )
    env_var_dict['g2o2_valid_hr_inc_conus_sfc'] = str(valid_hr_inc_conus_sfc)
    env_var_dict['g2o2_init_hr_beg'] = str(init_hr_beg).zfill(2)
    env_var_dict['g2o2_init_hr_end'] = str(init_hr_end).zfill(2)
    env_var_dict['g2o2_init_hr_inc'] = str(init_hr_inc).zfill(2)

elif RUN == 'precip_step1':
    fhr_min = float(os.environ['precip1_fhr_min'])
    fhr_max = float(os.environ['precip1_fhr_max'])
    fcyc_list = os.environ['precip1_fcyc_list'].split(' ')
    obtype = os.environ['precip1_obtype']
    accum_length = int(os.environ['precip1_accum_length'])
    if obtype == 'ccpa' and accum_length == 24:
        vhr_list = [ '12' ]
        obs_daily_file = 'True' 
    else:
        print("ERROR: "+obtype+" for observations with "
              "accumulation length of "+str(accum_length)+"hr is not valid")
        exit(1)

    nfcyc = len(fcyc_list)
    nvhr = len(vhr_list)
    if nfcyc > nvhr:
        fhr_intvl = int(24/nfcyc)
    else:
        fhr_intvl = int(24/nvhr)
    nfhr = fhr_max/fhr_intvl
    fhr_max = int(nfhr*fhr_intvl)
    if fhr_min < accum_length:
        fhr_min = accum_length
    fhr_min_fcyc_list = []
    if obtype == 'ccpa' and accum_length == 24:
        for fcyc in fcyc_list:
            fhr_min_fcyc = fhr_min + (12 - int(fcyc))
            if fhr_min_fcyc < accum_length:
                fhr_min_fcyc+=accum_length
            fhr_min_fcyc_list.append(fhr_min_fcyc)
    fhr_min = np.amin(np.array(fhr_min_fcyc_list)) 
    fhr_list = []
    fhr = fhr_min
    while fhr <= fhr_max:
        fhr_list.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl

    valid_hr_beg = vhr_list[0]
    valid_hr_end = vhr_list[-1]
    valid_hr_inc = int((24/nvhr)*3600)
    init_hr_beg = fcyc_list[0]
    init_hr_end = fcyc_list[-1]
    init_hr_inc = int((24/nfcyc)*3600)

    env_var_dict['precip1_fhr_list'] = ' '.join(fhr_list).replace(' ', ', ')
    env_var_dict['precip1_vhr_list'] = ' '.join(vhr_list).replace(', ', ' ')
    env_var_dict['precip1_valid_hr_beg'] = str(valid_hr_beg).zfill(2)
    env_var_dict['precip1_valid_hr_end'] = str(valid_hr_end).zfill(2)
    env_var_dict['precip1_valid_hr_inc'] = str(valid_hr_inc)
    env_var_dict['precip1_init_hr_beg'] = str(init_hr_beg).zfill(2)
    env_var_dict['precip1_init_hr_end'] = str(init_hr_end).zfill(2)
    env_var_dict['precip1_init_hr_inc'] = str(init_hr_inc)
    env_var_dict['precip1_obs_daily_file'] = obs_daily_file

with open('python_gen_env_vars.sh', 'a') as file:
    file.write('#!/bin/sh\n')
    file.write('echo BEGIN: python_gen_env_vars.sh\n')
    for name, value in env_var_dict.items():
        file.write('export '+name+'='+'"'+value+'"\n')
    file.write('echo END: python_gen_env_vars.sh')

print("END: "+os.path.basename(__file__))
