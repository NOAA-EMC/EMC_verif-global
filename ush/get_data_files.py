'''
Program Name: get_data_file.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This gets the necessary data files to run
          the METplus use case.
'''

import os
import subprocess
import datetime
from time import sleep
import pandas as pd

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
model_data_run_hpss = os.environ['model_data_run_hpss']
model_hpss_dir_list = os.environ['model_hpss_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
machine = os.environ['machine']
RUN_abbrev = os.environ['RUN_abbrev']
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Set some common varaibles
hpss_prod_base_dir = '/NCEPPROD/hpssprod/runhistory'
cwd = os.getcwd()

# No HPSS access from Orion
if machine == 'ORION':
    print("WARNING: Orion does not currently have access to HPSS..."
          +"setting model_data_runhpss to NO")
    model_data_run_hpss = 'NO'

def get_time_info(start_date_str, end_date_str,
                  start_hr_str, end_hr_str, hr_inc_str,
                  fhr_list, date_type):
    """! This creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings
        
         Args:
             start_date_str - string of the verification start
                              date
             end_date_str   - string of the verification end
                              date
             start_hr_str   - string of the verification start
                              hour
             end_hr_str     - string of the verification end
                              hour
             hr_inc_str     - string of the increment between
                              start_hr and end_hr
             fhr_list       - list of strings of the forecast
                              hours to verify
             date_type      - string defining by what type
                              date and times to create METplus
                              data
             
         Returns:
             time_info - list of dictionaries with the valid,
                         initalization, and forecast hour
                         pairings
    """
    sdate = datetime.datetime(int(start_date_str[0:4]),
                              int(start_date_str[4:6]),
                              int(start_date_str[6:]),
                              int(start_hr_str))
    edate = datetime.datetime(int(end_date_str[0:4]),
                              int(end_date_str[4:6]),
                              int(end_date_str[6:]),
                              int(end_hr_str))
    date_inc = datetime.timedelta(seconds=int(hr_inc_str))
    time_info = []
    date = sdate
    while date <= edate:
        if date_type == 'VALID':
            valid_time = date
        elif date_type == 'INIT':
            init_time = date
        for fhr in fhr_list:
            if fhr == 'anl':
                lead = '00'
            else:
                lead = fhr
            if date_type == 'VALID':
                init_time = valid_time - datetime.timedelta(hours=int(lead))
            elif date_type == 'INIT':
                valid_time = init_time + datetime.timedelta(hours=int(lead))
            t = {}
            t['valid_time'] = valid_time
            t['init_time'] = init_time
            t['lead'] = lead
            time_info.append(t)
        date = date + date_inc
    return time_info

def format_filler(unfilled_file_format, dt_valid_time, dt_init_time, str_lead):
    """! This creates a list of objects containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings
        
         Args:
             unfilled_file_format   - string of file naming convention
             dt_valid_time          - datetime object of the valid time
             dt_init_time           - datetime object of the
                                      initialization time
             str_lead               - string of the forecast lead
          
         Returns:
             filled_file_format - string of file_format
                                  filled in with verifying
                                  time information
    """
    filled_file_format = ''
    format_opt_list = ['lead', 'valid', 'init', 'cycle']
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   format_opt_count_fmt = (
                       filled_file_format_chunk \
                       .partition('{'+format_opt+'?fmt=')[2] \
                       .partition('}')[0]
                   )
                   if format_opt == 'valid':
                       replace_format_opt_count = dt_valid_time.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(str_lead) < 10:
                               replace_format_opt_count = str_lead[1]
                           else:
                               replace_format_opt_count = str_lead
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = str_lead.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = str_lead.zfill(3)
                       else:
                           replace_format_opt_count = str_lead
                   elif format_opt in ['init', 'cycle']:
                       replace_format_opt_count = dt_init_time.strftime(
                           format_opt_count_fmt
                       )
                   filled_file_format_chunk = (
                       filled_file_format_chunk.replace(
                           '{'+format_opt+'?fmt='
                           +format_opt_count_fmt+'}',
                           replace_format_opt_count
                       )
                   )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format

def set_up_gfs_hpss_info(dt_init_time, hpss_dir, hpss_file_prefix,
                         hpss_file_suffix, save_data_dir):
    """! This sets up HPSS and job information specifically
         for getting GFS data from HPSS.

         Args:
             dt_init_time      - datetime object of the
                                 initialization time
             hpss_dir          - string of the base HPSS
                                 directory path
             hpss_file_prefix  - string of information at
                                 the beinginng of the HPSS
                                 file
             hpss_file_suffix  - string of information
                                 on the end of the HPSS
                                 file
             save_data_dir     - string of the path to the
                                 directory where the HPSS
                                 retrieved file will be
                                 saved

         Returns:
             hpss_tar          - string of the tar file
                                 path where hpss_file
                                 is located
             hpss_file         - string of the file name
                                 to be retrieved from HPSS
             hpss_job_filename - string of the path of the
                                 HPSS job card name
    """
    # Read in environment variables
    HTAR = os.environ['HTAR']
    # Set date variables
    YYYYmmddHH = dt_init_time.strftime('%Y%m%d%H')
    YYYYmmdd = dt_init_time.strftime('%Y%m%d')
    YYYYmm = dt_init_time.strftime('%Y%m')
    YYYY = dt_init_time.strftime('%Y')
    mm = dt_init_time.strftime('%m')
    dd = dt_init_time.strftime('%d')
    HH = dt_init_time.strftime('%H')
    if 'NCEPPROD' in hpss_dir:
        # Operational GFS HPSS archive only for pgrb2 files
        # note: no cyclone track files
        hpss_date_dir = os.path.join(hpss_dir, 'rh'+YYYY, YYYYmm, YYYYmmdd)
        if dt_init_time \
                >= datetime.datetime.strptime('20200226', '%Y%m%d'):
            hpss_tar = os.path.join(
                hpss_date_dir, 'com_gfs_prod_'+hpss_file_prefix+'.'
                +YYYYmmdd+'_'+HH+'.'+hpss_file_prefix+'_pgrb2.tar'
            )
            hpss_file = os.path.join(
                hpss_file_prefix+'.'+YYYYmmdd, HH,
                hpss_file_prefix+'.t'+HH+'z.pgrb2.0p25.'
                +hpss_file_suffix
            )
        elif dt_init_time \
                    >= datetime.datetime.strptime('20190612', '%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20200226', '%Y%m%d'):
            hpss_tar = os.path.join(
                hpss_date_dir, 'gpfs_dell1_nco_ops_com_gfs_prod_'
                +hpss_file_prefix+'.'+YYYYmmdd+'_'+HH+'.'
                +hpss_file_prefix+'_pgrb2.tar'
            )
            hpss_file = os.path.join(
                hpss_file_prefix+'.'+YYYYmmdd, HH,
                hpss_file_prefix+'.t'+HH+'z.pgrb2.0p25.'
                +hpss_file_suffix
            )
        elif dt_init_time \
                    >= datetime.datetime.strptime('20170720','%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20190612','%Y%m%d'):
            hpss_tar = os.path.join(
                hpss_date_dir, 'gpfs_hps_nco_ops_com_gfs_prod_'
                +hpss_file_prefix+'.'+YYYYmmddHH+'.pgrb2_0p25.tar'
            )
            hpss_file = (
                hpss_file_prefix+'.t'+HH+'z.pgrb2.0p25.'
                +hpss_file_suffix
             )
        elif dt_init_time \
                    >= datetime.datetime.strptime('20160510', '%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20170720', '%Y%m%d'):
            hpss_tar = os.path.join(
                hpss_date_dir, 'com2_gfs_prod_'+hpss_file_prefix+'.'
                +YYYYmmddHH+'.pgrb2_0p25.tar'
            )
            hpss_file = (
                hpss_file_prefix+'.t'+HH+'z.pgrb2.0p25.'
                +hpss_file_suffix
            )
        elif dt_init_time \
                < datetime.datetime.strptime('20160510', '%Y%m%d'):
            hpss_tar = os.path.join(
                hpss_date_dir, 'com_gfs_prod_'+hpss_file_prefix+'.'
                +YYYYmmddHH+'.pgrb2_0p25.tar'
            )
            hpss_file = (
                hpss_file_prefix+'.t'+HH+'z.pgrb2.0p25.'
                +hpss_file_suffix
            )
        # Make some adjustments for enkfgdas files
        if hpss_file_prefix == 'enkfgdas':
            hpss_tar = hpss_tar.replace('_pgrb2.tar', '.tar') \
                       .replace('.pgrb2_0p25.tar', '.tar')
            hpss_file = hpss_file.replace('pgrb2.0p25.','') \
                        .replace(hpss_file_prefix+'.t', 'gdas.t')
    else:
        if hpss_file_prefix == 'gfs':
            hpss_tar = os.path.join(hpss_dir, YYYYmmddHH, 'gfsa.tar')
        elif hpss_file_prefix == 'gdas':
            hpss_tar = os.path.join(hpss_dir, YYYYmmddHH, 'gdas.tar')
        elif hpss_file_prefix == 'enkfgdas':
            hpss_tar = os.path.join(hpss_dir, YYYYmmddHH, 'enkfgdas.tar')
        if hpss_file_suffix == 'cyclone.trackatcfunix':
            hpss_file = os.path.join(hpss_file_prefix+'.'+YYYYmmdd, HH,
                                      'atmos', 'avno.t'+HH+'z.'
                                       +hpss_file_suffix)
        elif hpss_file_prefix == 'enkfgdas':
            hpss_file = os.path.join(hpss_file_prefix+'.'+YYYYmmdd, HH,
                                      'atmos', 'gdas.t'+HH+'z.'
                                      +hpss_file_suffix)
        else:
            hpss_file = os.path.join(hpss_file_prefix+'.'+YYYYmmdd, HH,
                                      'atmos', hpss_file_prefix+'.t'+HH
                                      +'z.pgrb2.0p25.'+hpss_file_suffix)
    hpss_job_filename = os.path.join(save_data_dir, 'HPSS_jobs',
                                     'HPSS_'+hpss_tar.rpartition('/')[2]
                                     +'_'+hpss_file.replace('/', '_')+'.sh')
    return hpss_tar, hpss_file, hpss_job_filename

def get_hpss_data(hpss_job_filename, save_data_dir, save_data_file,
                  hpss_tar, hpss_file):
    """! This creates a job card with the necessary information
         to retrieve a file from HPSS. It then submits this
         job card to the transfer queue and the designating
         wall time. 

         Args:
             hpss_job_filename - string of the path of the
                                 HPSS job card name
             save_data_dir     - string of the path to the
                                 directory where the HPSS
                                 retrieved file will be
                                 saved
             save_data_file    - string of the file name
                                 the HPSS retrieved file
                                 will be saved as
             hpss_tar          - string of the tar file
                                 path where hpss_file
                                 is located
             hpss_file         - string of the file name
                                 to be retrieved from HPSS

         Returns:
    """
    # Read in environment variables
    HTAR = os.environ['HTAR']
    hpss_walltime = os.environ['hpss_walltime']
    machine = os.environ['machine']
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    # Set up job wall time information
    walltime_seconds = (
        datetime.timedelta(minutes=int(hpss_walltime)).total_seconds()
    )
    walltime = (datetime.datetime.min
                + datetime.timedelta(minutes=int(hpss_walltime))).time()
    if os.path.exists(hpss_job_filename):
        os.remove(hpss_job_filename)
    # Create job card
    with open(hpss_job_filename, 'a') as hpss_job_file:
        hpss_job_file.write('#!/bin/sh'+'\n')
        hpss_job_file.write('cd '+save_data_dir+'\n')
        if 'trackatcfunix' in hpss_file:
            hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'
                                +hpss_file.replace('avno', 'avn')+'\n')
            if 'gfsa.tar' in hpss_tar or 'gdas.tar' in hpss_tar \
                    or 'enkfgdas.tar' in hpss_tar:
                hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'
                                    +hpss_file.replace('avno', 'avn') \
                                    .replace('atmos/','')+'\n')
        else:
            hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'+hpss_file+'\n')
            if 'gfsa.tar' in hpss_tar or 'gdas.tar' in hpss_tar \
                    or 'enkfgdas.tar' in hpss_tar:
                hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'
                                    +hpss_file.replace('atmos/','')+'\n')
        if 'pgrb2' in hpss_file:
            cnvgrib = os.environ['CNVGRIB']
            hpss_job_file.write(cnvgrib+' -g21 '+hpss_file+' '
                                +save_data_file+' > /dev/null 2>&1\n')
            if 'gfsa.tar' in hpss_tar or 'gdas.tar' in hpss_tar \
                    or 'enkfgdas.tar' in hpss_tar:
                hpss_job_file.write(cnvgrib+' -g21 '
                                    +hpss_file.replace('atmos/','')+' '
                                    +save_data_file+' > /dev/null 2>&1\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
        elif 'trackatcfunix' in hpss_file:
            hpss_job_file.write('cp '+hpss_file.split('avn')[0]+'avn* '
                                +save_data_file+'\n')
            if 'gfsa.tar' in hpss_tar or 'gdas.tar' in hpss_tar \
                    or 'enkfgdas.tar' in hpss_tar:
                hpss_job_file.write('cp '+hpss_file.replace('atmos/','') \
                                    .split('avn')[0]+'avn* '+save_data_file
                                    +'\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0]+'\n')
            model_atcf_abbrv = (save_data_file.split('/')[-2])[0:4].upper()
            hpss_job_file.write('sed -i s/AVNO/'+model_atcf_abbrv+'/g '
                                +save_data_file)
        else:
            if hpss_file[0:5] != 'ccpa.':
                hpss_job_file.write('cp '+hpss_file+' '+save_data_file+'\n')
                if 'gfsa.tar' in hpss_tar or 'gdas.tar' in hpss_tar \
                        or 'enkfgdas.tar' in hpss_tar:
                    hpss_job_file.write('cp '
                                        +hpss_file.replace('atmos/','')+' '
                                        +save_data_file+'\n')
                hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
    # Submit job card
    os.chmod(hpss_job_filename, 0o755)
    hpss_job_output = hpss_job_filename.replace('.sh', '.out')
    if os.path.exists(hpss_job_output):
        os.remove(hpss_job_output)
    hpss_job_name = hpss_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+hpss_job_filename+" to "+QUEUESERV)
    print("Output sent to "+hpss_job_output)
    if machine == 'WCOSS_C':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+hpss_job_output+' -e '
                  +hpss_job_output+' '
                  +'-J '+hpss_job_name+' -R rusage[mem=2048] '
                  +hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'WCOSS_DELL_P3':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+hpss_job_output+' -e '
                  +hpss_job_output+' '
                  +'-J '+hpss_job_name+' -M 2048 -R "affinity[core(1)]" '
                  +hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'HERA':
        os.system('sbatch --ntasks=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --partition='+QUEUESERV+' '
                  +'--account='+ACCOUNT+' --output='+hpss_job_output+' '
                  +'--job-name='+hpss_job_name+' '+hpss_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +hpss_job_name+' -t R,PD -h | wc -l')
    elif machine == 'ORION':
        print("ERROR: No HPSS access from Orion.")
    if machine != 'ORION':
        sleep_counter, sleep_checker = 1, 10
        while (sleep_counter*sleep_checker) <= walltime_seconds:
            sleep(sleep_checker)
            print("Walltime checker: "+str(sleep_counter*sleep_checker)+" "
                  +"out of "+str(int(walltime_seconds))+" seconds")
            check_job = subprocess.check_output(job_check_cmd, shell=True,
                                                encoding='UTF-8')
            if check_job[0] == '0':
                break
            sleep_counter+=1

def convert_grib2_grib1(grib2_file, grib1_file):
    """! This converts GRIB2 data to GRIB1
        
         Args:
             grib2_file - string of the path to
                          the GRIB2 file to
                          convert
             grib1_file - string of the path to
                          save the converted GRIB1
                          file
 
         Returns:
    """
    print("Converting GRIB2 file "+grib2_file+" "
          +"to GRIB1 file "+grib1_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g21 '+grib2_file+' '
              +grib1_file+' > /dev/null 2>&1')

def get_model_file(valid_time_dt, init_time_dt, lead_str,
                   name, data_dir, file_format, run_hpss,
                   hpss_data_dir, link_data_dir, link_file_format):
    """! This links a model file from its archive.
         If the file does not exist locally, then retrieve
         from HPSS if requested.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             data_dir         - string of the online archive
                                for model
             file_format      - string of the file format the
                                files are saved as in the data_dir
             run_hpss         - string of whether to get missing
                                online model data (YES) or not (NO)
             hpss_data_dir    - string of the path to model data
                                on HPSS
             link_data_dir    - string of the directory to link
                                model data to
             link_file_format - string of the linked file name

         Returns:
    """
    grib2_file_names = ['grib2', 'grb2']
    link_filename = format_filler(link_file_format, valid_time_dt,
                                  init_time_dt, lead_str)
    link_model_file = os.path.join(link_data_dir, link_filename)
    if not os.path.exists(link_model_file):
        model_filename = format_filler(file_format, valid_time_dt,
                                       init_time_dt, lead_str)
        model_file = os.path.join(data_dir, name, model_filename)
        if os.path.exists(model_file):
            if any(g in model_file for g in grib2_file_names):
                convert_grib2_grib1(model_file, link_model_file)
            else:
                os.system('ln -sf '+model_file+' '+link_model_file)
        else:
            if run_hpss == 'YES':
                print("Did not find "+model_file+" online..."
                      +"going to try to get file from HPSS")
                if 'gfs' in file_format:
                    dump = 'gfs'
                elif 'gdas' in file_format:
                    dump = 'gdas'
                else:
                    dump = name
                if lead_str != 'anl':
                   file_lead = 'f'+lead_str.zfill(3)
                else:
                   file_lead = lead_str
                model_hpss_tar, model_hpss_file, model_hpss_job_filename = (
                    set_up_gfs_hpss_info(init_time_dt, hpss_data_dir,
                                         dump, file_lead, link_data_dir)
                )
                get_hpss_data(model_hpss_job_filename, link_data_dir,
                              link_model_file, model_hpss_tar, model_hpss_file)
    if not os.path.exists(link_model_file):
        if run_hpss == 'YES':
            print("WARNING: "+model_file+" does not exist and did not find "
                  +"HPSS file "+model_hpss_file+" from "+model_hpss_tar+" or "
                  +"walltime exceeded")
        else:
            print("WARNING: "+model_file+" does not exist")

def get_model_stat_file(valid_time_dt, init_time_dt, lead_str,
                        name, stat_data_dir, gather_by, RUN_dir_name,
                        RUN_sub_dir_name, link_data_dir):
    """! This links a model .stat file from its archive.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             stat_data_dir    - string of the online archive
                                for model MET .stat files
             gather_by        - string of the file format the
                                files are saved as in the data_dir
             RUN_dir_name     - string of RUN directory name
                                in 'metplus_data' archive
             RUN_sub_dir_name - string of RUN sub-directory name
                                (under RUN_dir_name)
                                in 'metplus_data' archive
             link_data_dir    - string of the directory to link
                                model data to

         Returns:
    """
    model_stat_gather_by_RUN_dir = os.path.join(stat_data_dir, 'metplus_data',
                                                'by_'+gather_by, RUN_dir_name,
                                                RUN_sub_dir_name)
    if gather_by == 'VALID':
         model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                        valid_time.strftime('%H')+'Z', name,
                                        name+'_'+valid_time.strftime('%Y%m%d')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                             +valid_time.strftime('%Y%m%d')
                                             +'_valid'+valid_time.strftime('%H')
                                             +'.stat')
    elif gather_by == 'INIT':
         model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                        init_time.strftime('%H')+'Z', name,
                                        name+'_'+init_time.strftime('%Y%m%d')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir, name+'_init'
                                             +init_time.strftime('%Y%m%d')
                                             +'_init'+init_time.strftime('%H')
                                             +'.stat')
    elif gather_by == 'VSDB':
         if RUN_dir_name == 'grid2grid':
             model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                            valid_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'_valid'
                                                 +valid_time.strftime('%H')
                                                 +'.stat')
    if not os.path.exists(link_model_stat_file):
        if os.path.exists(model_stat_file):
            os.system('ln -sf '+model_stat_file+' '+link_model_stat_file)
        else:
            print("WARNING: "+stat_file+" does not exist")

