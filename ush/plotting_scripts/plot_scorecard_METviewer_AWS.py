'''
Program Name: plot_scorecard_METviewer_AWS.py
Contact(s): Mallory Row
Abstract: This scripts generates a standard GFS grid-to-grid
          scorecard from METviewer AWS.
              1) Create scorecard XML
              2) Create and send batch job card for scorecard
              3) Send scorecard to website
'''

import sys
import datetime as datetime
import shutil
import os
import subprocess
from time import sleep

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
machine = os.environ['machine']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
USHverif_global = os.environ['USHverif_global']
model_list = os.environ['model_list'].split(' ')
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
SEND2WEB = os.environ['SEND2WEB']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
mv_database_list = os.environ['g2g2_sc_mv_database_list'].split(' ')
valid_beg = os.environ['g2g2_sc_valid_start_date']
valid_end = os.environ['g2g2_sc_valid_end_date']
fcyc_list = os.environ['g2g2_sc_fcyc_list'].split(' ')
vhr_list = os.environ['g2g2_sc_vhr_list'].split(' ')

# Set up job wall time information
web_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()
METviewer_AWS_scripts_dir = os.path.join(USHverif_global,
                                         'METviewer_AWS_scripts')

# Do some formatting for XML variables
valid_beg_dt = datetime.datetime.strptime(valid_beg+vhr_list[0], '%Y%m%d%H')
valid_end_dt = datetime.datetime.strptime(valid_end+vhr_list[-1], '%Y%m%d%H')
fcst_valid_beg = valid_beg_dt.strftime('%Y-%m-%d %H:%M:%S')
fcst_valid_end = valid_end_dt.strftime('%Y-%m-%d %H:%M:%S')
gendate_dt = datetime.datetime.utcnow()
gendate = gendate_dt.strftime('%Y%m%d%H%M%S')

