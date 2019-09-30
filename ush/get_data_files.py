##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Get model and observation files
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

from __future__ import (print_function, division)
import os
import subprocess
import datetime
from time import sleep

print("BEGIN: "+os.path.basename(__file__))

RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
model_arch_dir_list = os.environ['model_arch_dir_list'].split(' ')
model_fileformat_list = os.environ['model_fileformat_list'].split(' ')
model_data_run_hpss = os.environ['model_data_runhpss']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
model_hpssdir_list = os.environ['model_hpssdir_list'].split(' ')
hpss_prod_base_dir = '/NCEPPROD/hpssprod/runhistory'

class TimeObj(object):
    __slots__ = 'validtime', 'inittime', 'lead'

class PrepbufrObj(object):
    __slots__ = 'prodfile', 'archfile', 'hpsstar', 'hpssfile', 'filetype' 

def get_time_info(start_date, end_date, 
                  start_hr, end_hr, hr_inc, 
                  fhr_list, make_met_data_by):
    sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), 
                              int(start_date[6:]), int(start_hr))
    edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), 
                              int(end_date[6:]), int(end_hr))
    date_inc = datetime.timedelta(seconds=int(hr_inc))

    time_info = []
    date = sdate
    while date <= edate:
        if make_met_data_by == 'VALID':
            validtime = date
        elif make_met_data_by == 'INIT':
            inittime = date
        for fhr in fhr_list:
            lead = fhr
            if make_met_data_by == 'VALID':
                inittime = validtime - datetime.timedelta(hours=int(lead))
            elif make_met_data_by == 'INIT':
                validtime = inittime + datetime.timedelta(hours=int(lead))
            to = TimeObj()
            to.validtime = validtime
            to.inittime = inittime
            to.lead = lead
            time_info.append(to)
        date = date + date_inc
    return time_info

def format_filler(file_format, valid_time, init_time, lead):
    filled_file_format = file_format
    if '{lead?fmt=' in file_format:
        lead_fmt = file_format.partition('{lead?fmt=')[2].partition('}')[0]
        filled_file_format = filled_file_format.replace(
            '{lead?fmt='+lead_fmt+'}',lead
            )
    if '{valid?fmt=' in file_format:
         valid_fmt = file_format.partition('{valid?fmt=')[2].partition('}')[0]
         filled_file_format = filled_file_format.replace(
             '{valid?fmt='+valid_fmt+'}', valid_time.strftime(valid_fmt)
             )
    if '{init?fmt=' in file_format:
         init_fmt = file_format.partition('{init?fmt=')[2].partition('}')[0]
         filled_file_format = filled_file_format.replace(
             '{init?fmt='+init_fmt+'}', init_time.strftime(init_fmt)
             )
    if '{cycle?fmt=' in file_format:
         cycle_fmt = file_format.partition('{cycle?fmt=')[2].partition('}')[0]
         filled_file_format = filled_file_format.replace(
             '{cycle?fmt='+cycle_fmt+'}', init_time.strftime(cycle_fmt)
             )
    return filled_file_format

def get_hpss_data(hpss_job_filename,
                  link_data_dir, link_data_file,
                  hpss_tar, hpss_file):
    htar = os.environ['HTAR']
    hpss_walltime = os.environ['hpss_walltime']
    machine = os.environ['machine']
    queueserv = os.environ['QUEUESERV']
    account = os.environ['ACCOUNT']
    walltime_seconds = datetime.timedelta(minutes=int(hpss_walltime)) \
        .total_seconds()
    walltime = (datetime.datetime.min 
                + datetime.timedelta(minutes=int(hpss_walltime))).time()
    with open(hpss_job_filename, 'a') as hpss_job_file:
        hpss_job_file.write('#!/bin/sh'+'\n')
        hpss_job_file.write('cd '+link_data_dir+'\n')
        hpss_job_file.write(htar+' -xf '+hpss_tar+' ./'+hpss_file+'\n')
        if hpss_file[0:4] == 'gfs.':
            cnvgrib = os.environ['CNVGRIB']
            hpss_job_file.write(cnvgrib+' -g21 '+hpss_file+' '
                                +link_data_file+' > /dev/null 2>&1\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
        else:
            if hpss_file[0:5] != 'ccpa.':
                hpss_job_file.write('cp '+hpss_file+' '+link_data_file+'\n')
                hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
    os.chmod(hpss_job_filename, 0o755)
    hpss_job_output = hpss_job_filename.replace('.sh', '.out')
    hpss_job_name = hpss_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+hpss_job_filename+" to "+queueserv)
    print("Output sent to "+hpss_job_output)
    if machine == 'WCOSS_C':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+queueserv+' '
                  '-P '+account+' -o '+hpss_job_output+' -e '+hpss_job_output+' '
                  '-J '+hpss_job_name+' -R rusage[mem=2048] '+hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         '-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'WCOSS_DELL_P3':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+queueserv+' '
                  '-P '+account+' -o '+hpss_job_output+' -e '+hpss_job_output+' '
                  '-J '+hpss_job_name+' -M 2048 -R "affinity[core(1)]" '+hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         '-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'THEIA' or machine == 'HERA':
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  '--partition='+queueserv+' --account='+account+' '
                  '--output='+hpss_job_output+' '
                  '--job-name='+hpss_job_name+' '+hpss_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +hpss_job_name+' -t R,PD -h | wc -l')
    sleep_counter, sleep_checker = 1, 10
    while (sleep_counter*sleep_checker) <= walltime_seconds:
        sleep(sleep_checker)
        print("Walltime checker: "+str(sleep_counter*sleep_checker)+" "
              "out of "+str(int(walltime_seconds))+" seconds")
        check_job = subprocess.check_output(job_check_cmd, shell=True)
        if check_job[0] == '0':
            break
        sleep_counter+=1

