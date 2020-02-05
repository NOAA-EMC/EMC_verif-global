'''
Program Name: build_webpage.py
Contact(s): Mallory Row
Abstract: This is run at the end of all step2 scripts
          in scripts/.
          This creates a job card to:
              1) if needed, create website from
                 EMC_verif-global template (webpage.tar) 
                 at specified user location on web server
              2) send images to web server
          It then submits to the transfer queue.
'''

import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
machine = os.environ['machine']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
RUN_type = RUN.split('_')[0]
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
print("Webhost: "+webhost)
print("Webhost location: "+webdir)

# Set up job wall time information
web_walltime = '60' 
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

# Create job card
web_job_filename = os.path.join(DATA, 'batch_jobs',
                                NET+'_'+RUN+'_web.sh')
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
        web_job_file.write('scp -r '+os.path.join(DATA, RUN, 'metplus_output',
                                                  'images')
                           +' '+webhostid+'@'+webhost+':'
                           +os.path.join(webdir, RUN_type, '.')+'\n')
        if RUN == 'tropcyc':
            for tropcyc_type in ['intensityerr', 'trackerr']:
                web_job_file.write(
                    'scp -r '+os.path.join(DATA, RUN,
                                           'create_webpage_templates',
                                           tropcyc_type, tropcyc_type+'*.php')
                    +' '+webhostid+'@'+webhost+':'
                    +os.path.join(webdir, RUN_type, tropcyc_type, '.\n')
                )

# Submit job card
os.chmod(web_job_filename, 0o755)
web_job_output = web_job_filename.replace('.sh', '.out')
web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+web_job_filename+" to "+QUEUESERV)
print("Output sent to "+web_job_output)
if machine == 'WCOSS_C':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
              +'-P '+ACCOUNT+' -o '+web_job_output+' -e '+web_job_output+' '
              +'-J '+web_job_name+' -R rusage[mem=2048] '+web_job_filename)
elif machine == 'WCOSS_DELL_P3':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
              +'-P '+ACCOUNT+' -o '+web_job_output+' -e '+web_job_output+' '
              +'-J '+web_job_name+' -M 2048 -R "affinity[core(1)]" '+web_job_filename)
elif machine == 'HERA':
    os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
              +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
              +'--output='+web_job_output+' '
              +'--job-name='+web_job_name+' '+web_job_filename)

print("END: "+os.path.basename(__file__))