# Create load XML, create job card and submit it
modelA = model_list[0]
for modelB in model_list[1:]:
    # Create XML
    scorecard_xml_file = os.path.join(DATA, RUN, 'metplus_output', 'scorecard',
                                      'scorecard_'+modelA+'_'+modelB+'.xml')
    print("Creating scorecard XML for "+modelA+" and "+modelB+" "
          +scorecard_xml_file)
    if os.path.exists(scorecard_xml_file):
        os.remove(scorecard_xml_file)
    with open(scorecard_xml_file, 'a') as xml:
        xml.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        xml.write('<plot_spec>\n')
        xml.write('  <connection>\n')
        xml.write('    <host>metviewer-dev-cluster.cluster-czbts4gd2wm2'
                  +'.us-east-1.rds.amazonaws.com:3306</host>\n')
        xml.write('    <database>'+','.join(mv_database_list)+'</database>\n')
        xml.write('    <user>rds_user</user>\n')
        xml.write('    <password>rds_pwd</password>\n')
        xml.write('  </connection>\n')
        xml.write('\n')
        xml.write('  <rscript>Rscript</rscript>\n')
        xml.write('\n')
        xml.write('  <folders>\n')
        xml.write('    <r_tmpl>rds_R_tmpl</r_tmpl>\n')
        xml.write('    <r_work>rds_R_work</r_work>\n')
        xml.write('    <plots>rds_plots</plots>\n')
        xml.write('    <data>rds_data</data>\n')
        xml.write('    <scripts>rds_scripts</scripts>\n')
        xml.write('  </folders>\n')
        xml.write('\n')
        xml.write('  <plot>\n')
        xml.write('    <view_value>false</view_value>\n')
        xml.write('    <view_symbol>true</view_symbol>\n')
        xml.write('    <view_legend>true</view_legend>\n')
        xml.write('    <printSQL>true</printSQL>\n')
        xml.write('    <stat_flag>EMC</stat_flag>\n')
        xml.write('    <stat>DIFF_SIG</stat>\n')
        xml.write('\n')
        xml.write('    <template>scorecard.R_tmpl</template>\n')
        xml.write('\n')
        xml.write('    <plot_fix>\n')
        xml.write('      <field name="model">\n')
        xml.write('        <val name="'+modelB+'" />\n')
        xml.write('        <val name="'+modelA+'" />\n')
        xml.write('      </field>\n')
        xml.write('      <field name="fcst_valid_beg">\n')
        xml.write('        <val name="'+fcst_valid_beg+'" />\n')
        xml.write('        <val name="'+fcst_valid_end+'" />\n')
        xml.write('      </field>\n')
        xml.write('      <field name="init_hour">\n')
        for fcyc in fcyc_list:
            xml.write('        <val name="'+fcyc+'" />\n')
        xml.write('      </field>\n')
        xml.write('      <field name="valid_hour">\n')
        for vhr in vhr_list:
            xml.write('        <val name="'+vhr+'" />\n')
        xml.write('      </field>\n')
        xml.write('      <field name="interp_mthd">\n')
        xml.write('        <val name="NEAREST" />\n')
        xml.write('      </field>\n')
        xml.write('    </plot_fix>\n')
        xml.write('\n')
        xml.write('    <rows>\n')
        xml.write('      <field name="stat">\n')
        xml.write('      <val name="ANOM_CORR" '
                  +'label="Anomaly Correlation"/>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="HGT" label="Heights"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P250" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="TMP" label="Temp"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P250" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="PRMSL" label="MSL Pres."/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="Z0" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="stat">\n')
        xml.write('        <val name="VAL1L2_ANOM_CORR" '
                  +'label="Anomaly Correlation"/>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="UGRD_VGRD" label="Vector Wind"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P250" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="stat">\n')
        xml.write('        <val name="RMSE" />\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="HGT" label="Heights"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="TMP" label="Temp"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="stat">\n')
        xml.write('        <val name="VL1L2_RMSVE" label="RMSE"/>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="UGRD_VGRD" label="Vector Wind"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="stat">\n')
        xml.write('        <val name="ME" label="Bias" />\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="HGT" label="Heights"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="TMP" label="Temp"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="stat">\n')
        xml.write('        <val name="VL1L2_BIAS" label="Bias"/>\n')
        xml.write('        <field name="fcst_var">\n')
        xml.write('          <val name="UGRD_VGRD" label="Wind Speed"/>\n')
        xml.write('          <field name="fcst_lev">\n')
        xml.write('            <val name="P10" />\n')
        xml.write('            <val name="P20" />\n')
        xml.write('            <val name="P50" />\n')
        xml.write('            <val name="P100" />\n')
        xml.write('            <val name="P200" />\n')
        xml.write('            <val name="P500" />\n')
        xml.write('            <val name="P700" />\n')
        xml.write('            <val name="P850" />\n')
        xml.write('            <val name="P1000" />\n')
        xml.write('          </field>\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('    </rows>\n')
        xml.write('\n')
        xml.write('    <columns>\n')
        xml.write('      <field name="vx_mask">\n')
        xml.write('        <val name="PNA" label="N.America" />\n')
        xml.write('        <field name="fcst_lead">\n')
        xml.write('          <val name="240000" label="Day 1" />\n')
        xml.write('          <val name="720000" label="Day 3" />\n')
        xml.write('          <val name="1200000" label="Day 5" />\n')
        xml.write('          <val name="1440000" label="Day 6" />\n')
        xml.write('          <val name="1920000" label="Day 8" />\n')
        xml.write('          <val name="2400000" label="Day 10" />\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="vx_mask">\n')
        xml.write('        <val name="NHX" label="N.Hemisphere" />\n')
        xml.write('        <field name="fcst_lead">\n')
        xml.write('          <val name="240000" label="Day 1" />\n')
        xml.write('          <val name="720000" label="Day 3" />\n')
        xml.write('          <val name="1200000" label="Day 5" />\n')
        xml.write('          <val name="1440000" label="Day 6" />\n')
        xml.write('          <val name="1920000" label="Day 8" />\n')
        xml.write('          <val name="2400000" label="Day 10" />\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="vx_mask">\n')
        xml.write('        <val name="SHX" label="S.Hemisphere" />\n')
        xml.write('        <field name="fcst_lead">\n')
        xml.write('          <val name="240000" label="Day 1" />\n')
        xml.write('          <val name="720000" label="Day 3" />\n')
        xml.write('          <val name="1200000" label="Day 5" />\n')
        xml.write('          <val name="1440000" label="Day 6" />\n')
        xml.write('          <val name="1920000" label="Day 8" />\n')
        xml.write('          <val name="2400000" label="Day 10" />\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('\n')
        xml.write('      <field name="vx_mask">\n')
        xml.write('        <val name="TRO" label="Tropics" />\n')
        xml.write('        <field name="fcst_lead">\n')
        xml.write('          <val name="240000" label="Day 1" />\n')
        xml.write('          <val name="720000" label="Day 3" />\n')
        xml.write('          <val name="1200000" label="Day 5" />\n')
        xml.write('          <val name="1440000" label="Day 6" />\n')
        xml.write('          <val name="1920000" label="Day 8" />\n')
        xml.write('          <val name="2400000" label="Day 10" />\n')
        xml.write('        </field>\n')
        xml.write('      </field>\n')
        xml.write('    </columns>\n')
        xml.write('\n')
        xml.write('    <agg_stat>false</agg_stat>\n')
        xml.write('    <boot_repl>1000</boot_repl>\n')
        xml.write('    <boot_random_seed>1</boot_random_seed>\n')
        xml.write('\n')
        xml.write('    <tmpl>\n')
        xml.write('      <data_file>scorecard_met_emc_'
                  +modelA+'_'+modelB+'_gen'+gendate+'.data</data_file>\n')
        xml.write('      <plot_file>scorecard_met_emc_'
                  +modelA+'_'+modelB+'_gen'+gendate+'.png</plot_file>\n')
        xml.write('      <title>'+modelB+' vs '+modelA+'</title>\n')
        xml.write('    </tmpl>\n')
        xml.write('\n')
        xml.write('  </plot>\n')
        xml.write('</plot_spec>\n')
    if modelB == model_list[1]:
        scorecard2web = (
            'scorecard_met_emc_'+modelA+'_'+modelB+'_gen'+gendate+'.png'
        )
    # Create job card file for:
    #   Create scorecard
    #   mv_scorecard_on_aws.sh agruments:
    #      1 - username
    #      2 - scorecard_dir
    #      3 - XML file
    AWS_job_filename = os.path.join(DATA, 'batch_jobs',
                                    NET+'_'+RUN+'_scorecard_METviewerAWS_'
                                    +modelA+'_'+modelB+'.sh')
    with open(AWS_job_filename, 'a') as AWS_job_file:
        AWS_job_file.write('#!/bin/sh'+'\n')
        AWS_job_file.write('echo "Creating scorecard on METviewer AWS using '
                           +os.path.join(METviewer_AWS_scripts_dir,
                                         'mv_scorecard_on_aws.sh')
                           +'"\n')
        AWS_job_file.write(
            os.path.join(METviewer_AWS_scripts_dir,
                         'mv_scorecard_on_aws.sh')+' '
            +os.environ['USER'].lower()+' '
            +os.path.join(DATA, RUN, 'metplus_output', 'scorecard')+' '
            +scorecard_xml_file+'\n'
        )
    # Submit job card
    os.chmod(AWS_job_filename, 0o755)
    AWS_job_output = AWS_job_filename.replace('.sh', '.out')
    AWS_job_name = AWS_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+AWS_job_filename+" to "+QUEUESERV)
    print("Output sent to "+AWS_job_output)
    if machine == 'WCOSS_C':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+AWS_job_output+' -e '
                  +AWS_job_output+' '
                  +'-J '+AWS_job_name+' -R rusage[mem=2048] '+AWS_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+AWS_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'WCOSS_DELL_P3':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+AWS_job_output+' -e '
                  +AWS_job_output+' '
                  +'-J '+AWS_job_name+' -M 2048 -R "affinity[core(1)]" '
                  +AWS_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+AWS_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'HERA':
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+AWS_job_output+' '
                  +'--job-name='+AWS_job_name+' '+AWS_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +AWS_job_name+' -t R,PD -h | wc -l')
    sleep_counter, sleep_checker = 1, 10
    while (sleep_counter*sleep_checker) <= walltime_seconds:
        sleep(sleep_checker)
        print("Walltime checker: "+str(sleep_counter*sleep_checker)+" "
              +"out of "+str(int(walltime_seconds))+" seconds")
        check_job = subprocess.check_output(job_check_cmd, shell=True)
        if check_job[0] == '0':
            break
        sleep_counter+=1