def set_up_gfs_hpss_info(init_time, hpss_dir, hpss_file_suffix,
                         link_data_dir):
    YYYYmmddHH = init_time.strftime('%Y%m%d%H')
    YYYYmmdd = init_time.strftime('%Y%m%d')
    YYYYmm = init_time.strftime('%Y%m')
    YYYY = init_time.strftime('%Y')
    mm = init_time.strftime('%m')
    dd = init_time.strftime('%d')
    HH = init_time.strftime('%H')
    hpss_file = 'gfs.t'+HH+'z.pgrb2.0p25.'+hpss_file_suffix
    if 'NCEPPROD' in hpss_dir:
        hpss_date_dir = os.path.join(hpss_dir, 'rh'+YYYY, YYYYmm,
                                     YYYYmmdd)
        if int(YYYYmmdd) >= 20190612:
            hpss_tar = os.path.join(hpss_date_dir,
                                    'gpfs_dell1_nco_ops_com_gfs_prod_gfs.'
                                    +YYYYmmdd+'_'+HH+'.gfs_pgrb2.tar')
            hpss_file = (
                'gfs.'+YYYYmmdd+'/'+HH+'/gfs.t'+HH
                +'z.pgrb2.0p25.'+hpss_file_suffix
                )
        elif int(YYYYmmdd) >= 20170720 and int(YYYYmmdd) < 20190612:
            hpss_tar = os.path.join(hpss_date_dir, 
                                    'gpfs_hps_nco_ops_com_gfs_prod_gfs.'
                                    +YYYYmmddHH+'.pgrb2_0p25.tar')
            hpss_file = 'gfs.t'+HH+'z.pgrb2.0p25.'+hpss_file_suffix
        elif int(YYYYmmdd) >= 20160510 and int(YYYYmmdd) < 20170720:
            hpss_tar = os.path.join(hpss_date_dir,
                                    'com2_gfs_prod_gfs.'
                                    +YYYYmmddHH+'.pgrb2_0p25.tar')
            hpss_file = 'gfs.t'+HH+'z.pgrb2.0p25.'+hpss_file_suffix
        else:
            hpss_tar = os.path.join(hpss_date_dir,
                                    'com_gfs_prod_gfs.'
                                    +YYYYmmddHH+'.pgrb2_0p25.tar')
            hpss_file = 'gfs.t'+HH+'z.pgrb2.0p25.'+hpss_file_suffix
    else:
        hpss_tar = os.path.join(hpss_dir, name, YYYYmmddHH, 'gfsa.tar')
        hpss_file = 'gfs.t'+HH+'z.pgrb2.0p25.'+hpss_file_suffix
    hpss_job_filename = os.path.join(
        link_data_dir, 'HPSS_jobs', 'HPSS_'+hpss_tar.rpartition('/')[2]
        +'_'+hpss_file.replace('/', '_')+'.sh'
        )
    return hpss_tar, hpss_file, hpss_job_filename

def convert_grib2_grib1(grib2_file, grib1_file):
    print("Converting GRIB2 file "+grib2_file
          +" to GRIB1 file "+grib1_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g21 '+grib2_file+' '
              +grib1_file+' > /dev/null 2>&1')