if RUN == 'grid2grid_step1':
    # Get model forecast and truth files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_truth_name = os.environ[
            RUN_abbrev_type+'_truth_name'
        ]
        RUN_abbrev_type_truth_file_format_list = os.environ[
            RUN_abbrev_type+'_truth_file_format_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, make_met_data_by
        )
        RUN_abbrev_type_valid_time_list = []
        for time in RUN_abbrev_type_time_info_dict:
            valid_time = time['valid_time']
            if valid_time not in RUN_abbrev_type_valid_time_list:
                RUN_abbrev_type_valid_time_list.append(valid_time)
        # Get forecast and truth files for each model
        for model in model_list:
            model_idx = model_list.index(model)
            model_dir = model_dir_list[model_idx]
            model_file_format = model_file_format_list[model_idx]
            model_hpss_dir = model_hpss_dir_list[model_idx]
            model_RUN_abbrev_type_truth_file_format = (
                RUN_abbrev_type_truth_file_format_list[model_idx]
            )
            link_model_data_dir = os.path.join(cwd, 'data', model)
            if not os.path.exists(link_model_data_dir):
                os.makedirs(link_model_data_dir)
                os.makedirs(os.path.join(link_model_data_dir, 'HPSS_jobs'))
            # Get model forecast files
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_file(valid_time, init_time, lead,
                                   model, model_dir, model_file_format,
                                   model_data_run_hpss, model_hpss_dir,
                                   link_model_data_dir,
                                   'f{lead?fmt=%H}.{init?fmt=%Y%m%d%H}')
            # Get model RUN_type truth files
            RUN_abbrev_type_truth_name_lead = (
                RUN_abbrev_type_truth_name.split('_')[1]
            )
            if RUN_abbrev_type_truth_name in ['self_anl', 'self_f00']:
                model_RUN_abbrev_type_truth_dir = model_dir
                RUN_abbrev_type_truth_name_short = model
                model_RUN_abbrev_type_truth_hpss_dir = model_hpss_dir
            elif RUN_abbrev_type_truth_name in ['gfs_anl', 'gfs_f00']:
                model_RUN_abbrev_type_truth_dir = os.environ['gstat']
                RUN_abbrev_type_truth_name_short = 'gfs'
                model_RUN_abbrev_type_truth_hpss_dir = (
                    '/NCEPPROD/hpssprod/runhistory'
                )
                if RUN_abbrev_type_truth_name \
                        == 'gfs_'+RUN_abbrev_type_truth_name_lead \
                        and model_RUN_abbrev_type_truth_file_format != \
                        ('pgb'+RUN_abbrev_type_truth_name_lead
                         +'.gfs.{valid?fmt=%Y%m%d%H}'):
                    print("WARNING: "+RUN_abbrev_type+"_truth_name set to "
                          +"gfs_"+RUN_abbrev_type_truth_name_lead+" but "
                          +"file format does not match exepcted value. "
                          +"Using to pgb"+RUN_abbrev_type_truth_name_lead
                          +".gfs.{valid?fmt=%Y%m%d%H}")
                    model_RUN_abbrev_type_truth_file_format = (
                        'pgb'+RUN_abbrev_type_truth_name_lead
                        +'.gfs.{valid?fmt=%Y%m%d%H}'
                    )
            if RUN_abbrev_type_truth_name_lead == 'f00':
                RUN_abbrev_type_truth_name_lead = '00'
            for valid_time in RUN_abbrev_type_valid_time_list:
                if valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_file(valid_time, valid_time,
                                   RUN_abbrev_type_truth_name_lead,
                                   RUN_abbrev_type_truth_name_short,
                                   model_RUN_abbrev_type_truth_dir,
                                   model_RUN_abbrev_type_truth_file_format,
                                   model_data_run_hpss,
                                   model_RUN_abbrev_type_truth_hpss_dir,
                                   link_model_data_dir,
                                   RUN_type+'.truth.{valid?fmt=%Y%m%d%H}')
                    # Check model RUN_type truth file exists, if not try
                    # to use model's own f00 file
                    truth_file = os.path.join(
                        model_RUN_abbrev_type_truth_dir,
                        RUN_abbrev_type_truth_name_short,
                        format_filler(model_RUN_abbrev_type_truth_file_format,
                                      valid_time, valid_time,
                                      RUN_abbrev_type_truth_name_lead)
                    )
                    link_truth_file = os.path.join(
                        link_model_data_dir,
                        format_filler(RUN_type+'.truth.{valid?fmt=%Y%m%d%H}',
                                      valid_time, valid_time,
                                      RUN_abbrev_type_truth_name_lead)
                    )
                    if not os.path.exists(link_truth_file) \
                            and RUN_abbrev_type_truth_name != 'self_f00':
                        print("WARNING: "+RUN_type+" truth file ("
                              +truth_file+") not found...will try to link "
                              +"model f00 instead")
                        link_model_f00_file = os.path.join(
                            link_model_data_dir,
                            format_filler('f{lead?fmt=%H}.{init?fmt=%Y%m%d%H}',
                                          valid_time, valid_time, '00')
                        )
                        if not os.path.exists(link_model_f00_file):
                            get_model_file(valid_time, valid_time, '00',
                                           model, model_dir, model_file_format,
                                           model_data_run_hpss, model_hpss_dir,
                                           link_model_data_dir,
                                           RUN_type+'.truth.{valid?fmt=%Y%m%d%H}')
                        else:
                            os.system('ln -sf '+link_model_f00_file+' '
                                       +link_truth_file)
                    if not os.path.exists(link_truth_file):
                        print("WARNING: Unable to link model f00 file as "
                              +"subsitute truth file for "+RUN_type)
