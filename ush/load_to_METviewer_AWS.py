'''
Program Name: load_to_METviewer_AWS.py
Contact(s): Mallory Row
Abstract: This is run at the end of all step1 scripts
          in scripts/.
          This scripts loads data to the METviewer AWS
          server.
              1) Create a temporary directory and 
                 link the files that are to be 
                 loaded
              2) Create XML that will load files
              3) Create database on AWS server
              4) Listing of METviewer datbases
'''

import sys
import datetime
import shutil
import os 
import subprocess

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
machine = os.environ['machine']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
RUN_type = RUN.split('_')[0]
USHverif_global = os.environ['USHverif_global']
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
MET_version = os.environ['MET_version']
model_list = os.environ['model_list'].split(' ')
web_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

# Get database information
if RUN == 'grid2grid_step1':
    mv_database = os.environ['g2g1_mv_database_name']
    mv_group = os.environ['g2g1_mv_database_group']
    mv_desc = os.environ['g2g1_mv_database_desc']
    gather_by = os.environ['g2g1_gather_by']
    subdir_list = os.environ['g2g1_type_list'].split(' ')
elif RUN == 'grid2obs_step1':
    mv_database = os.environ['g2o1_mv_database_name']
    mv_group = os.environ['g2o1_mv_database_group']
    mv_desc = os.environ['g2o1_mv_database_desc']
    gather_by = os.environ['g2o1_gather_by']
    subdir_list = os.environ['g2o1_type_list'].split(' ')
elif RUN == 'precip_step1':
    mv_database = os.environ['precip1_mv_database_name']
    mv_group = os.environ['precip1_mv_database_group']
    mv_desc = os.environ['precip1_mv_database_desc']
    gather_by = os.environ['precip1_gather_by']
    subdir_list = os.environ['precip1_type_list'].split(' ')
data_dir = os.path.join(os.getcwd(), 'metplus_output', 
                        'gather_by_'+gather_by, 'stat_analysis')
METviewer_AWS_scripts_dir = os.path.join(USHverif_global,
                                         'METviewer_AWS_scripts')

# Check current databases to see if it exists
current_database_info = subprocess.check_output(
    [os.path.join(METviewer_AWS_scripts_dir, 'mv_db_size_on_aws.sh'),
     os.environ['USER'].lower()]
)
if mv_database in current_database_info:
    new_or_add = 'add'
else:
    new_or_add = 'new'

# Create linking file dir
link_file_dir = os.path.join(os.getcwd(), 'metviewerAWS_files')
os.makedirs(link_file_dir, mode=0775)

# Create load XML
load_xml_file = os.path.join(os.getcwd(), 'load_'+mv_database+'.xml')
print("Creating load xml "+load_xml_file)
if new_or_add == 'new':
    drop_index = 'false'
else:
    drop_index = 'true'
if os.path.exists(load_xml_file):
    os.remove(load_xml_file)
with open(load_xml_file, 'a') as xml:
    xml.write('<load_spec>\n')
    xml.write('  <connection>\n')
    xml.write('    <host>metviewer-dev-cluster.cluster-czbts4gd2wm2.'
              +'us-east-1.rds.amazonaws.com:3306</host>\n')
    xml.write('    <database>'+mv_database+'</database>\n')
    xml.write('    <user>rds_user</user>\n')
    xml.write('    <password>rds_pwd</password>\n')
    xml.write('    <management_system>aurora</management_system>\n')
    xml.write('  </connection>\n')
    xml.write('\n')
    xml.write('  <met_version>V'+MET_version+'</met_version>\n')
    xml.write('\n')
    xml.write('  <verbose>true</verbose>\n')
    xml.write('  <insert_size>1</insert_size>\n')
    xml.write('  <mode_header_db_check>true</mode_header_db_check>\n')
    xml.write('  <stat_header_db_check>true</stat_header_db_check>\n')
    xml.write('  <drop_indexes>'+drop_index+'</drop_indexes>\n')
    xml.write('  <apply_indexes>true</apply_indexes>\n')
    xml.write('  <load_stat>true</load_stat>\n')
    xml.write('  <load_mode>true</load_mode>\n')
    xml.write('  <load_mpr>true</load_mpr>\n')
    xml.write('  <load_orank>true</load_orank>\n')
    xml.write('  <force_dup_file>false</force_dup_file>\n')
    xml.write('  <group>'+mv_group+'</group>\n')
    xml.write('  <description>'+mv_desc+'</description>\n')
    xml.write('  <load_files>\n')
