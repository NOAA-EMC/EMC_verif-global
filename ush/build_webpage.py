import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

machine = os.environ['machine']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
net = os.environ['NET']
run = os.environ['RUN']
run_type = run.split('_')[0]
queueserv = os.environ['QUEUESERV']
account = os.environ['ACCOUNT']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
web_walltime = '60' 
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

print("Webhost: "+webhost)
print("Webhost location: "+webdir)

web_job_filename = os.path.join(DATA, 'batch_jobs',
                                net+'_'+run+'_web.sh')
with open(web_job_filename, 'a') as web_job_file:
        web_job_file.write('#!/bin/sh'+'\n')
        web_job_file.write('ssh -q -l '+webhostid+' '+webhost+' " ls -l '+webdir+' "'+'\n')
        web_job_file.write('if [ $? -ne 0 ]; then'+'\n')
        web_job_file.write('    echo "Making directory '+webdir+'"'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                            +' " mkdir -p '+webdir+' "'+'\n')
        web_job_file.write('    scp -q '+USHverif_global+'/webpage.tar  '
                            +webhostid+'@'+webhost+':'+webdir+'/.'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                            +' "cd '+webdir+' ; tar -xvf webpage.tar "'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                            +' "rm '+webdir+'/webpage.tar "'+'\n')
        web_job_file.write('fi'+'\n')
        web_job_file.write('\n')
        web_job_file.write('scp -r '+os.path.join(DATA, run, 'metplus_output', 'images/*')
                           +' '+webhostid+'@'+webhost+':'+webdir+'/'+run_type+'/images/.')
os.chmod(web_job_filename, 0o755)
web_job_output = web_job_filename.replace('.sh', '.out')
web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+web_job_filename+" to "+queueserv)
print("Output sent to "+web_job_output)
if machine == 'WCOSS_C':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+queueserv+' '
              '-P '+account+' -o '+web_job_output+' -e '+web_job_output+' '
              '-J '+web_job_name+' -R rusage[mem=2048] '+web_job_filename)
elif machine == 'WCOSS_DELL_P3':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+queueserv+' '
              '-P '+account+' -o '+web_job_output+' -e '+web_job_output+' '
              '-J '+web_job_name+' -M 2048 -R "affinity[core(1)]" '+web_job_filename)
elif machine == 'THEIA' or machine == 'HERA':
    os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
              '--partition='+queueserv+' --account='+account+' '
              '--output='+web_job_output+' '
              '--job-name='+web_job_name+' '+web_job_filename)

print("END: "+os.path.basename(__file__))