elif RUN == 'grid2grid_step2':
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_truth_name_list = os.environ[
            RUN_abbrev_type+'_truth_name_list'
        ].split(' ')
        RUN_abbrev_type_gather_by_list = os.environ[
            RUN_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, plot_by
        )
        # Get stat files model
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_RUN_abbrev_type_gather_by = (
                RUN_abbrev_type_gather_by_list[model_idx]
            )
            link_model_RUN_type_data_dir = os.path.join(cwd, 'data',
                                                        model, RUN_type)
            if not os.path.exists(link_model_RUN_type_data_dir):
                os.makedirs(link_model_RUN_type_data_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                get_model_stat_file(valid_time, init_time, lead,
                                    model, model_stat_dir,
                                    model_RUN_abbrev_type_gather_by,
                                    'grid2grid', RUN_type,
                                    link_model_RUN_type_data_dir)
#elif RUN == 'grid2obs_step1':
#elif RUN == 'grid2obs_step2':
#elif RUN == 'precip_step1':
#elif RUN == 'precip_step2':
#elif RUN == 'satellite_step1':
#elif RUN == 'satellite_step2':
#elif RUN == 'tropcyc':
#elif RUN == 'maps2d':
#elif RUN == 'mapsda':

print("END: "+os.path.basename(__file__))
