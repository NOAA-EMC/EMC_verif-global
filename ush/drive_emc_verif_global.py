import os
import sys
import subprocess
import re
import configparser
from datetime import datetime, timedelta

########################################################################
# THERE IS NO NEED FOR USERS TO MODIFY THIS SCRIPT.
########################################################################

def error_and_exit(message):
    print(f"{message}. EXITING!")
    sys.exit(1)

def check_machine(config_machine):
    if not 'HOSTNAME' in list(os.environ.keys()):
        hostname = subprocess.check_output(
            'hostname', shell=True, encoding='UTF-8'
        ).replace('\n', '')
    else:
        hostname = os.environ['HOSTNAME']
        hera_match = re.match(re.compile(r"^hfe[0-9]{2}$"), hostname)
    ursa_match = re.match(re.compile(r"^ufe0[1-4]{1}$"), hostname)
    cactus_match = re.match(
        re.compile(r"^clogin[0-9]{2}$"), hostname
    )
    cactus_match2 = re.match(
        re.compile(r"^cdecflow[0-9]{2}$"), hostname
    )
    dogwood_match = re.match(
        re.compile(r"^dlogin[0-9]{2}$"), hostname
    )
    dogwood_match2 = re.match(
        re.compile(r"^ddecflow[0-9]{2}$"), hostname
    )
    gaeac6_match = re.match(re.compile(r"^gaea6[1-8]{1}"), hostname)
    if cactus_match or dogwood_match or cactus_match2 or dogwood_match2:
        machine = "wcoss2"
    elif ursa_match:
        machine = "ursa"
    elif gaeac6_match:
        machine = "gaeac6"
    else:
        error_and_exit(f"Cannot find match for {hostname}")
    if config_machine != machine:
        error_and_exist(
            f"Machine name passed in config was {config_machine} "
            +f"but found hostname {hostname} matching machine {machine}"
        )