if RUN == 'grid2grid_step1':
    anl_name = os.environ['g2g1_anl_name']
    anl_file_format_list = os.environ['g2g1_anl_fileformat_list'].split(' ')
    if make_met_data_by == 'VALID':
        start_hr = os.environ['g2g1_valid_hr_beg']
        end_hr = os.environ['g2g1_valid_hr_end']
        hr_inc = os.environ['g2g1_valid_hr_inc']
    else:
        start_hr = os.environ['g2g1_init_hr_beg']
        end_hr = os.environ['g2g1_init_hr_end']
        hr_inc = os.environ['g2g1_init_hr_inc']
    fhr_list = os.environ['g2g1_fhr_list'].split(', ')
    type_list = os.environ['g2g1_type_list'].split(' ')

    time_info = get_time_info(start_date, end_date, 
                              start_hr, end_hr, hr_inc, 
                              fhr_list, make_met_data_by)

    cwd = os.getcwd()
    for name in model_list:
        index = model_list.index(name)
        dir = model_dir_list[index]
        file_format = model_fileformat_list[index]
        hpss_dir = model_hpssdir_list[index]
        link_model_data_dir = os.path.join(cwd, 'data', name)
        if not os.path.exists(link_model_data_dir):
            os.makedirs(link_model_data_dir)
            os.makedirs(link_model_data_dir+'/HPSS_jobs')
        for time in time_info:
            valid_time = time.validtime
            init_time = time.inittime
            lead = time.lead
            if init_time.strftime('%H') in [ '03', '09', '15', '21' ]:
                continue
            else:
                link_model_forecast_file = os.path.join(
                    link_model_data_dir, 
                    'f'+lead+'.'+init_time.strftime('%Y%m%d%H')
                    )
                if not os.path.exists(link_model_forecast_file):
                    model_forecast_filename = format_filler(file_format,
                                                            valid_time, 
                                                            init_time, lead)
                    model_forecast_file = os.path.join(dir, name,
                                                       model_forecast_filename)
                    if os.path.exists(model_forecast_file):
                        if "grib2" in model_forecast_file:
                            convert_grib2_grib1(model_forecast_file, 
                                                link_model_forecast_file)
                        else:
                            os.system('ln -sf '+model_forecast_file+' '
                                      +link_model_forecast_file)
                    else:
                        if model_data_run_hpss == 'YES':
                            print("Did not find "+model_forecast_file+" "
                                  "online...going to try to get file from HPSS")
                            hpss_tar, hpss_file, hpss_job_filename = (
                                set_up_gfs_hpss_info(init_time, hpss_dir, 
                                                     'f'+lead.zfill(3), 
                                                     link_model_data_dir)
                                )
                            get_hpss_data(hpss_job_filename,
                                          link_model_data_dir, 
                                          link_model_forecast_file,
                                          hpss_tar, hpss_file)
                    if not os.path.exists(link_model_forecast_file):
                        if model_data_run_hpss == 'YES':
                            print("WARNING: "+model_forecast_file+" "
                                  "does not exist and did not find "
                                  "HPSS file "+hpss_file+" from "+hpss_tar+" "
                                  "or walltime exceeded")
                        else:
                            print("WARNING: "+model_forecast_file
                                  +" does not exist")

    valid_time_list = []
    for time in time_info:
        valid_time = time.validtime
        if valid_time not in valid_time_list:
            valid_time_list.append(valid_time)
    for name in model_list:
        index = model_list.index(name)
        dir = model_dir_list[index]
        if 'gfs' in anl_name or len(anl_file_format_list) == 1:
            anl_file_format = anl_file_format_list[0]
        else:
            anl_file_format = anl_file_format_list[index]
        hpss_dir = model_hpssdir_list[index]
        link_model_data_dir = os.path.join(cwd, 'data', name)
        if not os.path.exists(link_model_data_dir):
            os.makedirs(link_model_data_dir)
            os.makedirs(link_model_data_dir+'/HPSS_jobs')
        for valid_time in valid_time_list:
            link_anl_file = os.path.join(
                link_model_data_dir,
                'anl.'+valid_time.strftime('%Y%m%d%H')
                )
            if not os.path.exists(link_anl_file):
                anl_filename = format_filler(anl_file_format,
                                             valid_time, 
                                             init_time, lead)
                if anl_name == 'self_anl' or anl_name == 'self_f00':
                    anl_dir = os.path.join(dir, name)
                elif anl_name == 'gfs_anl' or anl_name == 'gfs_f00':
                    anl_dir = os.path.join(os.environ['gstat'], 'gfs')
                else:
                    print("ERROR: "+anl_name+" is not a valid option "
                          "for g2g1_anl_name")
                    exit(1)
                anl_file = os.path.join(anl_dir, anl_filename)
                if os.path.exists(anl_file):
                    anl_found = True
                    if "grib2" in anl_file:
                            convert_grib2_grib1(anl_file,
                                                link_anl_file) 
                    else:
                        os.system('ln -sf '+anl_file+' '+link_anl_file)
                else:
                    if model_data_run_hpss == 'YES':
                        print("Did not find "+anl_file+" "
                              "online...going to try to get file from HPSS")
                        if 'self' in anl_name:
                            hpss_dir = hpss_dir
                        elif 'gfs' in anl_name:
                            hpss_dir = '/NCEPPROD/hpssprod/runhistory'
                        hpss_tar, hpss_file, hpss_job_filename = (
                                set_up_gfs_hpss_info(init_time, hpss_dir, 
                                                     'anl', 
                                                     link_model_data_dir)
                                )
                        get_hpss_data(hpss_job_filename,
                                      link_model_data_dir, link_anl_file,
                                      hpss_tar, hpss_file)
                    else:
                        anl_found = False 
                if not os.path.exists(link_anl_file):
                     if model_data_run_hpss == 'YES':
                         error_msg = ('WARNING: '+anl_file+' does not exist '
                                      'and did not find HPSS file '
                                      +hpss_file+' from '+hpss_tar+' or '
                                      'walltime exceeded')
                     else:
                         error_msg = 'WARNING: '+anl_file+' does not exist'
                     print(error_msg)
                     anl_found = False
                     error_dir = os.path.join(link_model_data_dir)
                     error_file = os.path.join(
                         error_dir,
                         'error_anl_'+valid_time.strftime('%Y%m%d%H%M')+'.txt'
                         )
                     if not os.path.exists(error_file):
                         with open(error_file, 'a') as file:
                             file.write(error_msg)
                else:
                     anl_found = True
                if anl_found == False:
                     print("Analysis file not found..."
                           +"will try to link f00 instead")
                     link_f00_file = os.path.join(
                         link_model_data_dir,
                         'f00.'+valid_time.strftime('%Y%m%d%H')
                     )
                     if os.path.exists(link_f00_file):
                         os.system('ln -sf '+link_f00_file+' '+link_anl_file)
                     else:
                         f00_filename = format_filler(file_format,
                                                      valid_time, valid_time,
                                                      '00')
                         f00_file = os.path.join(dir, name,
                                                 f00_filename)
                         if os.path.exists(f00_file):
                             if "grib2" in f00_file:
                                 convert_grib2_grib1(f00_file,
                                                     link_anl_file)
                                 convert_grib2_grib1(f00_file,
                                                     link_f00_file)
                             else:
                                 os.system('ln -sf '+f00_file
                                           +' '+link_anl_file)
                                 os.system('ln -sf '+f00_file
                                           +' '+link_f00_file)
                         else:
                             if model_data_run_hpss == 'YES':
                                 hpss_tar, hpss_file, hpss_job_filename = (
                                     set_up_gfs_hpss_info(init_time, hpss_dir,
                                                          'f000',
                                                           link_model_data_dir)
                                 )
                                 get_hpss_data(hpss_job_filename,
                                               link_model_data_dir,
                                               link_anl_file,
                                               hpss_tar, hpss_file)
                                 if os.path.exists(link_anl_file):
                                     os.system('ln -sf '+link_anl_file
                                               +' '+link_f00_file)
                         if not os.path.exists(link_anl_file):
                             print("Unable to link f00 file as analysis")

            if 'sfc' in type_list:
                link_f00_file = os.path.join(
                    link_model_data_dir,
                    'f00.'+valid_time.strftime('%Y%m%d%H')
                    )
                if not os.path.exists(link_f00_file):
                    f00_filename = format_filler(file_format,
                                                 valid_time, valid_time, '00')
                    f00_file = os.path.join(dir, name,
                                            f00_filename)
                    if os.path.exists(f00_file):
                        if "grib2" in f00_file:
                            convert_grib2_grib1(f00_file,
                                                link_f00_file)
                        else:  
                            os.system('ln -sf '+f00_file+' '+link_f00_file)
                    else:
                        if model_data_run_hpss == 'YES':
                            print("Did not find "+f00_file+" "
                                  "online...going to try to get file from HPSS")
                            hpss_tar, hpss_file, hpss_job_filename = (
                                set_up_gfs_hpss_info(init_time, hpss_dir, 
                                                     'f000', 
                                                     link_model_data_dir)
                                )
                            get_hpss_data(hpss_job_filename,
                                          link_model_data_dir, link_f00_file,
                                          hpss_tar, hpss_file)
                    if not os.path.exists(link_f00_file):
                        if model_data_run_hpss == 'YES':
                           error_msg = ('WARNING: '+f00_file+' does not exist '
                                        'and did not find HPSS file '
                                        +hpss_file+' from '+hpss_tar+' or '
                                        'walltime exceeded')
                        else:
                            error_msg = 'WARNING: '+f00_file+' does not exist'
                        print(error_msg)
                        error_dir = os.path.join(link_model_data_dir)
                        error_file = os.path.join(
                            error_dir,
                            'error_f00_'+valid_time.strftime('%Y%m%d%H%M')+'.txt'
                            )
                        if not os.path.exists(error_file):
                            with open(error_file, 'a') as file:
                                file.write(error_msg)

elif RUN == 'grid2grid_step2':
    type_list = os.environ['g2g2_type_list'].split(' ')
    gather_by_list = os.environ['g2g2_gather_by_list'].split(' ')
    if plot_by == 'VALID':
        start_hr = os.environ['g2g2_valid_hr_beg']
        end_hr = os.environ['g2g2_valid_hr_end']
        hr_inc = os.environ['g2g2_valid_hr_inc']
    else:
        start_hr = os.environ['g2g2_init_hr_beg']
        end_hr = os.environ['g2g2_init_hr_end']
        hr_inc = os.environ['g2g2_init_hr_inc']
    fhr_list = os.environ['g2g2_fhr_list'].split(', ')
   
    time_info = get_time_info(start_date, end_date,
                              start_hr, end_hr, hr_inc,
                              fhr_list, plot_by)

    cwd = os.getcwd()
    for name in model_list:
        index = model_list.index(name)
        if len(model_arch_dir_list) != len(model_list):
            arch_dir = model_arch_dir_list[0]
        else:
            arch_dir = model_arch_dir_list[index]
        if len(gather_by_list) != len(model_list):
            gather_by = gather_by_list[0]
        else:
            gather_by = gather_by_list[index]
        for type in type_list:
            full_arch_dir = os.path.join(arch_dir, 'metplus_data', 
                                         'by_'+gather_by, 'grid2grid',
                                          type)
            link_model_data_dir = os.path.join(cwd, 'data', name, type)
            if not os.path.exists(link_model_data_dir):
                os.makedirs(link_model_data_dir)
            for time in time_info:
                valid_time = time.validtime
                init_time = time.inittime
                lead = time.lead
                if gather_by == 'VALID' or gather_by == 'VSDB':
                    stat_file = os.path.join(full_arch_dir, 
                                             valid_time.strftime('%H')+'Z', 
                                             name, 
                                             name+'_'+valid_time.strftime('%Y%m%d')+'.stat')
                    link_stat_file = os.path.join(link_model_data_dir, 
                                                  name+'_valid'+valid_time.strftime('%Y%m%d')+
                                                  '_valid'+valid_time.strftime('%H')+'.stat')
                elif gather_by == 'INIT':
                    stat_file = os.path.join(full_arch_dir, 
                                             init_time.strftime('%H')+'Z', 
                                             name, 
                                             name+'_'+init_time.strftime('%Y%m%d')+'.stat')
                    link_stat_file = os.path.join(link_model_data_dir, 
                                                  name+'_init'+init_time.strftime('%Y%m%d')+
                                                  '_init'+init_time.strftime('%H')+'.stat')
                if not os.path.exists(link_stat_file):
                    if os.path.exists(stat_file):
                        os.system('ln -sf '+stat_file+' '
                                  +link_stat_file)
                    else:
                        print("WARNING: "+stat_file
                              +" does not exist")
 
