'''
Program Name: run_batch.py
Contact(s): Mallory Row
Abstract: This script is run by run_verif_global.sh.
          It creates a job card for the verification
          script to run and submits it.
'''

from __future__ import (print_function, division)
import os
import sys
import subprocess

print("BEGIN: "+os.path.basename(__file__))

# Read in script agruments
machine = sys.argv[1]
script = sys.argv[2]

# Read in environment variables
NET = os.environ['NET']
RUN = os.environ['RUN']
QUEUE = os.environ['QUEUE']
ACCOUNT = os.environ['ACCOUNT']
nproc = os.environ['nproc']

# Create job card directory and file name
cwd = os.getcwd()
batch_job_dir = os.path.join(cwd, 'batch_jobs')
if not os.path.exists(batch_job_dir):
    os.makedirs(batch_job_dir)
job_card_filename = os.path.join(batch_job_dir, 
                                 NET+'_'+RUN+'.sh')
job_output_filename = os.path.join(batch_job_dir,
                                   NET+'_'+RUN+'.out')
job_name = NET+'_'+RUN

# Create job card
print("Writing job card to "+job_card_filename)
with open(job_card_filename, 'a') as job_card:
    if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
        job_card.write('#!/bin/sh\n')
        job_card.write('#BSUB -q '+QUEUE+'\n')
        job_card.write('#BSUB -P '+ACCOUNT+'\n')
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
            if RUN in ['grid2grid_step2', 'grid2obs_step2']:
                job_card.write('#BSUB -n '+str(int(nproc)*3)+'\n')
            elif RUN == 'maps2d':
                job_card.write('#BSUB -n '+str(int(nproc)*4)+'\n')
            else:
                job_card.write('#BSUB -n '+nproc+'\n')
            job_card.write('#BSUB -R "span[ptile='+nproc+']"\n')
            job_card.write('#BSUB -R affinity[core(1):distribute=balance]\n')
    elif machine == 'HERA':
        job_card.write('#!/bin/sh --login\n')
        job_card.write('#SBATCH --qos='+QUEUE+'\n')
        job_card.write('#SBATCH --account='+ACCOUNT+'\n')
        job_card.write('#SBATCH --job-name='+job_name+'\n')
        job_card.write('#SBATCH --output='+job_output_filename+'\n')
        job_card.write('#SBATCH --mem=3g\n')
        job_card.write('#SBATCH --nodes=1\n')
        job_card.write('#SBATCH --ntasks-per-node='+nproc+'\n')
        #job_card.write('#SBATCH --ntasks=1\n')
        job_card.write('#SBATCH --time=6:00:00\n')
    job_card.write('\n')
    job_card.write('/bin/sh '+script)
   
# Submit job card 
print("Submitting "+job_card_filename+" to "+QUEUE)
print("Output sent to "+job_output_filename)
if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
    os.system('bsub < '+job_card_filename)
elif machine == 'HERA':
    os.system('sbatch '+job_card_filename)

print("END: "+os.path.basename(__file__))
