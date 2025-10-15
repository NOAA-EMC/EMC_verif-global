import datetime
import os
import subprocess
import sys


def create_run_script(target_date, machine_name, application_name, max_forecast_hour_for_stats, common_script_to_append, experiment_name, user_model_output_location):
    """
    Generates a SLURM or PBS batch script for a specific date to transfer a file to stats.

    Args:
        target_date (datetime.date): The date for which to generate the script.
        machine_name (str): The name of the machine (e.g., 'gaeac6', 'wcoss2').
        application_name (str): The name of the application (e.g., 'grid2obs').
        max_forecast_hour_for_stats (int): The maximum forecast hour to consider for stats.
        common_script_to_append (str): The name of the common script file to append.
        experiment_name (str): The name of the experiment for the PSLOT variable.
        user_model_output_location (str): The base path for user model output.
    """
    # --- 1. Define Variables ---
    # Format the date into 'yyyymmdd' string
    date_str = target_date.strftime('%Y%m%d')

    # Calculate number of days from hours for date calculations
    number_of_model_days = max_forecast_hour_for_stats // 24

    # Calculate dependent GFS dates
    sdate_gfs = target_date - datetime.timedelta(days=number_of_model_days)
    edate_gfs = target_date
    sdate_gfs_str = sdate_gfs.strftime('%Y%m%d') + '00'
    edate_gfs_str = edate_gfs.strftime('%Y%m%d') + '18'
    
    # Define model input location for step1_stats
    step1_model_input_directory = f"{user_model_output_location}/${{PSLOT}}"
    
    # Define date-dependent variables
    jobname = f"{machine_name}_{application_name}_stats_{date_str}"
    log_dir = "." # Set log directory to the current directory
    logfile = f"{log_dir}/{jobname}_{date_str}.log"
    run_batch_file = f"submit_{machine_name}_{application_name}_{date_str}.sh" # The output script name

    # Check for and remove existing files ---
    if os.path.exists(run_batch_file):
        try:
            os.remove(run_batch_file)
            print(f"INFO: Removed existing script file '{run_batch_file}'.")
        except OSError as e:
            print(f"Error: Could not remove existing script file '{run_batch_file}': {e}")
            sys.exit(1)

    # Check for the log file only for wcoss2, as it's the only one that defines a specific log file
    if machine_name == 'wcoss2' and os.path.exists(logfile):
        try:
            os.remove(logfile)
            print(f"INFO: Removed existing log file '{logfile}'.")
        except OSError as e:
            print(f"Error: Could not remove existing log file '{logfile}': {e}")
            sys.exit(1)

    # Define static variables (can be changed as needed)
    task_cpu = "01:00:00"
    if application_name == 'grid2obs':
        # Convert HH:MM:SS string to timedelta, add 30 minutes, and convert back
        h, m, s = map(int, task_cpu.split(':'))
        new_time = datetime.timedelta(hours=h, minutes=m, seconds=s) + datetime.timedelta(minutes=30)

        # Format timedelta back to HH:MM:SS string
        total_seconds = int(new_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        task_cpu = f"{hours:02}:{minutes:02}:{seconds:02}"
        print(f"INFO: Increased CPU time for '{application_name}' to {task_cpu}")

    # Set the root path for verif-global by going up two directories
    current_dir = os.getcwd()
    home_verif_global_path = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # --- 2. Write the Machine-Specific Part of the Batch Script ---
    try:
        with open(run_batch_file, 'w') as sh:
            sh.write("#!/usr/bin/env bash\n")

            # --- GAEA (SLURM) Job Card ---
            if machine_name == 'gaeac6':
                account = "gfs-cpu"
                partition = "batch"
                clusters = "c6"
                qos = "normal"
                sh.write(f"#SBATCH --account={account}\n")
                sh.write(f"#SBATCH --job-name={jobname}\n")
                sh.write(f"#SBATCH --output={jobname}.out.%j\n")
                sh.write(f"#SBATCH --time={task_cpu}\n")
                sh.write(f"#SBATCH --ntasks=1\n")
                sh.write(f"#SBATCH --cpus-per-task=1\n")
                sh.write(f"#SBATCH --clusters={clusters}\n")
                sh.write(f"#SBATCH --partition={partition}\n")
                sh.write(f"#SBATCH --qos={qos}\n")

            # --- WCOSS2 (PBS) Job Card ---
            elif machine_name == 'wcoss2':
                account = "AQM-DEV" # Example account for WCOSS2
                queue = "dev" # Example queue for WCOSS2
                sh.write(f"#PBS -o {logfile}\n")
                sh.write(f"#PBS -e {logfile}\n")
                sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                sh.write(f"#PBS -N {jobname}\n")
                sh.write(f"#PBS -q {queue}\n")
                sh.write(f"#PBS -A {account}\n")
                sh.write(f"#PBS -l walltime={task_cpu}\n")
                sh.write("#PBS -l debug=true\n")
            
            sh.write("\nset -eux\n")

            # --- Set Machine Name ---
            sh.write("\n")
            sh.write("# Set the machine name\n")
            if machine_name == 'gaeac6':
                sh.write("export machine=gaeac6\n")
            elif machine_name == 'wcoss2':
                sh.write("export machine=wcoss2\n")

            # --- Experiment Date Configuration ---
            sh.write("\n")
            sh.write("# --- Experiment Date Configuration ---\n")
            sh.write("# Set the start and end date of the experiment's GFS cycles\n")
            sh.write(f"export SDATE_GFS={sdate_gfs_str}\n")
            sh.write(f"export EDATE_GFS={edate_gfs_str}\n")
            sh.write("# Set the frequency at which the GFS cycles were run\n")
            sh.write("export INTERVAL_GFS=6\n")
            sh.write("# Set the verification date and cycle of interest\n")
            sh.write(f"export PDY={date_str}\n")
            sh.write("# Minimum and maximum forecast hours to verify\n")
            sh.write("export FHMIN_GFS=0\n")
            sh.write(f"export FHMAX_GFS={max_forecast_hour_for_stats}\n")


            # --- Set Application Run Flags ---
            sh.write("\n")
            sh.write("# Set just one of these at a time to \"YES\":\n")
            sh.write(f"export RUN_GRID2GRID_STEP1={'YES' if application_name == 'grid2grid' else 'NO'}\n")
            sh.write(f"export RUN_GRID2OBS_STEP1={'YES' if application_name == 'grid2obs' else 'NO'}\n")
            sh.write(f"export RUN_PRECIP_STEP1={'YES' if application_name == 'precip' else 'NO'}\n")
            sh.write(f"export RUN_SATELLITE_STEP1={'YES' if application_name == 'satellite' else 'NO'}\n")
            
            # --- Set verif-global Path ---
            sh.write("\n")
            sh.write("# Set the root path to the verif-global package\n")
            sh.write(f"export HOMEverif_global=\"{home_verif_global_path}\"\n")
            
            # --- Set Experiment Name ---
            sh.write("\n")
            sh.write("# Change PSLOT to the name of your experiment\n")
            sh.write(f"export PSLOT={experiment_name}\n")

            # --- Set Archive Directory ---
            sh.write("\n")
            sh.write("# Set the location of your online archive\n")
            sh.write(f"export ARCDIR={step1_model_input_directory}\n")
            sh.write("# NOTE: the location of the statistic files will be one directory up from ARCDIR\n")
            sh.write("#       then appended by /metplus_data/by_${gather_by}/\n")
            sh.write("#       followed by the validation type (e.g. grid2grid, grid2obs, precip)\n")
            sh.write("#       validation type (e.g. pres, sfc, upper_air, conus_sfc, ccpa_accum24hr)\n")
            sh.write("#       then /${cyc}z/${model}/${model}_${PDY}.stat\n")


        print(f"Successfully created initial script: '{run_batch_file}'")

    except IOError as e:
        print(f"Error writing to initial script file {run_batch_file}: {e}")
        return

    # --- 3. Append the Common Lines from the separate file ---
    try:
        with open(common_script_to_append, 'r') as common_file:
            common_content = common_file.read()

        with open(run_batch_file, 'a') as sh:
            sh.write("\n# --- Appending Common Post-Processing Commands ---\n")
            sh.write(common_content)

        print(f"Successfully appended '{common_script_to_append}' to '{run_batch_file}'.")

    except FileNotFoundError:
        print(f"Warning: The common script '{common_script_to_append}' was not found.")
    except IOError as e:
        print(f"Error appending common script file: {e}")
        return

    # --- 4. Print info and submit the job ---
    print("Script    = "+run_batch_file)
    
    # Speculate on the final stats directory based on the script's comments
    stats_dir_pattern = f"{user_model_output_location}/metplus_data/by_${{gather_by}}/{application_name}/<validation_type>/${{cyc}}z/${{model}}/"

    if machine_name == 'gaeac6':
        print(f"Log File Pattern  = {jobname}.out.%j")
        print(f"Stats Dir Pattern = {stats_dir_pattern}")
        submission_command = f"sbatch {run_batch_file}"
    elif machine_name == 'wcoss2':
        print("Log File          = "+logfile)
        print(f"Stats Dir Pattern = {stats_dir_pattern}")
        submission_command = f"qsub {run_batch_file}"
    else:
        submission_command = None

    if submission_command:
        print(f"Submitting job with: {submission_command}")
        subprocess.call([submission_command], shell=True)
    else:
        print(f"Error: Unknown machine '{machine_name}'. Cannot determine submission command.")

# --- Main execution block to demonstrate usage ---
if __name__ == "__main__":
    # --- Define settings ---
    max_forecast_hour_for_stats = 120 # 5 days
    experiment_name = "gfs_dev"
    # Define user-defined model output location
    user_model_output_location = "/gpfs/f6/ira-sti/world-shared/${USER}/KEEP_archive"
    common_script_to_append = "standalone_step1_stats.append"
    
    # --- Define allowed inputs ---
    ALLOWED_MACHINES = ['gaeac6']
    ALLOWED_APPLICATIONS = ['grid2obs', 'grid2grid', 'precip', 'satellite']

    # --- Check for number of USER-PROVIDED arguments ---
    num_args = len(sys.argv) - 1

    if num_args < 3:
        print("Usage: python generate_batch_script.py [machine] [application] [date] [optional_end_date]")
        print("        Date format can be yyyymmdd or yyyy-mm-dd")
        print("Error: You must provide at least three arguments.")
        print(f"Available machines: {', '.join(ALLOWED_MACHINES)}")
        print(f"Available applications: {', '.join(ALLOWED_APPLICATIONS)}")
        sys.exit(1)

    # --- Assign and Validate Arguments ---
    machine_name = sys.argv[1].lower()
    application_name = sys.argv[2].lower()
    start_date_str = sys.argv[3]
    end_date_str = start_date_str if num_args == 3 else sys.argv[4]

    if machine_name not in ALLOWED_MACHINES:
        print(f"Error: Invalid machine name '{machine_name}'.")
        print(f"Please choose from: {', '.join(ALLOWED_MACHINES)}")
        sys.exit(1)

    if application_name not in ALLOWED_APPLICATIONS:
        print(f"Error: Invalid application name '{application_name}'.")
        print(f"Please choose from: {', '.join(ALLOWED_APPLICATIONS)}")
        sys.exit(1)

    # --- Convert string arguments to date objects ---
    start_date, end_date = None, None
    try:
        # Parse start_date
        for fmt in ('%Y-%m-%d', '%Y%m%d'):
            try:
                start_date = datetime.datetime.strptime(start_date_str, fmt).date()
                break
            except ValueError:
                pass
        
        # Parse end_date
        for fmt in ('%Y-%m-%d', '%Y%m%d'):
            try:
                end_date = datetime.datetime.strptime(end_date_str, fmt).date()
                break
            except ValueError:
                pass
        
        if start_date is None or end_date is None:
            raise ValueError("Invalid date format")

    except ValueError:
        print("Error: Invalid date format. Please use yyyymmdd or yyyy-mm-dd.")
        sys.exit(1)

    if start_date > end_date:
        print("Error: The start date cannot be after the end date.")
        sys.exit(1)

    print(f"Machine: {machine_name}, Application: {application_name}")
    print(f"Generating scripts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # --- Script Generation Loop ---
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        print(f"--- Generating script for {current_date.strftime('%Y-%m-%d')} ---")
        create_run_script(current_date, machine_name, application_name, max_forecast_hour_for_stats, common_script_to_append, experiment_name, user_model_output_location)
        current_date += delta
        print("-" * 30)

    print("\nScript generation complete.")