def create_job_script(
    case, user_config, machine_name, model_name, date_start,
    date_end, jobfile, logfile
):
    for check_file in [jobfile, logfile]:
        if os.path.exists(check_file):
            try:
                print(f"Removing existing file {check_file}")
                os.remove(check_file)
            except OSError as e:
                error_and_exit(
                    f"Could not removed existing log file {check_file}: {e}"
                )
    # --- Define Variables ---
    # Set job run name
    jobname = jobfile.rpartition("/")[2].replace(".sh", "")
    # Set EMC_verif-global home location
    current_dir = os.getcwd()
    home_verif_global_path = os.path.abspath(
        os.path.join(current_dir, os.pardir)
    )
    # Set job run settings
    if "STEP1" in case:
        walltime = "04:00:00"
        memory = "25GB"
        nproc = "1"
    if machine_name == 'gaeac6':
        account = "gfs-cpu"
        partition = "batch"
        clusters = "c6"
        queue = "normal"
        queueserv = "service"
        fix_files = (
            "/gpfs/f6/drsa-precip3/world-shared/role.glopara/fix/verif/20220805"
        )
        global_archive = (
            "/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/archive"
        )
        prepbufr_archive = (
            "/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/prepbufr"
        )
        obs_archive = (
            "/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/obdata"
        )
        ccpa_24hr_archive = (
            "/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
        )
        sat_obs_archive = (
            "/gpfs/f6/drsa-precip3/world-shared/${USER}/obs_archive"
        )
    elif machine_name == 'ursa':
        account = "fv3-cpu"
        queue = "batch"
        queueserv = "u1-service"
        partition = "u1-compute"
        fix_files = (
            "/scratch3/NCEPDEV/global/role.glopara/fix/verif/20220805"
        )
        global_archive = (
            "/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/archive"
        )
        prepbufr_archive = (
            "/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/prepbufr"
        )
        obs_archive = (
            "/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/obdata"
        )
        ccpa_24hr_archive = (
            "/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
        )
        sat_obs_archive = (
            "/scratch4/NCEPDEV/naqfc/${USER}/noscrub/obs_archive"
        )
    elif machine_name == 'wcoss2':
        account = "VERF-DEV"
        queue = "dev"
        queueserv = "dev_transfer"
        partition = ""
        fix_files = (
            "/lfs/h2/emc/global/noscrub/emc.global/FIX/fix/verif/20220805"
        )
        global_archive = (
            "/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/model_data"
        )
        prepbufr_archive = (
            "/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/prepbufr"
        )
        obs_archive = (
            "/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data"
        )
        ccpa_24hr_archive = (
            "/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/ccpa_accum24hr"
        )
        sat_obs_archive = (
            "/lfs/h2/emc/vpppg/noscrub/ho-chun.huang/verif_global_obs_archive"
        )

    sh = open(jobfile, "w")   
    # --- Write the Machine-Specific Part of the Batch Script ---
    sh.write("#!/usr/bin/env bash\n")
    if machine_name == "gaeac6":
        sh.write(f"#SBATCH --account={account}\n")
        sh.write(f"#SBATCH --job-name={jobname}\n")
        sh.write(f"#SBATCH --output={logfile}\n")
        sh.write(f"#SBATCH --time={walltime}\n")
        sh.write(f"#SBATCH --ntasks=1\n")
        sh.write(f"#SBATCH --cpus-per-task={nproc}\n")
        sh.write(f"#SBATCH --clusters={clusters}\n")
        sh.write(f"#SBATCH --partition={partition}\n")
        sh.write(f"#SBATCH --qos={queue}\n")
    elif machine_name == "ursa":
        sh.write(f"#SBATCH --account={account}\n")
        sh.write(f"#SBATCH --job-name={jobname}\n")
        sh.write(f"#SBATCH --output={logfile}\n")
        sh.write(f"#SBATCH --time={walltime}\n")
        sh.write(f"#SBATCH --ntasks=1\n")
        sh.write(f"#SBATCH --cpus-per-task={nproc}\n")
        sh.write(f"#SBATCH --qos={queue}\n")
        sh.write(f"#SBATCH --get-user-env\n")
    elif machine_name == "wcoss2":
        sh.write(f"#PBS -o {logfile}\n")
        sh.write(f"#PBS -e {logfile}\n")
        sh.write(f"#PBS -l place=shared,select=1:ncpus={nproc}:mem={memory}\n")
        sh.write(f"#PBS -N {jobname}\n")
        sh.write(f"#PBS -q {queue}\n")
        sh.write(f"#PBS -A {account}\n")
        sh.write(f"#PBS -l walltime={walltime}\n")
        sh.write("#PBS -l debug=true\n")
    sh.write("\nset -eux\n")

    # --- Set Machine Name ---
    sh.write("\n")
    sh.write("# Set the machine name\n")
    sh.write(f"export machine={machine_name}\n")
    sh.write(f"export ACCOUNT={account}\n")
    sh.write(f"export QUEUE={queue}\n")
    sh.write(f"export QUEUESERV={queueserv}\n")
    sh.write(f"export PARTITION_BATCH={partition}\n")
    sh.write(f"export nproc={nproc}\n")
    sh.write(f"export MPMD=YES\n")

    # --- Set verif-global Path ---
    sh.write("\n")
    sh.write("# Set the root path to the verif-global package\n")
    sh.write(f'export HOMEverif_global="{home_verif_global_path}"\n')
    sh.write(f"export PARMverif_global=\"${{HOMEverif_global}}/parm\"\n")
    sh.write(f"export USHverif_global=\"${{HOMEverif_global}}/ush\"\n")
    
    # --- Set module load section ---
    sh.write("\n")
    sh.write("# Load the needed modules for METplus\n")
    if machine_name == "wcoss2":
        sh.write(f"source ${{HOMEverif_global}}/versions/run.ver\n")
    if machine_name == "ursa":
        sh.write("module purge\n")
    else:
        sh.write("module reset\n")
    sh.write(f"module use \"${{HOMEverif_global}}/modulefiles\"\n")
    sh.write(f"module load \"emc_verif_global_${{machine}}\"\n")
    sh.write(f"export HOMEMET=\"${{HOMEMET}}\"\n")
    sh.write(f"export HOMEMETplus=\"${{HOMEMETplus}}\"\n")
    sh.write(f"export USHMETplus=\"${{HOMEMETplus}}/ush\"\n")
    sh.write(f"export PYTHONPATH=\"${{USHMETplus}}:${{PYTHONPATH}}\"\n")

    # --- Set temporary working directory ---
    sh.write("\n")
    sh.write("# Create and navigate to a temporary working directory")
    sh.write("export jobid=$$\n")
    sh.write("export DATA=${DATAROOT}/emc_verif_global.${jobid}\n")
    sh.write('mkdir -p "${DATA}"\n')
    sh.write('cd "${DATA}" || exit 1\n')
    sh.write("export OUTPUTROOT=${DATA}\n")
    #sh.write("export pid=$$\n")
    #sh.write('export pgmout="OUTPUT.${pid}"\n')
    #sh.write("export pgmerr=errfile\n")
    #sh.write("export pgm=metplus\n")
    #sh.write("export RUN=gfs\n")
    #sh.write("export NET=gfs\n")
    #sh.write("export envir=prod\n")
    #sh.write("export RUN_ENVIR=emc\n")

    # --- Set fix files ---
    sh.write("\n")
    sh.write("# Link in fix files\n")
    sh.write("export FIXglobal=${DATA}\n")
    sh.write(f"ln -sf {fix_files} \"${{FIXglobal}}/verif\"\n")

    # --- Set data directories ---
    sh.write("\n")
    sh.write("# Set data directories\n")
    sh.write(f"export global_archive={global_archive}\n")
    sh.write(f"export prepbufr_arch_dir={prepbufr_archive}\n")
    sh.write(f"export obdata_dir={obs_archive}\n")
    sh.write(f"export ccpa_24hr_arch_dir={ccpa_24hr_archive}\n")
    sh.write(f"export sat1_obs_dir={sat_obs_archive}\n")
    sh.write(f"export prepbufr_prod_upper_air_dir=/lfs/h1/ops/prod/com/obsproc/${{obsproc_ver}}\n")
    sh.write(f"export prepbufr_prod_conus_sfc_dir=/lfs/h1/ops/prod/com/obsproc/${{obsproc_ver}}\n")
    sh.write(f"export ccpa_24hr_prod_dir=/lfs/h1/ops/prod/com/verf_precip/${{verf_precip_ver}}\n")
    sh.write(
        'export iabp_ftp="http://iabp.apl.washington.edu/'
        +'Data_Products/Daily_Full_Res_Data"\n'
    )
    sh.write(
        'export ghrsst_ncei_avhrr_anl_ftp="https://www.ncei.noaa.gov'
        +'/data/oceans/ghrsst/L4/GLOB/NCEI/AVHRR_OI"\n'
    )
    sh.write(
        'export ghrsst_ospo_geopolar_anl_ftp="https://www.ncei.noaa.gov/data/oceans'
        +'/ghrsst/L4/GLOB/OSPO/Geo_Polar_Blended"\n'
    )
    
    # --- Clean up ---
    sh.write("\n")
    sh.write("# Final clean up\n")
    sh.write('if [[ ${KEEPDATA:-"NO"} = "NO" ]] ; then rm -rf "${DATA}" ; fi')
    sh.close()

    print(f"Script     = {jobfile}")
    print(f"Log File   = {logfile}")
    