# Send to website
if SEND2WEB == 'YES':
    print("Webhost: "+webhost)
    print("Webhost location: "+webdir)
    # Create job card
    web_job_filename = os.path.join(DATA, 'batch_jobs',
                                    NET+'_'+RUN
                                    +'_scorecard_METviewerAWS_web.sh')
    with open(web_job_filename, 'a') as web_job_file:
        web_job_file.write('#!/bin/sh'+'\n')
        web_job_file.write('ssh -q -l '+webhostid+' '+webhost+' " ls -l '
                           +webdir+' "'+'\n')
        web_job_file.write('if [ $? -ne 0 ]; then'+'\n')
        web_job_file.write('    echo "Making directory '+webdir+'"'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "mkdir -p '+webdir+' "'+'\n')
        web_job_file.write('    scp -q '+os.path.join(USHverif_global,
                                                      'webpage.tar')+'  '
                           +webhostid+'@'+webhost+':'+webdir+'/.'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "cd '+webdir+' ; tar -xvf webpage.tar "'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "rm '+os.path.join(webdir, 'webpage.tar')
                           +' "'+'\n')
        web_job_file.write('fi'+'\n')
        web_job_file.write('\n')
        web_job_file.write('scp -r '+os.path.join(DATA, RUN,
                                                  'metplus_output',
                                                  'scorecard/'
                                                  +scorecard2web)
                           +' '+webhostid+'@'+webhost+':'
                           +os.path.join(webdir, 'scorecard', 'images', 
                                         'scorecard.png'))
    # Submit job card
    os.chmod(web_job_filename, 0o755)
    web_job_output = web_job_filename.replace('.sh', '.out')
    web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+web_job_filename+" to "+QUEUESERV)
    print("Output sent to "+web_job_output)
    if machine == 'WCOSS_C':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+web_job_output+' -e '
                  +web_job_output+' '
                  +'-J '+web_job_name+' -R rusage[mem=2048] '+web_job_filename)
    elif machine == 'WCOSS_DELL_P3':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+web_job_output+' -e '+web_job_output+' '
                  +'-J '+web_job_name+' -M 2048 -R "affinity[core(1)]" '
                  +web_job_filename)
    elif machine == 'HERA':
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)

print("END: "+os.path.basename(__file__))