elif RUN == 'grid2obs_step1':
    type_list = os.environ['g2o1_type_list'].split(' ')
    prepbufr_prod_upper_air_dir = os.environ['prepbufr_prod_upper_air_dir']
    prepbufr_prod_conus_sfc_dir = os.environ['prepbufr_prod_conus_sfc_dir']
    prepbufr_arch_dir = os.environ['prepbufr_arch_dir']
    prepbufr_run_hpss = os.environ['prepbufr_data_runhpss']
    for type in type_list:
        fhr_list_type = os.environ['g2o1_fhr_list_'+type].split(', ')
        if make_met_data_by == 'VALID':
            start_hr_type = os.environ['g2o1_valid_hr_beg_'+type]
            end_hr_type = os.environ['g2o1_valid_hr_end_'+type]
            hr_inc_type = os.environ['g2o1_valid_hr_inc_'+type]
        else:
            start_hr_type = os.environ['g2o1_init_hr_beg']
            end_hr_type = os.environ['g2o1_init_hr_end']
            hr_inc_type = os.environ['g2o1_init_hr_inc'] 
        time_info = get_time_info(start_date, end_date,
                                  start_hr_type, end_hr_type, hr_inc_type,
                                  fhr_list_type, make_met_data_by)

        cwd = os.getcwd()
        for name in model_list:
            index = model_list.index(name)
            dir = model_dir_list[index]
            file_format = model_fileformat_list[index]
            hpss_dir = model_hpssdir_list[index]
            link_model_data_dir = os.path.join(cwd, 'data', name)
            if not os.path.exists(link_model_data_dir):
                os.makedirs(link_model_data_dir)
                os.makedirs(link_model_data_dir+'/HPSS_jobs')
            for time in time_info:
                valid_time = time.validtime
                init_time = time.inittime
                lead = time.lead
                if init_time.strftime('%H') in [ '03', '09', '15', '21' ]:
                    continue
                else:
                    link_model_forecast_file = os.path.join(
                        link_model_data_dir,
                        'f'+lead+'.'+init_time.strftime('%Y%m%d%H')
                        )
                    if not os.path.exists(link_model_forecast_file):
                        model_forecast_filename = format_filler(file_format,
                                                                valid_time, 
                                                                init_time, 
                                                                lead)
                        model_forecast_file = os.path.join(
                            dir, name, model_forecast_filename
                            )
                        if os.path.exists(model_forecast_file):
                            if "grib2" in model_forecast_file:
                                convert_grib2_grib1(model_forecast_file,
                                                    link_model_forecast_file)
                            else:
                                os.system('ln -sf '+model_forecast_file+' '
                                          +link_model_forecast_file)
                        else:
                            if model_data_run_hpss == 'YES':
                                print("Did not find "
                                      +model_forecast_file+" online..."
                                      "going to try to get file from HPSS")
                                hpss_tar, hpss_file, hpss_job_filename = (
                                set_up_gfs_hpss_info(init_time, hpss_dir, 
                                                     'f'+lead.zfill(3), 
                                                     link_model_data_dir)
                                )
                                get_hpss_data(hpss_job_filename,
                                              link_model_data_dir, 
                                              link_model_forecast_file,
                                              hpss_tar, hpss_file)
                        if not os.path.exists(link_model_forecast_file):
                            if model_data_run_hpss == 'YES':
                                print("WARNING: "+model_forecast_file+" does "
                                      "not exist and did not find HPSS file "
                                      +hpss_file+" from "+hpss_tar+" "
                                      " or walltime exceeded")
                            else:
                                print("WARNING: "+model_forecast_file
                                      +" does not exist")

        valid_time_list = []
        for time in time_info:
            valid_time = time.validtime
            if valid_time not in valid_time_list:
                valid_time_list.append(valid_time)
        for valid_time in valid_time_list:
            prepbufr_files_to_check = []
            YYYYmmddHH = valid_time.strftime('%Y%m%d%H')
            YYYYmmdd = valid_time.strftime('%Y%m%d')
            YYYYmm = valid_time.strftime('%Y%m')
            YYYY = valid_time.strftime('%Y')
            mm = valid_time.strftime('%m')
            dd = valid_time.strftime('%d')
            HH = valid_time.strftime('%H')
            if type == 'upper_air':
                link_prepbufr_data_dir = os.path.join(cwd, 'data',
                                                      'prepbufr')
                link_prepbufr_file = os.path.join(link_prepbufr_data_dir,
                                                  'prepbufr.gdas.'+YYYYmmddHH)
                prod_file = os.path.join(prepbufr_prod_upper_air_dir, 
                                         'gdas.'+YYYYmmdd, HH,
                                         'gdas.t'+HH+'z.prepbufr')
                arch_file = os.path.join(prepbufr_arch_dir, 'gdas',
                                          'prepbufr.gdas.'+YYYYmmddHH)
                hpss_date_dir = os.path.join(hpss_prod_base_dir,
                                             'rh'+YYYY, YYYYmm,
                                             YYYYmmdd)
                if int(YYYYmmdd) >= 20190612:
                    hpss_tar_file = (
                        'gpfs_dell1_nco_ops_com_gfs_prod_gdas.'
                        +YYYYmmdd+'_'+HH+'.gdas.tar'
                        )
                    hpss_file = 'gdas.'+YYYYmmdd+'/'+HH+'/gdas.t'+HH+'z.prepbufr'
                elif int(YYYYmmdd) >= 20170720 and int(YYYYmmdd) < 20190612:
                    hpss_tar_file = (
                        'gpfs_hps_nco_ops_com_gfs_prod_gdas.'
                        +YYYYmmddHH+'.tar'
                        )
                    hpss_file = 'gdas.t'+HH+'z.prepbufr'
                elif int(YYYYmmdd) >= 20160510 and int(YYYYmmdd) < 20170720:
                    hpss_tar_file = 'com2_gfs_prod_gdas.'+YYYYmmddHH+'.tar'
                    hpss_file = 'gdas1.t'+HH+'z.prepbufr'
                else:
                    hpss_tar_file = 'com_gfs_prod_gdas.'+YYYYmmddHH+'.tar'
                    hpss_file = 'gdas1.t'+HH+'z.prepbufr'
                hpss_tar = os.path.join(hpss_date_dir, hpss_tar_file)
                pbo = PrepbufrObj()
                pbo.prodfile = prod_file
                pbo.archfile = arch_file
                pbo.hpsstar = hpss_tar
                pbo.hpssfile = hpss_file
                pbo.filetype = 'gdas'
                prepbufr_files_to_check.append(pbo)
            elif type == 'conus_sfc':
               if int(YYYYmmdd) > 20170319:
                   link_prepbufr_data_dir = os.path.join(cwd, 'data',
                                                         'prepbufr')
                   link_prepbufr_file = os.path.join(link_prepbufr_data_dir,
                                                     'prepbufr.nam.'+YYYYmmddHH)
                   offset_hr = str(int(HH)%6).zfill(2)
                   offset_time = (
                       valid_time 
                       + datetime.timedelta(hours=int(offset_hr))
                       )
                   offset_YYYYmmddHH = offset_time.strftime('%Y%m%d%H')
                   offset_YYYYmmdd = offset_time.strftime('%Y%m%d')
                   offset_YYYYmm = offset_time.strftime('%Y%m')
                   offset_YYYY = offset_time.strftime('%Y')
                   offset_mm = offset_time.strftime('%m')
                   offset_dd = offset_time.strftime('%d')
                   offset_HH = offset_time.strftime('%H')
                   prod_file = os.path.join(prepbufr_prod_conus_sfc_dir,
                                            'nam.'+offset_YYYYmmdd,
                                            'nam.t'+offset_HH
                                            +'z.prepbufr.tm'+offset_hr)
                   arch_file = os.path.join(prepbufr_arch_dir, 'nam',
                                            'nam.'+offset_YYYYmmdd,
                                            'nam.t'+offset_HH+'z.prepbufr.tm'+offset_hr)
                   hpss_date_dir = os.path.join(hpss_prod_base_dir,
                                                'rh'+offset_YYYY, offset_YYYYmm,
                                                 offset_YYYYmmdd)
                   if int(offset_YYYYmmdd) > 20190820:
                       hpss_tar_file = (
                           'gpfs_dell1_nco_ops_com_nam_prod_nam.'
                           +offset_YYYYmmddHH+'.bufr.tar'
                       )
                       hpss_file = 'nam.t'+offset_HH+'z.prepbufr.tm'+offset_hr
                   elif int(offset_YYYYmmdd) == 20170320:
                       hpss_tar_file = 'com_nam_prod_nam.'+offset_YYYYmmddHH+'.bufr.tar'
                       hpss_file = 'nam.t'+offset_HH+'z.prepbufr.tm'+offset_hr
                   else:
                       hpss_tar_file = 'com2_nam_prod_nam.'+offset_YYYYmmddHH+'.bufr.tar'
                       hpss_file = 'nam.t'+offset_HH+'z.prepbufr.tm'+offset_hr
                   hpss_tar = os.path.join(hpss_date_dir, hpss_tar_file)
                   pbo = PrepbufrObj()
                   pbo.prodfile = prod_file
                   pbo.archfile = arch_file
                   pbo.hpsstar = hpss_tar
                   pbo.hpssfile = hpss_file
                   pbo.filetype = 'nam'
                   prepbufr_files_to_check.append(pbo)
               else:
                   link_prepbufr_data_dir = os.path.join(cwd, 'data',
                                                         'prepbufr')
                   link_prepbufr_file = os.path.join(link_prepbufr_data_dir,
                                                     'prepbufr.ndas.'+YYYYmmddHH)
                   ndas_prepbufr_dict = {}
                   for xhr in [ '00', '03', '06', '09', '12', '15', '18', '21' ]:
                       xdate = valid_time + datetime.timedelta(hours=int(xhr))
                       ndas_prepbufr_dict['YYYY'+xhr] = xdate.strftime('%Y')
                       ndas_prepbufr_dict['YYYYmm'+xhr] = xdate.strftime('%Y%m')
                       ndas_prepbufr_dict['YYYYmmdd'+xhr] = xdate.strftime('%Y%m%d')
                       ndas_prepbufr_dict['HH'+xhr] = xdate.strftime('%H')
                   if ndas_prepbufr_dict['HH00'] in [ '00', '06', '12', '18']:
                       prod_file1 = os.path.join(
                           prepbufr_prod_conus_sfc_dir,
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd12'],
                           'ndas.t'+ndas_prepbufr_dict['HH12']
                           +'z.prepbufr.tm12'
                           )
                       prod_file2 = os.path.join(
                           prepbufr_prod_conus_sfc_dir,
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd06'],
                           'ndas.t'+ndas_prepbufr_dict['HH06']
                           +'z.prepbufr.tm06'
                           )
                       prod_file3 = os.path.join(
                           prepbufr_prod_conus_sfc_dir,
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd00'],
                           'nam.t'+ndas_prepbufr_dict['HH00']
                           +'z.prepbufr.tm00'
                           )
                       arch_file1 = os.path.join(
                           prepbufr_arch_dir, 'ndas',
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd12'],
                           'ndas.t'+ndas_prepbufr_dict['HH12']
                           +'z.prepbufr.tm12'
                           )
                       arch_file2 = os.path.join(
                           prepbufr_arch_dir, 'ndas',
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd06'],
                           'ndas.t'+ndas_prepbufr_dict['HH06']
                           +'z.prepbufr.tm06'
                           )
                       arch_file3 = os.path.join(
                           prepbufr_arch_dir, 'ndas',
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd00'],
                           'nam.t'+ndas_prepbufr_dict['HH00']
                           +'z.prepbufr.tm00'
                           )
                       hpss_tar1 = os.path.join(
                           hpss_prod_base_dir, 'rh'+ndas_prepbufr_dict['YYYY12'],
                           ndas_prepbufr_dict['YYYYmm12'], 
                           ndas_prepbufr_dict['YYYYmmdd12'],
                           'com_nam_prod_ndas.'
                           +ndas_prepbufr_dict['YYYYmmdd12']
                           +ndas_prepbufr_dict['HH12']+'.bufr.tar'
                           )
                       hpss_tar2 = os.path.join(
                           hpss_prod_base_dir, 'rh'+ndas_prepbufr_dict['YYYY06'],
                           ndas_prepbufr_dict['YYYYmm06'],
                           ndas_prepbufr_dict['YYYYmmdd06'],
                           'com_nam_prod_ndas.'
                           +ndas_prepbufr_dict['YYYYmmdd06']
                           +ndas_prepbufr_dict['HH06']+'.bufr.tar'
                           )
                       hpss_tar3 = os.path.join(
                           hpss_prod_base_dir, 'rh'+ndas_prepbufr_dict['YYYY00'],
                           ndas_prepbufr_dict['YYYYmm00'],
                           ndas_prepbufr_dict['YYYYmmdd00'],
                           'com_nam_prod_nam.'+ndas_prepbufr_dict['YYYYmmdd00']
                           +ndas_prepbufr_dict['HH00']+'.bufr.tar'
                           )
                       hpss_file1 = (
                           'ndas.t'+ndas_prepbufr_dict['HH12']
                           +'z.prepbufr.tm12'
                           )
                       hpss_file2 = (
                           'ndas.t'+ndas_prepbufr_dict['HH06']
                           +'z.prepbufr.tm06'
                           )
                       hpss_file3 = (
                           'nam.t'+ndas_prepbufr_dict['HH00']
                           +'z.prepbufr.tm00'
                           )
                       pbo1 = PrepbufrObj()
                       pbo1.prodfile = prod_file1
                       pbo1.archfile = arch_file1
                       pbo1.hpsstar = hpss_tar1
                       pbo1.hpssfile = hpss_file1
                       pbo1.filetype = 'ndas'
                       prepbufr_files_to_check.append(pbo1)
                       pbo2 = PrepbufrObj()
                       pbo2.prodfile = prod_file2
                       pbo2.archfile = arch_file2
                       pbo2.hpsstar = hpss_tar2
                       pbo2.hpssfile = hpss_file2
                       pbo2.filetype = 'ndas'
                       prepbufr_files_to_check.append(pbo2)
                       pbo3 = PrepbufrObj()
                       pbo3.prodfile = prod_file3
                       pbo3.archfile = arch_file3
                       pbo3.hpsstar = hpss_tar3
                       pbo3.hpssfile = hpss_file3
                       pbo3.filetype = 'nam'
                       prepbufr_files_to_check.append(pbo3)
                   elif ndas_prepbufr_dict['HH00'] in [ '03', '09', '15', '21' ]:
                       prod_file1 = os.path.join(
                           prepbufr_prod_conus_sfc_dir,
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd09'],
                           'ndas.t'+ndas_prepbufr_dict['HH09']
                           +'z.prepbufr.tm09'
                           )
                       prod_file2 = os.path.join(
                           prepbufr_prod_conus_sfc_dir,
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd03'],
                           'ndas.t'+ndas_prepbufr_dict['HH03']
                           +'z.prepbufr.tm03'
                           )
                       arch_file1 = os.path.join(
                           prepbufr_arch_dir, 'ndas',
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd09'],
                           'ndas.t'+ndas_prepbufr_dict['HH09']
                           +'z.prepbufr.tm09'
                           )
                       arch_file2 = os.path.join(
                           prepbufr_arch_dir, 'ndas',
                           'ndas.'+ndas_prepbufr_dict['YYYYmmdd03'],
                           'ndas.t'+ndas_prepbufr_dict['HH03']
                           +'z.prepbufr.tm03'
                           )
                       hpss_tar1 = os.path.join(
                           hpss_prod_base_dir, 'rh'+ndas_prepbufr_dict['YYYY09'],
                           ndas_prepbufr_dict['YYYYmm09'],
                           ndas_prepbufr_dict['YYYYmmdd09'],
                           'com_nam_prod_ndas.'
                           +ndas_prepbufr_dict['YYYYmmdd09']
                           +ndas_prepbufr_dict['HH09']+'.bufr.tar'
                           )
                       hpss_tar2 = os.path.join(
                           hpss_prod_base_dir, 'rh'+ndas_prepbufr_dict['YYYY03'],
                           ndas_prepbufr_dict['YYYYmm03'],
                           ndas_prepbufr_dict['YYYYmmdd03'],
                           'com_nam_prod_ndas.'
                           +ndas_prepbufr_dict['YYYYmmdd03']
                           +ndas_prepbufr_dict['HH03']+'.bufr.tar'
                           )
                       hpss_file1 = (
                           'ndas.t'+ndas_prepbufr_dict['HH09']
                           +'z.prepbufr.tm09'
                           )
                       hpss_file2 = (
                           'ndas.t'+ndas_prepbufr_dict['HH03']
                           +'z.prepbufr.tm03'
                           )
                       pbo1 = PrepbufrObj()
                       pbo1.prodfile = prod_file1
                       pbo1.archfile = arch_file1
                       pbo1.hpsstar = hpss_tar1
                       pbo1.hpssfile = hpss_file1
                       pbo1.filetype = 'ndas'
                       prepbufr_files_to_check.append(pbo1)
                       pbo2 = PrepbufrObj()
                       pbo2.prodfile = prod_file2
                       pbo2.archfile = arch_file2
                       pbo2.hpsstar = hpss_tar2
                       pbo2.hpssfile = hpss_file2
                       pbo2.filetype = 'ndas'
                       prepbufr_files_to_check.append(pbo2)
            if not os.path.exists(link_prepbufr_data_dir):
                os.makedirs(link_prepbufr_data_dir)
                os.makedirs(link_prepbufr_data_dir+'/HPSS_jobs')
            if not os.path.exists(link_prepbufr_file):
                for prepbufr_file_group in prepbufr_files_to_check:
                    prod_file = prepbufr_file_group.prodfile
                    arch_file = prepbufr_file_group.archfile    
                    hpss_tar = prepbufr_file_group.hpsstar
                    hpss_file = prepbufr_file_group.hpssfile
                    file_type = prepbufr_file_group.filetype
                    if os.path.exists(prod_file):
                        os.system('ln -sf '+prod_file+' '+link_prepbufr_file)
                    elif os.path.exists(arch_file):
                        os.system('ln -sf '+arch_file+' '+link_prepbufr_file)
                    else:
                        if prepbufr_run_hpss == 'YES':
                            print("Did not find "+prod_file+" or "
                                  +arch_file+" online...going to try "
                                  "to get file from HPSS")
                            hpss_job_filename = os.path.join(
                                  link_prepbufr_data_dir,
                                  'HPSS_jobs', 'HPSS_'
                                  +hpss_tar.rpartition('/')[2]
                                  +'_'+hpss_file.replace('/', '_')+'.sh'
                                  )
                            get_hpss_data(hpss_job_filename,
                                          link_prepbufr_data_dir, 
                                          link_prepbufr_file,
                                          hpss_tar, hpss_file)
                    if os.path.exists(link_prepbufr_file):
                        break
            if not os.path.exists(link_prepbufr_file):
                error_dir = os.path.join(link_prepbufr_data_dir)
                error_file = os.path.join(
                    error_dir,
                    'error_'+valid_time.strftime('%Y%m%d%H%M')+'.txt'
                    )
                for prepbufr_file_group in prepbufr_files_to_check:
                    prod_file = prepbufr_file_group.prodfile
                    arch_file = prepbufr_file_group.archfile
                    hpss_tar = prepbufr_file_group.hpsstar
                    hpss_file = prepbufr_file_group.hpssfile
                    file_type = prepbufr_file_group.filetype
                    if prepbufr_run_hpss == 'YES':
                        error_msg = ('WARNING: '+prod_file+' and '+arch_file
                                     +' do not exist and did not find '
                                     'HPSS file '+hpss_file+' from '
                                     +hpss_tar+' or walltime exceeded')
                    else:
                        error_msg = ('WARNING: '+prod_file+' and '+arch_file
                                     +' do not exist')
                    print(error_msg)
                    with open(error_file, 'a') as file:
                        file.write(error_msg)