##########################################################
### Check and read the passed config
if len(sys.argv) != 2:
    error_and_exit(
        f"{sys.argv[0]} take one command line agrument "
        +f"(path to config file), given {len(sys.argv)-1}."
    )

config_path = os.path.abspath(sys.argv[1])
if not os.path.exists(config_path):
    error_and_exit(
        f"ERROR: {config_path} does not exist. EXITING"
    )
print(f"Parsing {config_path}\n")
config = configparser.ConfigParser(interpolation=None)
config.optionxform = str
config.read(config_path)
for section_name in config.sections():
    for name, value in config.items(section_name):
        if "$" in value:
            config[section_name][name] = os.path.expandvars(value)
        if '"' in value:
            config[section_name][name] = value.replace('"', '')

### Set up run directories
DATAROOT_dirs = [config["INPUT_OUTPUT"]["DATAROOT"]]
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "jobs"))
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "logs"))
for DATAROOT_dir in DATAROOT_dirs:
    if not os.path.exists(DATAROOT_dir):
        print(f"Creating {DATAROOT_dir}")
        os.makedirs(DATAROOT_dir, exist_ok=True)
print("")

### Convert string agruments to date objects
start_date_str = config["DATES"]["start_date"]
end_date_str = config["DATES"]["end_date"]
start_date, end_date = None, None
try:
    # Parse start_date
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            start_date = datetime.strptime(start_date_str, fmt).date()
            break
        except ValueError:
            pass
    # Parse end_date
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            end_date = datetime.strptime(end_date_str, fmt).date()
            break
        except ValueError:
            pass
    if start_date is None or end_date is None:
        raise ValueError("Invalid date format")
except ValueError:
    error_and_exit(
        "Invalid date format. Please use yyyymmdd or yyyy-mm-dd."
    )
if start_date > end_date:
    error_and_exit(
        "The start date cannot be after the end date."
    )

### Check machine
machine = config["MACHINE"]["name"]
check_machine(machine)
ALLOWED_MACHINES = ["gaeac6", "wcoss2", "ursa"]
if machine not in ALLOWED_MACHINES:
    error_and_exit(
        f"Invalid machine name '{machine}'. "
        +f"Please choose from: {', '.join(ALLOWED_MACHINES)}"
    )

### Run jobs
for case_switch, case_switch_value in config["RUN"].items():
    if "STEP1" in case_switch and case_switch_value == "YES":
        model_list = config["INPUT_OUTPUT"]["model_list"].split(" ")
        delta = timedelta(days=1) 
        ### Check number of jobs to submit
        njobs = 0
        for model_name in model_list:
            current_date = start_date
            while current_date <= end_date:
                njobs+=1
                current_date += delta
        if njobs >= 50:
            print(f"You are about to submit {njobs} jobs to the queue")
            print("Please mind the number of jobs you are submitting")
            proceed = input(f"Proceed to submit {njobs}? [Y/n]")
            if proceed != 'Y':
                error_and_exit(
                    f"Not proceeding, adjust your set up to submit less jobs"
                )
            print("")
        for model in model_list:
            current_date = start_date
            while current_date <= end_date:
                print(
                    f"--- Generating script for {model} {current_date:%Y-%m-%d} ---"
                )
                job_script = os.path.join(
                    os.path.join(config["INPUT_OUTPUT"]["DATAROOT"]), "jobs",
                    f"submit_{case_switch.replace('RUN_', '').lower()}_{model_name}_"
                    +f"{current_date:%Y%m%d}.sh"
                )
                log_script = job_script.replace("jobs", "logs").replace(".sh", ".log")
                create_job_script(
                    case_switch.replace("RUN", ""), config, machine, model,
                    current_date, current_date, job_script, log_script
                )
                current_date += delta
                print("-" * 30)