for subdir in subdir_list:
    for model in model_list:
        for file_name in os.listdir(os.path.join(data_dir, subdir, model)):
            os.link(
                os.path.join(data_dir, subdir, model, file_name), 
                os.path.join(link_file_dir, subdir+'_'+file_name)
            )
            with open(load_xml_file, 'a') as xml:
                xml.write('    <file>/base_dir/'
                          +subdir+'_'+file_name+'</file>\n')
with open(load_xml_file, 'a') as xml:
    xml.write('  </load_files>\n')
    xml.write('\n')
    xml.write('</load_spec>')

# Create job card file for:
#   Create database if needed and load data
#   mv_create_db_on_aws.sh agruments:
#      1 - username
#      2 - database name
#   mv_load_to_aws.sh agruments:
#      1 - username
#      2 - base dir
#      3 - XML file
#      4 (opt) - sub dir
AWS_job_filename = os.path.join(DATA, 'batch_jobs',
                                NET+'_'+RUN+'_load2METviewerAWS.sh')
with open(AWS_job_filename, 'a') as AWS_job_file:
    AWS_job_file.write('#!/bin/sh'+'\n')
    if new_or_add == 'new':
        AWS_job_file.write('echo "Creating database on METviewer AWS using '
                           +os.path.join(METviewer_AWS_scripts_dir,
                                         'mv_create_db_on_aws.sh')
                           +'"\n')
        AWS_job_file.write(
            os.path.join(METviewer_AWS_scripts_dir,
                         'mv_create_db_on_aws.sh')+' '
            +os.environ['USER'].lower()+' '
            +mv_database+'\n'
        )
    AWS_job_file.write('echo "Loading data to METviewer AWS using '
                       +os.path.join(METviewer_AWS_scripts_dir,
                                     'mv_load_to_aws.sh')
                       +'"\n')
    AWS_job_file.write(
        os.path.join(METviewer_AWS_scripts_dir, 'mv_load_to_aws.sh')+' '
        +os.environ['USER'].lower()+' '
        +link_file_dir+' '
        +load_xml_file+'\n'
    )
    AWS_job_file.write('echo "Check METviewer AWS database list using '
                       +os.path.join(METviewer_AWS_scripts_dir,
                                     'mv_db_size_on_aws.sh')
                      +'"\n')
    AWS_job_file.write(
        os.path.join(METviewer_AWS_scripts_dir, 'mv_db_size_on_aws.sh')+' '
        +os.environ['USER'].lower()
    )

# Submit job card
os.chmod(AWS_job_filename, 0o755)
AWS_job_output = AWS_job_filename.replace('.sh', '.out')
AWS_job_name = AWS_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+AWS_job_filename+" to "+QUEUESERV)
print("Output sent to "+AWS_job_output)
if machine == 'WCOSS_C':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
              +'-P '+ACCOUNT+' -o '+AWS_job_output+' -e '+AWS_job_output+' '
              +'-J '+AWS_job_name+' -R rusage[mem=2048] '+AWS_job_filename)
elif machine == 'WCOSS_DELL_P3':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
              +'-P '+ACCOUNT+' -o '+AWS_job_output+' -e '+AWS_job_output+' '
              +'-J '+AWS_job_name+' -M 2048 -R "affinity[core(1)]" '+AWS_job_filename)
elif machine == 'HERA':
    os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
              +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
              +'--output='+AWS_job_output+' '
              +'--job-name='+AWS_job_name+' '+AWS_job_filename)

print("END: "+os.path.basename(__file__))
