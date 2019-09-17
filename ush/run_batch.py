##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Create job card to submit to queue
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

from __future__ import (print_function, division)
import os
import sys
import subprocess

print("BEGIN: "+os.path.basename(__file__))
machine = sys.argv[1]
script = sys.argv[2]

net = os.environ['NET']
run = os.environ['RUN']
queue = os.environ['QUEUE']
account = os.environ['ACCOUNT']
nproc = os.environ['nproc']

cwd = os.getcwd()
batch_job_dir = os.path.join(cwd, 'batch_jobs')
if not os.path.exists(batch_job_dir):
    os.makedirs(batch_job_dir)

job_card_filename = os.path.join(batch_job_dir, 
                                 net+'_'+run+'.sh')
job_output_filename = batch_job_dir+'/'+net+'_'+run+'.out'
job_name = net+'_'+run

print("Writing job card to "+job_card_filename)
with open(job_card_filename, 'a') as job_card:
    if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
        job_card.write('#!/bin/sh\n')
        job_card.write('#BSUB -q '+queue+'\n')
        job_card.write('#BSUB -P '+account+'\n')
        job_card.write('#BSUB -J '+job_name+'\n')
        job_card.write('#BSUB -o '+job_output_filename+'\n')
        job_card.write('#BSUB -e '+job_output_filename+'\n')
        job_card.write('#BSUB -W 6:00\n')
        job_card.write('#BSUB -M 3000\n')
        if machine == 'WCOSS_C':
            job_card.write("#BSUB -extsched 'CRAYLINUX[]' -R '1*"
                           "{select[craylinux && !vnode]} + "
                           +nproc+"*{select[craylinux && vnode]"
                           "span[ptile=24] cu[type=cabinet]}'")
        elif machine == 'WCOSS_DELL_P3':
            job_card.write('#BSUB -n '+nproc+'\n')
            job_card.write('#BSUB -R "span[ptile='+nproc+']"\n')
            job_card.write('#BSUB -R affinity[core(1):distribute=balance]\n')
    elif machine == 'THEIA' or machine == 'HERA':
        job_card.write('#!/bin/sh --login\n')
        job_card.write('#SBATCH --qos='+queue+'\n')
        job_card.write('#SBATCH --account='+account+'\n')
        job_card.write('#SBATCH --job-name='+job_name+'\n')
        job_card.write('#SBATCH --output='+job_output_filename+'\n')
        job_card.write('#SBATCH --mem=3g\n')
        job_card.write('#SBATCH --nodes=1\n')
        job_card.write('#SBATCH --ntasks-per-node='+nproc+'\n')
        #job_card.write('#SBATCH --ntasks=1\n')
        job_card.write('#SBATCH --time=6:00:00\n')
    job_card.write('\n')
    job_card.write('/bin/sh '+script)
    
print("Submitting "+job_card_filename+" to "+queue)
print("Output sent to "+job_output_filename)
if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
    os.system('bsub < '+job_card_filename)
elif machine == 'THEIA' or machine == 'HERA':
    os.system('sbatch '+job_card_filename)

print("END: "+os.path.basename(__file__))
