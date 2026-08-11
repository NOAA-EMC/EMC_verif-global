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
    print(f"ERROR: {message}. EXITING!")
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
        machine = "WCOSS2"
    elif ursa_match:
        machine = "URSA"
    elif gaeac6_match:
        machine = "GAEAC6"
    else:
        error_and_exit(f"Cannot find match for {hostname}")
    if config_machine != machine:
        error_and_exit(
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
    reset_value_dict = {}
    if "STEP1" in case:
        model_idx = (
            user_config["INPUT_OUTPUT"]\
            ["model_list"].split(" ").index(model_name)
        )
        reset_value_dict["model_list"] = model_name
        reset_keys = [
            "model_dir_list", "model_stat_dir_list",
            "model_file_format_list", "model_hpss_dir_list"
        ]
        for key in reset_keys:
            reset_value_dict[key] = (
                user_config["INPUT_OUTPUT"]\
                [key].split(" ")[model_idx]
            )
        if "GRID2GRID" in case:
            for ctype in ["anom", "pres", "sfc"]:
                reset_value_dict[f"g2g1_{ctype}_truth_file_format_list"] = (
                    user_config[case][f"g2g1_{ctype}_truth_file_format_list"]\
                    .split(" ")[model_idx]
                )
        elif "PRECIP" in case:
            for ctype in ["ccpa_accum24hr"]:
                reset_value_dict[f"precip1_{ctype}_model_file_format_list"] = (
                    user_config[case][f"precip1_{ctype}_model_file_format_list"]\
                    .split(" ")[model_idx]
                )
    # Set EMC_verif-global home location
    current_dir = os.getcwd()
    home_verif_global_path = os.path.abspath(
        os.path.join(current_dir, os.pardir)
    )
    # Set job specifics
    jobname = jobfile.rpartition("/")[2].replace(".sh", "")
    job_ex_script = os.path.join(
        home_verif_global_path, "scripts",
        f"ex{case.lower()}.sh"
    )
    # Set machine specifics
    account = user_config["MACHINE"]["queue_account"]
    if machine_name == 'GAEAC6':
        max_ncpus_per_node = "192"
        partition = "batch"
        clusters = "c6"
        queue = "normal"
        queueserv = "service"
        clusters_dtn = "es"
        partition_dtn = "dtn_f5_f6"
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
            "/gpfs/f6/drsa-precip3/world-shared/Ho-Chun.Huang/obs_archive"
        )
    elif machine_name == 'URSA':
        max_ncpus_per_node = "192"
        queue = "batch"
        queueserv = "u1-service"
        partition = "u1-compute"
        clusters_dtn = ""
        partition_dtn = ""
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
            "/scratch4/NCEPDEV/naqfc/Ho-Chun.Huang/noscrub/obs_archive"
        )
    elif machine_name == 'WCOSS2':
        max_ncpus_per_node = "128"
        queue = "dev"
        queueserv = "dev_transfer"
        partition = ""
        clusters_dtn = ""
        partition_dtn = ""
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

    nnodes = user_config["MACHINE"]["nodes"]
    ncpus_per_node = user_config["MACHINE"]["cpus_per_node"]
    memory = user_config["MACHINE"]["memory"]
    walltime = user_config["MACHINE"]["walltime"]
    if int(ncpus_per_node) > int(max_ncpus_per_node):
        error_and_exit(
            f"Requested cpus ({ncpus_per_node}) greater than "
            +f"{machine_name} max ({max_ncpus_per_node})"
        )
    sh = open(jobfile, "w")
    submission_command = None
    # --- Write the machine-specific part ---
    sh.write("#!/usr/bin/env bash\n")
    if machine_name == "GAEAC6":
        sh.write(f"#SBATCH --account={account}\n")
        sh.write(f"#SBATCH --job-name={jobname}\n")
        sh.write(f"#SBATCH --output={logfile}\n")
        sh.write(f"#SBATCH --time={walltime}\n")
        sh.write(f"#SBATCH --ntasks={nnodes}\n")
        sh.write(f"#SBATCH --cpus-per-task={ncpus_per_node}\n")
        sh.write(f"#SBATCH --clusters={clusters}\n")
        sh.write(f"#SBATCH --partition={partition}\n")
        sh.write(f"#SBATCH --qos={queue}\n")
        submission_command = f"sbatch {jobfile}"
    elif machine_name == "URSA":
        sh.write(f"#SBATCH --account={account}\n")
        sh.write(f"#SBATCH --job-name={jobname}\n")
        sh.write(f"#SBATCH --output={logfile}\n")
        sh.write(f"#SBATCH --time={walltime}\n")
        sh.write(f"#SBATCH --ntasks={nnodes}\n")
        sh.write(f"#SBATCH --cpus-per-task={ncpus_per_node}\n")
        sh.write(f"#SBATCH --qos={queue}\n")
        sh.write(f"#SBATCH --get-user-env\n")
        submission_command = f"sbatch {jobfile}"
    elif machine_name == "WCOSS2":
        sh.write(f"#PBS -o {logfile}\n")
        sh.write(f"#PBS -e {logfile}\n")
        sh.write(f"#PBS -l place=vscatter:exclhost,select={nnodes}:ncpus={ncpus_per_node}:ompthreads=1:mem={memory}\n")
        sh.write(f"#PBS -N {jobname}\n")
        sh.write(f"#PBS -q {queue}\n")
        sh.write(f"#PBS -A {account}\n")
        sh.write(f"#PBS -l walltime={walltime}\n")
        sh.write("#PBS -l debug=true\n")
        submission_command = f"qsub {jobfile}"
    sh.write("\nset -eux\n")

    # --- Set machine name ---
    sh.write("\n")
    sh.write("# Set the machine name\n")
    sh.write(f"export machine={machine_name}\n")
    sh.write(f"export ACCOUNT={account}\n")
    sh.write(f"export QUEUE={queue}\n")
    sh.write(f"export QUEUESERV={queueserv}\n")
    sh.write(f"export PARTITION_BATCH={partition}\n")
    sh.write(f"export PARTITION_DTN={partition_dtn}\n")
    sh.write(f"export CLUSTERS_DTN={clusters_dtn}\n")
    sh.write(f"export ncpus_per_node={ncpus_per_node}\n")
    sh.write(f"export MPMD=YES\n")

    # --- Set verif-global path ---
    sh.write("\n")
    sh.write("# Set the root path to the verif-global package\n")
    sh.write(f'export HOMEverif_global="{home_verif_global_path}"\n')
    sh.write(f"export PARMverif_global=\"${{HOMEverif_global}}/parm\"\n")
    sh.write(f"export USHverif_global=\"${{HOMEverif_global}}/ush\"\n")

    # --- Set module load section ---
    sh.write("\n")
    sh.write("# Load the needed modules for METplus\n")
    if machine_name == "WCOSS2":
        sh.write(f"source ${{HOMEverif_global}}/versions/run.ver\n")
    if machine_name == "URSA":
        sh.write("module purge\n")
    else:
        sh.write("module reset\n")
    sh.write(f"module use \"${{HOMEverif_global}}/modulefiles\"\n")
    sh.write(f"module load \"emc_verif_global_{machine.lower()}\"\n")
    sh.write(f"export HOMEMET=\"${{MET_ROOT}}\"\n")
    sh.write(f"export HOMEMET_bin_exec=\"bin\"\n")
    sh.write(f"export HOMEMETplus=\"${{METPLUS_ROOT}}\"\n")
    sh.write(f"export USHMETplus=\"${{HOMEMETplus}}/ush\"\n")
    sh.write(f"export MET_version=\"12.0.1\"\n")
    sh.write(f"export METplus_version=\"6.0.0\"\n")
    sh.write(f"export PYTHONPATH=\"${{USHMETplus}}:${{PYTHONPATH}}\"\n")

    # --- Set temporary working directory ---
    sh.write("\n")
    sh.write("# Create and navigate to a temporary working directory\n")
    sh.write("export jobid=$$\n")
    sh.write(f'export DATAROOT={user_config["INPUT_OUTPUT"]["DATAROOT"]}\n')
    sh.write("export DATA=${DATAROOT}/emc_verif_global.${jobid}\n")
    sh.write('mkdir -p "${DATA}"\n')
    sh.write('cd "${DATA}" || exit 1\n')
    sh.write("export OUTPUTROOT=${DATA}\n")
    #sh.write("export pid=$$\n")
    #sh.write('export pgmout="OUTPUT.${pid}"\n')
    #sh.write("export pgmerr=errfile\n")
    #sh.write("export pgm=metplus\n")
    sh.write(f"export RUN={case.lower()}\n")
    sh.write("export NET=verif_global\n")
    #sh.write("export envir=prod\n")
    #sh.write("export RUN_ENVIR=emc\n")


    # --- Set executable tpaths ---
    sh.write("\n")
    sh.write("# Set executable paths\n")
    sh.write("export CUT=$(which cut)\n")
    sh.write("export TR=$(which tr)\n")
    sh.write("export CONVERT=$(which convert)\n")
    sh.write("export NCDUMP=$(which ncdump)\n")
    sh.write("export HTAR=$(which htar)\n")

    # --- Set fix files ---
    sh.write("\n")
    sh.write("# Link in fix files\n")
    sh.write("export FIXglobal=${DATA}\n")
    sh.write(f"ln -sf {fix_files} \"${{FIXglobal}}/verif\"\n")
    sh.write(f"export FIXverif_global=\"${{FIXglobal}}/verif\"\n")

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

    # --- Set MET/METplus versions ---
    if "STEP1" in case or "MAPS" in case:
        sh.write("\n")
        sh.write("# Set MET and METplus versions\n")
        sh.write("export MET_version=12.0.1\n")
        sh.write("export METplus_version=6.0.0\n")

    # --- Set python files ---
    sh.write("\n")
    sh.write("# Set PYTHONPATH\n")
    sh.write("export PYTHONPATH=${PYTHONPATH}:${USHverif_global}\n")

    # --- Set resources ---
    if machine == 'WCOSS2':
        sh.write("\n")
        sh.write("#Set WCOSS2 resources\n")
        sh.write("export nselect=$(cat $PBS_NODEFILE | wc -l)\n")
        sh.write("export nproc=$(($nselect * $ncpus_per_node))\n")

    # --- Write configuration settings ---
    sh.write("\n")
    sh.write("# Configuration settings\n")
    sections = ["INPUT_OUTPUT", "DATES"]
    skip_keys = ["DATAROOT"]
    if "STEP1" not in case:
        sections.append("WEB")
    sections.append(case.upper())
    for section in sections:
        for key, value in user_config.items(section):
            if key in list(reset_value_dict.keys()):
                sh.write(
                    f'export {key}="{reset_value_dict[key]}"\n'
                )
            elif key in skip_keys:
                continue
            else:
                sh.write(f'export {key}="{value}"\n')

    # --- Write Execution script ---
    sh.write("\n")
    sh.write("# Execute script\n")
    sh.write(f"{job_ex_script}\n")

    # --- Clean up ---
    sh.write("\n")
    sh.write("# Final clean up\n")
    sh.write('if [[ ${KEEPDATA:-"NO"} = "NO" ]] ; then rm -rf "${DATA}" ; fi')

    sh.close()

    # --- Submit job ---
    if submission_command:
       print(f"Submitting job with: {submission_command}")
       subprocess.call([submission_command], shell=True)
    else:
       error_and_exit(
           f"Unknown machine '{machine_name}'."
           "Cannot determine submission command."
       )
    print(f"Script     = {jobfile}")
    print(f"Log File   = {logfile}")
    if "STEP1" in case:
        stats_dir_pattern = os.path.join(
            reset_value_dict["model_stat_dir_list"],
            "metplus_data", f'by_{user_config["DATES"]["make_met_data_by"]}',
            case.replace("_STEP1", "").lower(),
            "<<type>>", "<<hour>>Z", model_name
        )
        print(f"Stats Dir Pattern = {stats_dir_pattern}")


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
        f"{config_path} does not exist. EXITING"
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
machine = config["MACHINE"]["name"].upper()
check_machine(machine)
ALLOWED_MACHINES = ["GAEAC6", "WCOSS2", "URSA"]
if machine not in ALLOWED_MACHINES:
    error_and_exit(
        f"Invalid machine name '{machine}'. "
        +f"Please choose from: {', '.join(ALLOWED_MACHINES)}"
    )

