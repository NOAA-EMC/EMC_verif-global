'''
Program Name: get_data_files_step2.py
Contact(s): Mallory Row
Abstract: This script is run by step2 scripts in scripts/.
          This gets the necessary stat files to run
          the plot use case.
'''

import os
import subprocess
import datetime
from time import sleep
import pandas as pd
import glob
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

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
                lead = '0'
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

def wget_data(wget_job_filename, wget_job_name, wget_job_output):
    """! This submits a job to the transfer queue
          to use wget to retrieve data

         Args:
             wget_job_filename - string of the path to
                                 the wget job file
             wget_job_name     - string of job submission
                                 name
             wget_job_output   - string of the path to
                                 write job submission
                                 output
         Returns:
    """
    wget_walltime = os.environ['hpss_walltime']
    machine = os.environ['machine']
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    CLUSTERS_DTN = os.environ['CLUSTERS_DTN']
    PARTITION_DTN = os.environ['PARTITION_DTN']
    # Set up job wall time information
    walltime_seconds = (
        datetime.timedelta(minutes=int(wget_walltime)).total_seconds()
    )
    walltime = (datetime.datetime.min
                + datetime.timedelta(minutes=int(wget_walltime))).time()
    # Submit job
    os.chmod(wget_job_filename, 0o755)
    print("Submitting "+wget_job_filename+" to "+QUEUESERV)
    print("Output sent to "+wget_job_output)
    if machine == 'WCOSS2':
        os.system('qsub -V -l walltime='+walltime.strftime('%H:%M:%S')+' '
                  +'-q '+QUEUESERV+' -A '+ACCOUNT+' -o '+wget_job_output+' '
                  +'-e '+wget_job_output+' -N '+wget_job_name+' '
                  +'-l select=1:ncpus=1 '+wget_job_filename)
        job_check_cmd = ('qselect -s QR -u '+os.environ['USER']+' '
                         +'-N '+wget_job_name+' | wc -l')
    elif machine == 'GAEAC6':
        os.system('sbatch --nodes=1 --ntasks-per-node=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --cluster='+CLUSTERS_DTN+' '
                  +'--partition='+PARTITION_DTN+' --constraint=f6 --qos=dtn '
                  +'--account='+ACCOUNT+' --output='+wget_job_output+' '
                  +'--job-name='+wget_job_name+' '+wget_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +wget_job_name+' -t R,PD -h | wc -l')
    elif machine in ['HERA', 'ORION', 'HERCULES']:
        os.system('sbatch --ntasks=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --partition='+QUEUESERV+' '
                  +'--account='+ACCOUNT+' --output='+wget_job_output+' '
                  +'--job-name='+wget_job_name+' '+wget_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +wget_job_name+' -t R,PD -h | wc -l')
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