elif RUN == 'grid2obs_step2':
    # Read in environment variables
    type_list = os.environ['g2o2_type_list'].split(' ')
    gather_by_list = os.environ['g2o2_gather_by_list'].split(' ')
    for type in type_list:
        fhr_list_type = os.environ['g2o2_fhr_list_'+type].split(', ')
        if plot_by == 'VALID':
            start_hr_type = os.environ['g2o2_valid_hr_beg_'+type]
            end_hr_type = os.environ['g2o2_valid_hr_end_'+type]
            hr_inc_type = os.environ['g2o2_valid_hr_inc_'+type]
        else:
            start_hr_type = os.environ['g2o2_init_hr_beg']
            end_hr_type = os.environ['g2o2_init_hr_end']
            hr_inc_type = os.environ['g2o2_init_hr_inc']
        # Get date and time information
        time_info = get_time_info(start_date, end_date, start_hr_type,
                                  end_hr_type, hr_inc_type, fhr_list_type,
                                  plot_by)
        # Get archive MET .stat files
        cwd = os.getcwd()
        for name in model_list:
            index = model_list.index(name)
            if len(model_arch_dir_list) != len(model_list):
                arch_dir = model_arch_dir_list[0]
            else:
                arch_dir = model_arch_dir_list[index]
            if len(gather_by_list) != len(model_list):
                gather_by = gather_by_list[0]
            else:
                gather_by = gather_by_list[index]
            full_arch_dir = os.path.join(arch_dir, 'metplus_data',
                                         'by_'+gather_by, 'grid2obs',
                                          type)
            link_model_data_dir = os.path.join(cwd, 'data', name, type)
            if not os.path.exists(link_model_data_dir):
                os.makedirs(link_model_data_dir)
            for time in time_info:
                valid_time = time.validtime
                init_time = time.inittime
                lead = time.lead
                if gather_by == 'VALID':
                    stat_file = os.path.join(full_arch_dir,
                                             valid_time.strftime('%H')+'Z',
                                             name, name+'_'
                                             +valid_time.strftime('%Y%m%d')
                                             +'.stat')
                    link_stat_file = os.path.join(link_model_data_dir, name
                                                  +'_valid'+valid_time \
                                                  .strftime('%Y%m%d')
                                                  +'_valid'+valid_time \
                                                  .strftime('%H')+'.stat')
                elif gather_by == 'INIT':
                    if (init_time.strftime('%H') not in 
                            [ '03', '09', '15', '21' ]):
                        stat_file = os.path.join(full_arch_dir,
                                                 init_time.strftime('%H')+'Z',
                                                 name, name+'_'
                                                 +init_time.strftime('%Y%m%d')
                                                 +'.stat')
                        link_stat_file = os.path.join(link_model_data_dir,
                                                      name+'_init'+init_time \
                                                      .strftime('%Y%m%d')
                                                      +'_init'+init_time \
                                                      .strftime('%H')+'.stat')
                elif gather_by == 'VSDB':
                    if (init_time.strftime('%H') not in 
                            [ '03', '09', '15', '21' ]):
                        stat_file = os.path.join(full_arch_dir,
                                                 init_time.strftime('%H')+'Z',
                                                 name, name+'_'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'.stat')
                        link_stat_file = os.path.join(link_model_data_dir,
                                                      name+'_valid'
                                                      +valid_time \
                                                      .strftime('%Y%m%d')
                                                      +'_init'+init_time \
                                                      .strftime('%H')+'.stat')
                if not os.path.exists(link_stat_file):
                    if os.path.exists(stat_file):
                        os.system('ln -sf '+stat_file+' '
                                  +link_stat_file)
                    else:
                        print("WARNING: "+stat_file
                              +" does not exist")