### Run jobs
model_list = config["INPUT_OUTPUT"]["model_list"].split(" ")
for case_switch, case_switch_value in config["RUN"].items():
    if case_switch_value == "YES":
        if "STEP1" in case_switch:
            ### Check number of jobs to submit
            njobs = 0
            for model in model_list:
                njobs+=1
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
                print(
                    f"--- Generating script for {case_switch.replace('RUN_', '')} "
                    +f"{model} {start_date:%Y%m%d} to {end_date:%Y%m%d}---"
                )
                job_script = os.path.join(
                    os.path.join(config["INPUT_OUTPUT"]["DATAROOT"]), "jobs",
                    f"submit_{case_switch.replace('RUN_', '').lower()}_{model}_"
                    +f"{start_date:%Y%m%d}_to_{end_date:%Y%m%d}.sh"
                )
                log_script = job_script.replace("jobs", "logs").replace(".sh", ".log")
                create_job_script(
                    case_switch.replace("RUN_", ""), config, machine, model,
                    start_date, end_date, job_script, log_script
                )
                print("-" * 30)
        else:
            print(
                f"--- Generating script for {case_switch.replace('RUN_', '')} "
                +f"{start_date:%Y%m%d} to {end_date:%Y%m%d}---"
            )
            job_script = os.path.join(
                os.path.join(config["INPUT_OUTPUT"]["DATAROOT"]), "jobs",
                f"submit_{case_switch.replace('RUN_', '').lower()}_"
                +f"{start_date:%Y%m%d}_to_{end_date:%Y%m%d}.sh"
            )
            log_script = job_script.replace("jobs", "logs").replace(".sh", ".log")
            create_job_script(
                case_switch.replace("RUN_", ""), config, machine, model_list,
                start_date, end_date, job_script, log_script
            )
