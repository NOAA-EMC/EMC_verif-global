##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Create job files
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

import sys
import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

METplus_version = os.environ['METplus_version']
PARMverif_global = os.environ['PARMverif_global']
USHMETplus = os.environ['USHMETplus']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
if RUN == 'grid2grid_step1':
    type_list = os.environ['g2g1_type_list'].split(' ')
    case = 'grid2grid'
elif RUN == 'grid2obs_step1':
    type_list = os.environ['g2o1_type_list'].split(' ')
    case = 'grid2obs'
elif RUN == 'precip_step1':
    type_list = os.environ['precip1_type_list'].split(' ')
    case = 'precip'
model_list = os.environ['model_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

def set_job_common_env(job_file):
    env_var_list = [ 'HOMEMETplus', 'HOMEMET', 'DATA', 'WGRIB2', 'NCAP2', 
                     'NCDUMP', 'CONVERT', 'METplus_verbosity', 'MET_verbosity', 
                     'log_MET_output_to_METplus', 'PARMverif_global',
                     'USHMETplus', 'FIXverif_global', 'METplus_version',
                     'MET_version' ]
    job_file.write('#!/bin/sh\n')
    for env_var in env_var_list:
        job_file.write('export '+env_var+'="'+os.environ[env_var]+'"\n')

def create_job_script_step1(sdate, edate, model_list, type_list, case):
    njob = 0
    date = sdate
    while date <= edate:
        for model in model_list:
            for type in type_list:
                njob+=1
                if case == 'grid2grid':
                    fhr_list = os.environ['g2g1_fhr_list']
                    gather_by = os.environ['g2g1_gather_by']
                    valid_hr_beg = os.environ['g2g1_valid_hr_beg']
                    valid_hr_end = os.environ['g2g1_valid_hr_end']
                    valid_hr_inc = os.environ['g2g1_valid_hr_inc']
                    init_hr_beg = os.environ['g2g1_init_hr_beg']
                    init_hr_end = os.environ['g2g1_init_hr_end']
                    init_hr_inc = os.environ['g2g1_init_hr_inc']
                    extra_env_info = {}
                    if type == 'sfc':
                        obtype = model+'_f00'
                    else:
                        if os.environ['g2g1_anl_name'] == 'self':
                            obtype = model+'_anl'
                        else:
                            obtype = os.environ['g2g1_anl_name']+'_anl'
                    extra_env_info['verif_grid'] = os.environ['g2g1_grid']
                elif case == 'grid2obs':
                    gather_by = os.environ['g2o1_gather_by']
                    init_hr_beg = os.environ['g2o1_init_hr_beg']
                    init_hr_end = os.environ['g2o1_init_hr_end']
                    init_hr_inc = os.environ['g2o1_init_hr_inc'] 
                    extra_env_info = {}
                    if type == 'upper_air':
                        fhr_list = os.environ['g2o1_fhr_list_upper_air']
                        obtype = os.environ['g2o1_obtype_upper_air']
                        valid_hr_beg = os.environ['g2o1_valid_hr_beg_upper_air']
                        valid_hr_end = os.environ['g2o1_valid_hr_end_upper_air']
                        valid_hr_inc = os.environ['g2o1_valid_hr_inc_upper_air']
                        extra_env_info['prepbufr'] = 'gdas'
                        extra_env_info['verif_grid'] = os.environ['g2o1_grid_upper_air']
                    elif type == 'conus_sfc':
                        fhr_list = os.environ['g2o1_fhr_list_conus_sfc']
                        obtype = os.environ['g2o1_obtype_conus_sfc']
                        valid_hr_beg = os.environ['g2o1_valid_hr_beg_conus_sfc']
                        valid_hr_end = os.environ['g2o1_valid_hr_end_conus_sfc']
                        valid_hr_inc = os.environ['g2o1_valid_hr_inc_conus_sfc']
                        if int(date.strftime('%Y%m%d')) > 20170319:
                            extra_env_info['prepbufr'] = 'nam'
                        else:
                            extra_env_info['prepbufr'] = 'ndas'
                        extra_env_info['verif_grid'] = os.environ['g2o1_grid_conus_sfc']
                elif case == 'precip':
                    gather_by = os.environ['precip1_gather_by']
                    fhr_list = os.environ['precip1_fhr_list']
                    obtype = os.environ['precip1_obtype']
                    valid_hr_beg = os.environ['precip1_valid_hr_beg']
                    valid_hr_end = os.environ['precip1_valid_hr_end']
                    valid_hr_inc = os.environ['precip1_valid_hr_inc']
                    init_hr_beg = os.environ['precip1_init_hr_beg']
                    init_hr_end = os.environ['precip1_init_hr_end']
                    init_hr_inc = os.environ['precip1_init_hr_inc']
                    extra_env_info = {}
                    extra_env_info['verif_grid'] = os.environ['precip1_grid']
                    model_bucket_list = os.environ['precip1_model_bucket_list'].split(' ') 
                    model_varname_list = os.environ['precip1_model_varname_list'].split(' ')
                    model_fileformat_list = os.environ['precip1_model_fileformat_list'].split(' ')
                    model_index = model_list.index(model)
                    extra_env_info['model_bucket'] = model_bucket_list[model_index]
                    extra_env_info['model_varname'] = model_varname_list[model_index]
                    extra_env_info['model_filetype'] = model_fileformat_list[model_index][0:4]
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export DATE="'+date.strftime('%Y%m%d')+'"\n')
                job_file.write('export model="'+model+'"\n')
                job_file.write('export obtype="'+obtype+'"\n')
                job_file.write('export make_met_data_by="'+make_met_data_by+'"\n')
                job_file.write('export gather_by="'+gather_by+'"\n')
                job_file.write('export fhr_list="'+fhr_list+'"\n')
                job_file.write('export valid_hr_beg="'+valid_hr_beg+'"\n')
                job_file.write('export valid_hr_end="'+valid_hr_end+'"\n')
                job_file.write('export valid_hr_inc="'+valid_hr_inc+'"\n')
                job_file.write('export init_hr_beg="'+init_hr_beg+'"\n')
                job_file.write('export init_hr_end="'+init_hr_end+'"\n')
                job_file.write('export init_hr_inc="'+init_hr_inc+'"\n')
                for name, value in extra_env_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                job_file.write(
                    USHMETplus+'/master_metplus.py ' 
                    '-c '+PARMverif_global+'/metplus_config/machine.conf '
                    '-c '+PARMverif_global+'/metplus_config/metplus_use_cases/'
                    'METplusV'+METplus_version+'/'+case+'/make_met_data_by_'
                    +make_met_data_by+'/'+type+'.conf\n'
                    )
                if case == 'grid2grid' and type == 'anom':
                    job_file.write(
                        USHMETplus+'/master_metplus.py '
                        '-c '+PARMverif_global+'/metplus_config/machine.conf '
                        '-c '+PARMverif_global+'/metplus_config/metplus_use_cases/'
                        'METplusV'+METplus_version+'/'+case+'/make_met_data_by_'
                        +make_met_data_by+'/'+type+'_height.conf\n'
                        )
                job_file.write(
                    USHMETplus+'/master_metplus.py '
                    '-c '+PARMverif_global+'/metplus_config/machine.conf '
                    '-c '+PARMverif_global+'/metplus_config/metplus_use_cases/'
                    'METplusV'+METplus_version+'/'+case+'/gather_by_'+gather_by+'/'
                    +type+'.conf')
                job_file.close()
        date = date + datetime.timedelta(days=1)

if RUN in [ 'grid2grid_step1', 'grid2obs_step1', 'precip_step1' ]:
    create_job_script_step1(sdate, edate, model_list, type_list, case)   

print("END: "+os.path.basename(__file__))