elif RUN == 'precip_step1':
    obtype = os.environ['precip1_obtype']
    accum_length = int(os.environ['precip1_accum_length'])
    model_bucket_list = os.environ['precip1_model_bucket_list'].split(' ')
    model_var_name_list = os.environ['precip1_model_varname_list'].split(' ')
    obs_run_hpss = os.environ['precip1_obs_data_runhpss']
    if make_met_data_by == 'VALID':
        start_hr = os.environ['precip1_valid_hr_beg']
        end_hr = os.environ['precip1_valid_hr_end']
        hr_inc = os.environ['precip1_valid_hr_inc']
    else:
        start_hr = os.environ['prceip1_init_hr_beg']
        end_hr = os.environ['precip1_init_hr_end']
        hr_inc = os.environ['precip1_init_hr_inc']
    fhr_list = os.environ['precip1_fhr_list'].split(', ')
     
    sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                              int(start_date[6:]), int(start_hr))
    edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                              int(end_date[6:]), int(end_hr))
    date_inc = datetime.timedelta(seconds=int(hr_inc))

    time_info = get_time_info(start_date, end_date,
                              start_hr, end_hr, hr_inc,
                              fhr_list, make_met_data_by)
    cwd = os.getcwd()
    for name in model_list:
        index = model_list.index(name)
        dir = model_dir_list[index]
        file_format = model_fileformat_list[index]
        hpss_dir = model_hpssdir_list[index]
        bucket = int(model_bucket_list[index])
        var_name = model_var_name_list[index]
        nfiles_accum = accum_length/bucket
        file_accum_intvl = bucket
        link_model_data_dir = os.path.join(cwd, 'data', name)
        if not os.path.exists(link_model_data_dir):
            os.makedirs(link_model_data_dir)
            os.makedirs(link_model_data_dir+'/HPSS_jobs')
        for time in time_info:
            valid_time = time.validtime
            init_time = time.inittime
            lead_end = time.lead
            if init_time.strftime('%H') in [ '03', '09', '15', '21' ]:
                continue
            else:
                nf, leads_in_accum_list = 1, []
                while nf <= nfiles_accum:
                    lead_now = int(lead_end)-((nf-1)*file_accum_intvl)
                    leads_in_accum_list.append(lead_now)
                    nf+=1
                leads_in_accum_list_check = filter(lambda x: x > 0,
                                                   leads_in_accum_list)
                if len(leads_in_accum_list_check) == len(leads_in_accum_list):
                    for lead_in_accum in leads_in_accum_list:
                        lead = str(lead_in_accum).zfill(2)
                        link_model_forecast_file = os.path.join(
                            link_model_data_dir,
                            'f'+lead+'.'+init_time.strftime('%Y%m%d%H')
                            )
                        if not os.path.exists(link_model_forecast_file):
                            model_forecast_filename = format_filler(
                                file_format, valid_time, init_time, lead
                                )
                            model_forecast_file = os.path.join(
                                dir, name, model_forecast_filename
                                )
                            if os.path.exists(model_forecast_file):
                                if var_name == 'APCP':
                                    if "grib2" in model_forecast_file:
                                        convert_grib2_grib1(model_forecast_file,
                                                            link_model_forecast_file)
                                    else:
                                        os.system('ln -sf '+model_forecast_file
                                                  +' '+link_model_forecast_file)
                                elif var_name == 'PRATE':
                                    if "grib2" in model_forecast_file:
                                        convert_grib2_grib1(model_forecast_file,
                                                            link_model_forecast_file)
                                    else:
                                        os.system('cp '+model_forecast_file
                                              +' '+link_model_forecast_file)
                            else:
                                if model_data_run_hpss == 'YES':
                                    print("Did not find "
                                          +model_forecast_file+" online..."
                                          "going to try to get file from HPSS")
                                    hpss_tar, hpss_file, hpss_job_filename = (
                                        set_up_gfs_hpss_info(init_time, hpss_dir, 
                                                             'f'+lead.zfill(3),
                                                             link_model_data_dir)
                                        )
                                    get_hpss_data(hpss_job_filename,
                                                  link_model_data_dir, 
                                                  link_model_forecast_file,
                                                  hpss_tar, hpss_file)
                            if not os.path.exists(link_model_forecast_file):
                                if model_data_run_hpss == 'YES':
                                    print("WARNING: "+model_forecast_file+" "
                                          "does not exist and did not find "
                                          "HPSS file "+hpss_file+" from "
                                          +hpss_tar+" or walltime exceeded")
                                else:
                                    print("WARNING: "+model_forecast_file
                                          +" does not exist")
                            else:
                                if var_name == 'PRATE':
                                    os.system('mv '+link_model_forecast_file
                                              +' '+link_model_data_dir
                                              +'/tmp_gb1')
                                    cnvgrib = os.environ['CNVGRIB']
                                    os.system(cnvgrib+' -g12 '
                                              +link_model_data_dir
                                              +'/tmp_gb1 '
                                              +link_model_data_dir+'/tmp_gb2')
                                    wgrib2 = os.environ['WGRIB2']
                                    os.system(wgrib2+' '
                                              +link_model_data_dir
                                              +'/tmp_gb2 -match ":PRATE:" '
                                              '-rpn "3600:*" -set_var APCP '
                                              '-set table_4.10 1 -grib_out '
                                              +link_model_data_dir
                                              +'/tmp_gb2_APCP >>/dev/null')
                                    os.system(cnvgrib+' -g21 '
                                              +link_model_data_dir
                                              +'/tmp_gb2_APCP '
                                              +link_model_forecast_file)
                                    os.system('rm '+link_model_data_dir
                                              +'/tmp*')

    valid_time_list = []
    for time in time_info:
        valid_time = time.validtime
        if valid_time not in valid_time_list:
            valid_time_list.append(valid_time)
    for valid_time in valid_time_list:
        YYYYmmddHH = valid_time.strftime('%Y%m%d%H')
        YYYYmmdd = valid_time.strftime('%Y%m%d')
        YYYYmm = valid_time.strftime('%Y%m')
        YYYY = valid_time.strftime('%Y')
        mm = valid_time.strftime('%m')
        dd = valid_time.strftime('%d')
        HH = valid_time.strftime('%H')
        link_obs_data_dir = os.path.join(cwd, 'data',
                                         obtype)
        if obtype == 'ccpa' and accum_length == 24:
            link_obs_file = os.path.join(link_obs_data_dir,
                                         'ccpa.'+YYYYmmdd+'12.24h') 
            prod_dir = os.environ['ccpa_24hr_prod_dir']
            prod_file = os.path.join(prod_dir,
                                     'precip.'+YYYYmmdd,
                                     'ccpa.'+YYYYmmdd+'12.24h')
            arch_dir = os.environ['ccpa_24hr_arch_dir']
            arch_file = os.path.join(arch_dir,
                                     'ccpa.'+YYYYmmdd+'12.24h')
            hpss_date_dir = os.path.join(hpss_prod_base_dir,
                                         'rh'+YYYY, YYYYmm,
                                         YYYYmmdd)
            hpss_tar = os.path.join(hpss_date_dir,
                                    'com_verf_prod_precip.'
                                    +YYYYmmdd+'.precip.tar')
            hpss_file = 'ccpa.'+YYYYmmdd+'12.24h'
        else:
            print("ERROR: "+obtype+" for observations with "
                  "accumulation length of "+str(accum_length)
                  +"hr is not valid")
            exit(1)
        if not os.path.exists(link_obs_data_dir):
            os.makedirs(link_obs_data_dir)
            os.makedirs(link_obs_data_dir+'/HPSS_jobs')
        if not os.path.exists(link_obs_file):
            if os.path.exists(prod_file):
                os.system('ln -sf '+prod_file+' '+link_obs_file)
            elif os.path.exists(arch_file):
                os.system('ln -sf '+arch_file+' '+link_obs_file)
            else:
                if obs_run_hpss == 'YES':
                    print("Did not find "+prod_file+" or "+arch_file+" "
                          +"online...going to try to get file from HPSS")
                    hpss_job_filename = os.path.join(
                        link_obs_data_dir, 'HPSS_jobs', 
                        'HPSS_'+hpss_tar.rpartition('/')[2]
                        +'_'+hpss_file.replace('/', '_')+'.sh'
                        )
                    get_hpss_data(hpss_job_filename,
                                  link_obs_data_dir, link_obs_file,
                                  hpss_tar, hpss_file)
        if not os.path.exists(link_obs_file):
            error_dir = os.path.join(link_obs_data_dir)
            error_file = os.path.join(
                error_dir,
                'error_'+valid_time.strftime('%Y%m%d%H%M')+'.txt'
                )
            if obs_run_hpss == 'YES':
                error_msg = ('WARNING: '+prod_file+' and '+arch_file+' do not '
                             +'exist and did not find HPSS file '
                             +hpss_file+' from '+hpss_tar+' or '
                             'walltime exceeded')
            else:
                error_msg = ('WARNING: '+prod_file+' and '
                             +arch_file+' do not exist')
            print(error_msg)
            with open(error_file, 'a') as file:
                file.write(error_msg)

print("END: "+os.path.basename(__file__))