def set_up_gfs_hpss_info(dt_init_time, hpss_dir, model_dump,
                         hpss_file_suffix, save_data_dir):
    """! This sets up HPSS and job information specifically
         for getting GFS data from HPSS.

         Args:
             dt_init_time      - datetime object of the
                                 initialization time
             hpss_dir          - string of the base HPSS
                                 directory path
             model_dump        - string of model dump
                                 the beinginng of the HPSS
                                 file
                                 (gfs, gdas, enkfgfs)
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
        # Operational GFS HPSS archive set up
        if dt_init_time \
                >= datetime.datetime.strptime('20221129', '%Y%m%d'):
            if hpss_file_suffix == 'prepbufr':
                hpss_tar_filename_prefix = ('com_obsproc_v1.1_'+model_dump+'.'
                                            +YYYYmmdd+'_'+HH+'.obsproc_'
                                            +model_dump)
                hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                                'atmos', model_dump+'.t'
                                                +HH+'z.')
            else:
                hpss_tar_filename_prefix = ('com_gfs_v16.3_'+model_dump+'.'
                                            +YYYYmmdd+'_'+HH+'.'+model_dump)
                hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                                'atmos', model_dump+'.t'
                                                +HH+'z.')
        elif dt_init_time \
                >= datetime.datetime.strptime('20220628', '%Y%m%d') \
            and dt_init_time \
                    < datetime.datetime.strptime('20221129', '%Y%m%d'):
            if hpss_file_suffix == 'prepbufr':
                hpss_tar_filename_prefix = ('com_obsproc_v1.0_'+model_dump+'.'
                                            +YYYYmmdd+'_'+HH+'.obsproc_'
                                            +model_dump)
                hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                                'atmos', model_dump+'.t'
                                                +HH+'z.')
            else:
                hpss_tar_filename_prefix = ('com_gfs_v16.2_'+model_dump+'.'
                                            +YYYYmmdd+'_'+HH+'.'+model_dump)
                hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                                'atmos', model_dump+'.t'
                                                +HH+'z.')
        elif dt_init_time \
                >= datetime.datetime.strptime('20210321', '%Y%m%d') \
            and dt_init_time \
                    < datetime.datetime.strptime('20220628', '%Y%m%d'):
            hpss_tar_filename_prefix = ('com_gfs_prod_'+model_dump+'.'
                                        +YYYYmmdd+'_'+HH+'.'+model_dump)
            hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                            'atmos', model_dump+'.t'+HH+'z.')
        elif dt_init_time \
                >= datetime.datetime.strptime('20200226', '%Y%m%d') \
            and dt_init_time \
                    < datetime.datetime.strptime('20210321', '%Y%m%d'):
            hpss_tar_filename_prefix = ('com_gfs_prod_'+model_dump+'.'
                                        +YYYYmmdd+'_'+HH+'.'+model_dump)
            hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                            model_dump+'.t'+HH+'z.')
        elif dt_init_time \
                    >= datetime.datetime.strptime('20190612', '%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20200226', '%Y%m%d'):
            hpss_tar_filename_prefix = ('gpfs_dell1_nco_ops_com_gfs_prod_'
                                        +model_dump+'.'+YYYYmmdd+'_'+HH
                                        +'.'+model_dump)
            hpss_file_prefix = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                            model_dump+'.t'+HH+'z.')
        elif dt_init_time \
                    >= datetime.datetime.strptime('20170720','%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20190612','%Y%m%d'):
            hpss_tar_filename_prefix = ('gpfs_hps_nco_ops_com_gfs_prod_'
                                        +model_dump+'.'+YYYYmmddHH)
            hpss_file_prefix = model_dump+'.t'+HH+'z.'
        elif dt_init_time \
                    >= datetime.datetime.strptime('20160510', '%Y%m%d') \
                and dt_init_time \
                    < datetime.datetime.strptime('20170720', '%Y%m%d'):
            hpss_tar_filename_prefix = ('com2_gfs_prod_'+model_dump
                                        +'.'+YYYYmmddHH)
            hpss_file_prefix = model_dump+'.t'+HH+'z.'
        elif dt_init_time \
                < datetime.datetime.strptime('20160510', '%Y%m%d'):
            hpss_tar_filename_prefix = ('com_gfs_prod_'+model_dump
                                        +'.'+YYYYmmddHH)
            hpss_file_prefix = model_dump+'.t'+HH+'z.'
        # gfs and gdas grib2 files
        if model_dump in ['gfs', 'gdas'] and (hpss_file_suffix == 'anl' \
                or hpss_file_suffix[0] == 'f'):
            if dt_init_time \
                    >= datetime.datetime.strptime('20190612', '%Y%m%d'):
                hpss_tar_filename = hpss_tar_filename_prefix+'_pgrb2.tar'
            else:
                hpss_tar_filename = hpss_tar_filename_prefix+'.pgrb2_0p25.tar'
            hpss_file = hpss_file_prefix+'pgrb2.0p25.'+hpss_file_suffix
        # gdas prepbufr file
        if model_dump == 'gdas' and hpss_file_suffix == 'prepbufr':
            hpss_tar_filename = hpss_tar_filename_prefix+'.tar'
            hpss_file = hpss_file_prefix+hpss_file_suffix
            if dt_init_time \
                    < datetime.datetime.strptime('20170720', '%Y%m%d'):
                hpss_file = hpss_file.replace(model_dump, model_dump+'1')
        # enkfgdas files
        if model_dump == 'enkfgdas':
            hpss_tar_filename = hpss_tar_filename_prefix+'.tar'
            hpss_file = (hpss_file_prefix.replace(model_dump+'.t', 'gdas.t')
                         +hpss_file_suffix)
        hpss_tar = os.path.join(hpss_dir, 'rh'+YYYY, YYYYmm, YYYYmmdd,
                                hpss_tar_filename)
    else:
        # Set up tar file
        if model_dump == 'gfs':
            hpss_tar_filename = model_dump+'a.tar'
        else:
            hpss_tar_filename = model_dump+'.tar'
        hpss_tar = os.path.join(hpss_dir, YYYYmmddHH, hpss_tar_filename)
        # Set up file
        if model_dump == 'enkfgdas':
            hpss_file = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                     'atmos', 'gdas.t'+HH+'z.'
                                     +hpss_file_suffix)
        else:
            hpss_file = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                     'atmos', model_dump+'.t'+HH
                                     +'z.pgrb2.0p25.'+hpss_file_suffix)
    # Set up job file name
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
        hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'+hpss_file+'\n')
        if '/NCEPPROD' not in hpss_tar:
            hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'
                                +hpss_file.replace('atmos/','')+'\n')
        if 'pgrb2' in hpss_file:
            cnvgrib = os.environ['CNVGRIB']
            hpss_job_file.write(cnvgrib+' -g21 '+hpss_file+' '
                                +save_data_file+' > /dev/null 2>&1\n')
            if '/NCEPPROD' not in hpss_tar:
                hpss_job_file.write(cnvgrib+' -g21 '
                                    +hpss_file.replace('atmos/','')+' '
                                    +save_data_file+' > /dev/null 2>&1\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
        else:
            if hpss_file[0:5] != 'ccpa.':
                hpss_job_file.write('cp '+hpss_file+' '+save_data_file+'\n')
                if '/NCEPPROD' not in hpss_tar:
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
    if machine == 'WCOSS2':
        os.system('qsub -V -l walltime='+walltime.strftime('%H:%M:%S')+' '
                  +'-q '+QUEUESERV+' -A '+ACCOUNT+' -o '+hpss_job_output+' '
                  +'-e '+hpss_job_output+' -N '+hpss_job_name+' '
                  +'-l select=1:ncpus=1 '+hpss_job_filename)
        job_check_cmd = ('qselect -s QR -u '+os.environ['USER']+' '
                         +'-N '+hpss_job_name+' | wc -l')
    elif machine in ['HERA']:
        os.system('sbatch --ntasks=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --partition='+QUEUESERV+' '
                  +'--account='+ACCOUNT+' --output='+hpss_job_output+' '
                  +'--job-name='+hpss_job_name+' '+hpss_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +hpss_job_name+' -t R,PD -h | wc -l')
    elif machine in ['ORION', 'HERCULES', 'GAEAC6']:
        print("ERROR: No HPSS access from "+machine)
    if machine not in ['ORION', 'HERCULES', 'GAEAC6']:
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

def convert_grib1_grib2(grib1_file, grib2_file):
    """! This converts GRIB2 data to GRIB1

         Args:
             grib1_file - string of the path to
                          the GRIB1 file to
                          convert
             grib2_file - string of the path to
                          save the converted GRIB2
                          file

         Returns:
    """
    print("Converting GRIB1 file "+grib1_file+" "
          +"to GRIB2 file "+grib2_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g12 '+grib1_file+' '
              +grib2_file+' > /dev/null 2>&1')

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
        #Uncomment the model_file line below if using default global archive
        #model_file = os.path.join(data_dir, name, model_filename)
        #Uncomment the model_file line below if ARCDIR contains
        #the model experiment name
        model_file = os.path.join(data_dir, model_filename)
        if os.path.exists(model_file):
            if any(g in model_file for g in grib2_file_names):
                convert_grib2_grib1(model_file, link_model_file)
            else:
                #if 'track' in link_filename:
                #    os.system('cp '+model_file+' '+link_model_file)
                #else:
                os.system('ln -sf '+model_file+' '+link_model_file)
        else:
            if run_hpss == 'YES':
                print("Did not find "+model_file+" online..."
                      +"going to try to get file from HPSS")
                if 'enkfgdas' in file_format:
                    model_dump = 'enkfgdas'
                elif 'gdas' in file_format:
                    model_dump = 'gdas'
                elif 'gfs' in file_format:
                    model_dump = 'gfs'
                else:
                    model_dump = name
                if lead_str != 'anl':
                   file_lead = 'f'+lead_str.zfill(3)
                else:
                   file_lead = lead_str
                if 'ensspread' in link_file_format \
                        or 'ensmean' in link_file_format:
                    if 'spread' in file_format:
                        file_type = 'spread'
                    elif 'mean' in file_format:
                        file_type = 'mean'
                    if '.nc4' in file_format:
                        nc_type = 'nc4'
                    else:
                        nc_type = 'nc'
                    (model_hpss_tar, model_hpss_file,
                     model_hpss_job_filename) = set_up_gfs_hpss_info(
                         init_time_dt, hpss_data_dir, model_dump,
                         'atm'+file_lead+'.ens'+file_type+'.'+nc_type,
                         link_data_dir
                    )
                else:
                    (model_hpss_tar, model_hpss_file,
                     model_hpss_job_filename) = set_up_gfs_hpss_info(
                         init_time_dt, hpss_data_dir, model_dump, file_lead,
                         link_data_dir
                    )
                get_hpss_data(model_hpss_job_filename, link_data_dir,
                              link_model_file, model_hpss_tar, model_hpss_file)
    else:
        print("Already got "+link_model_file)
    if not os.path.exists(link_model_file):
        if run_hpss == 'YES':
            print("WARNING: "+model_file+" does not exist and did not find "
                  +"HPSS file "+model_hpss_file+" from "+model_hpss_tar+" or "
                  +"walltime exceeded")
        else:
            print("WARNING: "+model_file+" does not exist")

def create_mean_truth(mean_model_list, mean_model_dir_list,
                      mean_model_file_format_list, valid_time_dt,
                      grid, output_dir):
    """! This creates a mean from a list of model files.

         Args:
             mean_model_list             - list of strings of
                                           model names
             mean_model_dir_list         - list of string of the
                                           model directories
             mean_model_file_format_list - list of strings of the
                                           file formats
             valid_time_dt               - datetime object of
                                           the valid time
             grid                        - the grid verification
                                           is done on, used for
                                           regridding
             output_dir                  - string of path to the
                                           base output
                                           directory

         Returns:
    """
    # Models
    mean_file = os.path.join(
        output_dir, output_dir.rpartition('/')[2]
        +'.'+valid_time_dt.strftime('%Y%m%d%H')
    )
    mean_grib2_file = (mean_file+'.grib2')
    mean_model_file_list = []
    nmean_models = len(mean_model_list)
    # Variables
    variable_name_level_dict = {
        'HGT': ['P1000', 'P850', 'P700', 'P500', 'P250', 'P200', 'P100',
                'P50', 'P20', 'P10', 'P5', 'P1', 'L0_7'],
        'TMP': ['P1000','P850', 'P700', 'P500', 'P250', 'P200', 'P100',
                'P50', 'P20', 'P10', 'P5', 'P1', 'Z2', 'Z0', 'L0_7'],
        'UGRD': ['P1000','P850', 'P700', 'P500', 'P250', 'P200', 'P100',
                 'P50', 'P20', 'P10', 'P5', 'P1', 'Z10'],
        'VGRD': ['P1000','P850', 'P700', 'P500', 'P250', 'P200', 'P100',
                 'P50', 'P20', 'P10', 'P5', 'P1', 'Z10'],
        'O3MR': ['P100', 'P70', 'P50', 'P30', 'P20', 'P10', 'P5', 'P1'],
        'PRMSL': ['Z0'],
        'RH': ['Z2'],
        'SPFH': ['Z2'],
        'HPBL': ['Z0'],
        'PRES': ['Z0', 'L0_7'],
        'TSOIL': ['Z0-10'],
        'SOILW': ['Z0-10'],
        'WEASD': ['Z0'],
        'CAPE': ['Z0'],
        'CWAT': ['L0_200'],
        'PWAT': ['L0_200'],
        'TOZNE': ['L0_200']
    }
    # Executables
    regrid_data_plane = os.path.join(
        os.environ['HOMEMET'], os.environ['HOMEMET_bin_exec'],
        'regrid_data_plane'
    )
    wgrib = os.environ['WGRIB']
    wgrib2 = os.environ['WGRIB2']
    copygb = os.environ['COPYGB']
    ncea = os.environ['NCEA']
    ncdump = os.environ['NCDUMP']
    # Get model files
    for mean_model in mean_model_list:
        mean_model_dir = os.path.join(output_dir, mean_model)
        mean_model_idx = mean_model_list.index(mean_model)
        mean_model_dir = mean_model_dir_list[mean_model_idx]
        mean_model_file_format = mean_model_file_format_list[mean_model_idx]
        save_mean_model_file_format = (
            mean_model_file_format_list[mean_model_idx]\
            .replace('.grib2', '').replace('.grb2', '')
        )
        output_mean_model_dir = os.path.join(output_dir, mean_model)
        if not os.path.exists(output_mean_model_dir):
            os.makedirs(output_mean_model_dir)
        get_model_file(valid_time_dt, valid_time_dt, '00',
                       mean_model, mean_model_dir, mean_model_file_format,
                       'NO', '/null', output_mean_model_dir,
                       save_mean_model_file_format)
        mean_model_file = os.path.join(output_mean_model_dir,
                                       format_filler(
                                           save_mean_model_file_format,
                                           valid_time_dt, valid_time_dt, '00'
                                       ))
        if os.path.exists(mean_model_file):
            mean_model_file_list.append(mean_model_file)
    # Regrid files indivdually for variables for each model, and
    # take mean if available for all models
    # Create invdivdual grib2 template file for variable
    # NCEP only use GFS files for this (center = 7)
    if len(mean_model_file_list) == nmean_models:
        print("Creating mean truth file "+mean_file+" using "
              +', '.join(mean_model_file_list))
        for var_name in variable_name_level_dict:
            for var_level in variable_name_level_dict[var_name]:
                all_models_have_var = True
                create_var_template = True
                mean_model_var_nc_file_list = []
                for mean_model in mean_model_list:
                    mean_model_idx = mean_model_list.index(mean_model)
                    save_mean_model_file_format = mean_model_file_format_list[
                        mean_model_idx
                    ].replace('.grib2', '').replace('.grb2', '')
                    output_mean_model_dir = os.path.join(output_dir,
                                                         mean_model)
                    save_mean_model_file = os.path.join(
                        output_mean_model_dir,
                        format_filler(save_mean_model_file_format,
                                      valid_time_dt, valid_time_dt, '00')
                    )
                    # Create template
                    if create_var_template:
                        output_template_dir = os.path.join(output_dir,
                                                          'template')
                        if not os.path.exists(output_template_dir):
                            os.makedirs(output_template_dir)
                        template_regrid_file = os.path.join(
                            output_template_dir, 'template.'
                            +valid_time_dt.strftime('%Y%m%d%H')+'_regrid'
                        )
                        template_grib2_file = os.path.join(
                            output_template_dir, 'template.'
                            +valid_time_dt.strftime('%Y%m%d%H')+'.grib2'
                        )
                        template_var_grib2_file = os.path.join(
                            output_template_dir, 'template.'
                            +valid_time_dt.strftime('%Y%m%d%H')+'_'
                            +var_name+'_'+var_level+'.grib2'
                        )
                        if not os.path.exists(template_regrid_file):
                            check_center = subprocess.check_output(
                                wgrib+' -V '+save_mean_model_file, shell=True,
                                encoding='UTF-8'
                            )
                            if 'center 7 ' in check_center:
                                os.system(copygb+' -'+grid.lower()+' -x '
                                          +save_mean_model_file+' '
                                          +template_regrid_file+' '
                                          +'> /dev/null 2>&1')
                            if os.path.exists(template_regrid_file):
                                convert_grib1_grib2(template_regrid_file,
                                                    template_grib2_file)
                        if 'P' in var_level:
                            var_level_grib2 = var_level[1:]+' mb'
                        elif 'Z' in var_level:
                            if var_level == 'Z0':
                                if var_name == 'PRMSL':
                                    var_level_grib2 = 'mean sea level'
                                else:
                                    var_level_grib2 = 'surface'
                            elif var_level == 'Z0-10':
                                var_level_grib2 = '0-0.1 m below ground'
                            else:
                                var_level_grib2 = (var_level[1:]+' m above '
                                                   +'ground')
                        elif var_level == 'L0_7':
                            var_level_grib2 = 'tropopause'
                        elif var_level == 'L0_200':
                            var_level_grib2 = ('entire atmosphere ('
                                               +'considered as a single '
                                               +'layer)')
                        if os.path.exists(template_grib2_file):
                            os.system(wgrib2+' '+template_grib2_file+' '
                                      +'-match ":'+var_name+':" '
                                      +'-match ":'+var_level_grib2+':" '
                                      +'-grib_out '
                                      +template_var_grib2_file+' '
                                      +'> /dev/null 2>&1')
                        if os.path.exists(template_var_grib2_file):
                            create_var_template = False
                    # Regrid
                    mean_model_var_nc_file = os.path.join(
                        output_mean_model_dir,
                        format_filler(save_mean_model_file_format,
                                      valid_time_dt, valid_time_dt, '00')+'_'
                        +var_name+'_'+var_level+'.nc'
                    )
                    mean_model_var_nc_file_list.append(
                         mean_model_var_nc_file
                    )
                    nc_var = var_name+'_'+var_level.replace(' ', '')
                    if '_' in var_level:
                        field_info = ("'"+'name="'+var_name+'"; '
                                      +'level="'+var_level.split('_')[0]
                                      +'"; GRIB_lvl_typ='
                                      +var_level.split('_')[1]+";'")
                    else:
                        field_info = ("'"+'name="'+var_name+'"; '
                                      +'level="'+var_level+'";'+"'")
                    run_rdp = subprocess.run(
                        regrid_data_plane+' '+save_mean_model_file+' '
                        +grid+' '+mean_model_var_nc_file+' '
                        +'-field '+field_info+' -method BILIN '
                        +'-width 2 -name '+nc_var+' -v 1 '
                        +'> /dev/null 2>&1', shell=True
                    )
                    if run_rdp.returncode != 0:
                        all_models_have_var = False
                # Take mean
                if all_models_have_var:
                    mean_var_nc_file = (mean_file+'_'+var_name+'_'
                                        +var_level+'.nc')
                    os.system(ncea+' '
                              +' '.join(mean_model_var_nc_file_list)+' '
                              +'-O -o '+mean_var_nc_file)
                    lat_dim_output = subprocess.check_output(
                        ncdump+' -h '+mean_var_nc_file+' '
                        +'| grep ":Nlat = "', shell=True,
                        encoding='UTF-8'
                    )
                    lat_dim = ''
                    for string in lat_dim_output:
                        if string.isdigit():
                            lat_dim = lat_dim + string
                    lon_dim_output = subprocess.check_output(
                        ncdump+' -h '+mean_var_nc_file+' '
                        +'| grep ":Nlon = "', shell=True,
                        encoding='UTF-8'
                    )
                    lon_dim = ''
                    for string in lon_dim_output:
                        if string.isdigit():
                            lon_dim = lon_dim + string
                    # Fill using template
                    os.environ['HDF5_DISABLE_VERSION_CHECK'] = '1'
                    mean_var_grib2_file = (mean_file+'_'+var_name+'_'
                                           +var_level+'.grib2')
                    os.system(wgrib2+' '
                              +template_var_grib2_file+' '
                              +'-import_netcdf '
                              +mean_var_nc_file+' '
                              +'"'+nc_var+'" "0:'+lat_dim+':0:'
                              +lon_dim+'"  -grib_out '
                              +mean_var_grib2_file+' '
                              +'> /dev/null 2>&1')
                    os.system('cat '+mean_var_grib2_file+' >> '
                              +mean_grib2_file)
        # Convert mean analysis to grib1
        if os.path.exists(mean_grib2_file):
            convert_grib2_grib1(mean_grib2_file, mean_file)
        if os.path.exists(mean_file):
            print("Created "+mean_file)
    else:
        print("WARNING: Do not have all files to create "+mean_file+" from "
              +"models "+', '.join(mean_model_list)+", only have files "
              +', '.join(mean_model_file_list))

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
                                        valid_time_dt.strftime('%H')+'Z', name,
                                        name+'_'
                                        +valid_time_dt.strftime('%Y%m%d')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                             +valid_time_dt.strftime('%Y%m%d')
                                             +'_valid'
                                             +valid_time_dt.strftime('%H')
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
         if RUN_dir_name in ['grid2grid', 'satellite']:
             model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                            valid_time_dt.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time_dt.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time_dt.strftime(
                                                     '%Y%m%d'
                                                 )
                                                 +'_valid'
                                                 +valid_time_dt.strftime('%H')
                                                 +'.stat')
         elif RUN_dir_name in ['grid2obs', 'precip']:
             model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                            init_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time_dt.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time_dt.strftime(
                                                     '%Y%m%d'
                                                 )
                                                 +'_init'
                                                 +init_time.strftime('%H')
                                                 +'.stat')
    if not os.path.exists(link_model_stat_file):
        if os.path.exists(model_stat_file):
            os.system('ln -sf '+model_stat_file+' '+link_model_stat_file)
        else:
            print("WARNING: "+model_stat_file+" does not exist")

# Read in common environment variables
RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
spinup_period_start = os.environ['spinup_period_start']
spinup_period_end = os.environ['spinup_period_end']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
machine = os.environ['machine']
RUN_abbrev = os.environ['RUN_abbrev']
RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Set up spin up period
check_spinup_period = False
if spinup_period_start != 'NA' and spinup_period_end != 'NA':
    check_spinup_period = True
    spinup_period_start_dt = datetime.datetime.strptime(
        spinup_period_start, '%Y%m%d%H'
    )
    spinup_period_end_dt = datetime.datetime.strptime(
        spinup_period_end, '%Y%m%d%H'
    )

# Set some common varaibles
hpss_prod_base_dir = '/NCEPPROD/hpssprod/runhistory'
cwd = os.getcwd()

# No HPSS access from Orion or Hercules
if machine in ['ORION', 'HERCULES']:
    print("WARNING: "+machine+" does not currently have access to HPSS..."
          +"setting model_data_runhpss to NO")
    model_data_run_hpss = 'NO'

if RUN == 'grid2grid_step2':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
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
            link_model_RUN_type_dir = os.path.join(cwd, 'data',
                                                   model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'grid2grid', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'grid2obs_step2':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
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
            link_model_RUN_type_dir = os.path.join(cwd, 'data',
                                                        model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'grid2obs', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'precip_step2':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
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
            link_model_RUN_type_dir = os.path.join(cwd, 'data',
                                                   model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'precip', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'satellite_step2':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
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
            link_model_RUN_type_dir = os.path.join(cwd, 'data',
                                                        model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'satellite', RUN_type,
                                        link_model_RUN_type_dir)

print("END: "+os.path.basename(__file__))
