import os
import numpy as np
import pandas as pd
import logging
import verif_global_util as vfg_util

def setup_logger():
    """! Sets up a basic logger.

            Returns:
                logger - logging object configured to output INFO level messages to the console.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        # Use a more visible format
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def scorecard_read_stat_file(logger, file_path, column_list):
    """! Reads a output file from "filter_stats" into a Pandas DataFrame.

            Args:
                logger      - logging object.
                file_path   - string of the full path to the stats file.
                column_list - list of strings containing the expected column names.

            Returns:
                df - Pandas DataFrame containing the data from the stat file,
                     with 'FCST_VALID_BEG' set as the index, or an empty DataFrame
                     if the file is missing or reading fails.
    """
    if not os.path.exists(file_path):
        logger.info(f"Input file not found: {file_path}")
        return pd.DataFrame(columns=column_list)
        
    try:
        # NOTE: Assumes data structure aligned with column_list provided by get_met_line_type_cols
        df = pd.read_csv(
            file_path, sep=" ", skiprows=1,
            skipinitialspace=True, names=column_list,
            na_values=['NA'], header=None
        )
        
        # Apply dtypes based on column list (MET standard)
        df_dtype_dict = {}
        float_idx = column_list.index('TOTAL')
        for col in column_list:
            col_idx = column_list.index(col)
            df_dtype_dict[col] = str if col_idx < float_idx else np.float64
        
        df = df.astype(df_dtype_dict)
        
        # Set index to the date (FCST_VALID_BEG) for alignment stability
        if 'FCST_VALID_BEG' in df.columns:
            df = df.set_index('FCST_VALID_BEG')
            
        return df
    except Exception as e:
        logger.error(f"Failed to read or process file {file_path}: {e}")
        return pd.DataFrame(columns=column_list)

def scorecard_write_avg_ci(logger, filename, data_line, file_write_tracker):
    """! Writes a line of data, ensuring the file is cleared on first write.

            Args:
                logger            - logging object.
                filename          - string of the full path to the output file.
                data_line         - string of the data to write.
                file_write_tracker- dictionary used to track if a file has been written
                                    to before in this run (keys are filenames).
    """
    
    write_mode = 'a'
    if filename not in file_write_tracker:
        write_mode = 'w'
        # Ensure directory exists before first write
        vfg_util.make_dir(os.path.dirname(filename))
        file_write_tracker[filename] = True
        
    try:
        with open(filename, write_mode) as file2write:
            file2write.write(data_line + '\n')
    except Exception as e:
        logger.error(f"Failed to write to file {filename}: {e}")


def calculate_scorecard_avg_ci(
    logger, line_type, metric, fcst_lead, number_of_days, 
    modelA_df, modelB_df, modelA_name, modelB_name, 
    ci_method, average_method, modelB_base_filename, output_base_dir,
    file_write_tracker
):
    """! Calculates averages and CI of a metric and writes results for one lead time and average.
         Write '--' if input DataFrames are empty (no common dates/data).

            Args:
                logger              - logging object.
                line_type           - string of the MET line type (e.g., 'CNT', 'FHO').
                metric              - string of the metric to calculate (e.g., 'rmse', 'bias', 'acc').
                fcst_lead           - string of the forecast lead time (e.g., '006').
                number_of_days      - integer count of the number of common dates in the data.
                modelA_df           - Pandas DataFrame for the Model A aligned to common dates.
                modelB_df           - Pandas DataFrame for the Model B aligned to common dates.
                modelA_name         - string name of Model A (e.g., 'gfsv16').
                modelB_name         - string name of Model B (e.g., 'gfsv17').
                ci_method           - string of the confidence interval method (e.g., 'EMC').
                average_method      - string of the averaging method (e.g., 'MEAN').
                modelB_base_filename- string representing the base filename info for model B
                                      (used to construct output paths).
                output_base_dir     - string of the path to the directory for output files.
                file_write_tracker  - dictionary for tracking initial file write.
    """
    
    # Initialize values to "--" for the case of missing data
    modelA_metric_avg = '--'
    modelB_metric_avg = '--'
    modelB_ci = '--'
    
    # Check if the aligned DataFrames contain any data (i.e., common_dates was not empty)
    if modelA_df.empty or modelB_df.empty:
        # If no common data, log and proceed to output writing with initialized '--' values
        logger.info(
            f"  Skipping calculation for {output_base_dir} {metric} (F{fcst_lead}): Aligned data is empty. Writing '--'."
        )
    else:
        # --- Calculate Daily Metric Series ---
        try:
            modelA_metric_daily, modelA_metric_array, stat_plot_name = vfg_util.calculate_scorecard_stat(logger, modelA_df, metric)
            modelB_metric_daily, modelB_metric_array, _ = vfg_util.calculate_scorecard_stat(logger, modelB_df, metric)
            
            # Check if the resulting metric arrays are valid for aggregation
            # This check is crucial for handling cases where calculate_stat might return empty/invalid data 
            # even if the raw DataFrame wasn't structurally empty, but was masked out.
            if not modelA_metric_array.any() or not modelB_metric_array.any():
                logger.info(f"  Skipping calculation for {metric}: Daily data array is empty or fully masked. Writing '--'.")
            else:
                modelA_daily_values = modelA_metric_array.flatten()
                modelB_daily_values = modelB_metric_array.flatten()
                
                # --- Calculate Mean metric ---

                modelA_daily_values_reshaped = modelA_daily_values.reshape(1, -1)
                modelB_daily_values_reshaped = modelB_daily_values.reshape(1, -1)
                
                # Note: calculate_average returns a numpy array, take [0] to get the scalar value
                modelA_metric_avg = vfg_util.calculate_scorecard_average(
                    logger, average_method, metric, modelA_df, modelA_daily_values_reshaped
                )[0]
                modelB_metric_avg = vfg_util.calculate_scorecard_average(
                    logger, average_method, metric, modelB_df, modelB_daily_values_reshaped
                )[0]
        
                # --- Calculate CI for Model B vs Model A ---
                
                # Check dimensionality robustly: 1D (Series) implies one column, 2D (DataFrame) check shape[1]
                modelA_ndim = modelA_metric_daily.ndim
                num_cols = modelA_metric_daily.shape[1] if modelA_ndim == 2 else 1 # Assume 1 if Series (ndim=1)
        
                if num_cols == 1:
                    if modelA_ndim == 1:
                        modelA_daily_series = modelA_metric_daily
                        modelB_daily_series = modelB_metric_daily
                    else: # modelA_ndim == 2 (DataFrame with 1 column)
                        modelA_daily_series = modelA_metric_daily.iloc[:, 0]
                        modelB_daily_series = modelB_metric_daily.iloc[:, 0]
                        
                    # NOTE: total_days should be the number of rows in the aligned dataframe, which is modelA_df.shape[0]
                    randx_data = np.random.rand(10000, modelA_df.shape[0]) 
                    
                    ci_result = vfg_util.calculate_ci(
                        logger, 
                        ci_method, 
                        modelB_daily_series,
                        modelA_daily_series,
                        modelA_df.shape[0], 
                        metric, 
                        average_method, 
                        randx_data
                    )
                    
                    # Update modelB_ci only if calculation was successful (not the original string '--')
                    if ci_result != '--':
                        modelB_ci = ci_result
                else:
                    logger.info(f"  Skipping CI calculation for metric '{metric}' as it returns multiple columns ({num_cols}). Writing '--'.")
        
        except Exception as e:
            logger.error(f"Failed to calculate stat for {metric} (F{fcst_lead}): {e}. Writing '--'.")


    # --- Output Path Generation and Writing ---
    
    # Write Model A Average

    # forecast hour output format
    fcst_lead_string=fcst_lead.lstrip('0')+"0000"

    modelA_avg_output_file = vfg_util.get_lead_avg_file(
        metric, modelB_base_filename.replace(modelB_name, modelA_name), fcst_lead, output_base_dir 
    )
    scorecard_write_avg_ci(
        logger, modelA_avg_output_file, f"{fcst_lead_string} {modelA_metric_avg}", file_write_tracker
    )
    logger.info(f"   Wrote {modelA_name} Avg to: {os.path.basename(modelA_avg_output_file)}")
    
    # Write Model B Average
    modelB_avg_output_file = vfg_util.get_lead_avg_file(
        metric, modelB_base_filename, fcst_lead, output_base_dir 
    )
    scorecard_write_avg_ci(
        logger, modelB_avg_output_file, f"{fcst_lead_string} {modelB_metric_avg}", file_write_tracker
    )
    logger.info(f"   Wrote {modelB_name} Avg to: {os.path.basename(modelB_avg_output_file)}")
    
    # Write CI
    ci_output_file = vfg_util.get_ci_file(
        metric, modelB_base_filename, fcst_lead, output_base_dir, ci_method
    )
    scorecard_write_avg_ci(
        logger, ci_output_file, f"{fcst_lead_string} {modelB_ci}", file_write_tracker
    )
    logger.info(f"   Wrote CI to: {os.path.basename(ci_output_file)}")


def main():
    """! Main function to drive the scorecard average and confidence interval calculation.
         It reads configuration, iterates over forecast leads, reads and aligns two sets
         of verification statistics for two models, and calculates/writes averages and CI.
    
            Returns:
                0 for successful completion, -1 if the input directory is missing.
    """
    logger = setup_logger()

    # --- Get CONFIGURATION SETTINGS ---
    DATA            = os.environ["DATA"]          
    met_root        = os.environ["HOMEMET"]          
    met_version     = os.environ["MET_version"]
    RUN             = os.environ["RUN"]          
    case_type       = os.environ["CASE_TYPE"]          
    JOB_GROUP       = os.environ["JOB_GROUP"]          
    fhrs            = os.environ["fhr_list"]          
    fcst_hr_list    = [str(int(fhr.strip())).zfill(3) for fhr in fhrs.split(',')]
    run_case        = os.environ["RUN_CASE"]          
    start_date      = os.environ["start_date"]          
    end_date        = os.environ["end_date"]          
    plot_by         = os.environ["plot_by"]          
    grid            = os.environ["grid"]          
    job_name        = os.environ["job_name"]          
    valid_hr        = os.environ["valid_hr_list"]          
    fcst_var_name   = os.environ["fcst_var_name"]          
    obs_var_name    = os.environ["obs_var_name"]          
    fcst_var_level  = os.environ["fcst_var_level"]          
    obs_var_level   = os.environ["obs_var_level"]          
    model_list      = os.environ["model_list"]          
    models = [m.strip() for m in model_list.split(",")]
    if len(models) >= 2:
        model1_name     = models[0]
        model2_name     = models[1]
    else:
        logger.info(f"The number of input model list is less than 2")
    obs_list        = os.environ["obs_list"]          
    models = [m.strip() for m in obs_list.split(",")]
    if len(models) >= 2:
        model1_truth    = models[0]
        model2_truth    = models[1]
    else:
        logger.info(f"The number of input truth list is less than 2")
    line_type       = os.environ["line_type"]          
    vx_mask         = os.environ["vx_mask"]          
    fcst_var_thresh = os.environ["fcst_var_thresh"]          
    obs_var_thresh  = os.environ["obs_var_thresh"]          
    interp_method   = os.environ["interp_method"]          
    interp_points   = os.environ["interp_points"]          
    job_DATA_dir    = os.environ["job_DATA_dir"]          
    metric          = os.environ["metric"]          
    ci_method       = os.environ["CI_METHOD"]      ##  "EMC"
    average_method  = os.environ["AVERAGE_METHOD"] ##  "MEAN"
    
    ## input_dir = "/lfs/h2/emc/vpppg/noscrub/ho-chun.huang/verif_global/grid2grid_step2/plot_output/plot_by_VALID/filter_stats"
    input_dir = os.path.join( os.path.dirname(job_DATA_dir), "filter_stats", case_type)

    
    ## if not os.path.exists(job_DATA_dir):
    ##     os.makedirs(job_DATA_dir)
    ##     logger.info(f"Created output base directory: {job_DATA_dir}")
    if not os.path.exists(input_dir):
        logger.info(f"Input stats directory: {input_dir} does not exist")
        return -1
    
    met_version_line_type_col_list = vfg_util.get_met_line_type_cols(
        logger, met_root, met_version, line_type
    )

    subdir_path = f"{line_type}_{job_name}_{vx_mask}/{run_case}/{case_type}"
    output_stat_path = os.path.join( job_DATA_dir, subdir_path )
    if not os.path.exists(output_stat_path):
        vfg_util.make_dir(output_stat_path)
                        
    interp_method = interp_method.replace("-","_")
    plevel=fcst_var_level.replace("-","_")

    stats_info1=f"fcst{model1_name}_{fcst_var_name}{plevel}{fcst_var_thresh}_obs{model1_truth}"
    stats_info2=f"fcst{model2_name}_{fcst_var_name}{plevel}{fcst_var_thresh}_obs{model2_truth}"
    common_info = (
        f"_{obs_var_name}{plevel}{obs_var_thresh}"
        f"_linetype{line_type}_grid{grid}_vxmask{vx_mask}"
        f"_interp{interp_method}{interp_points}"
        f"_valid{start_date}{valid_hr}0000to{end_date}{valid_hr}0000"
    )
    input_filename1_prefix=stats_info1.lower()+common_info.lower()
    input_filename2_prefix=stats_info2.lower()+common_info.lower()

    file_write_tracker = {}
                    
    for fhr in fcst_hr_list:
        input_filename_suffix=f"fhr{fhr}.stat"

        input_filename1 = f"{input_filename1_prefix}_{input_filename_suffix}"
        input_filename2 = f"{input_filename2_prefix}_{input_filename_suffix}"
                        
        # Define the full input paths
        input_stats_path = input_dir # Use the defined input_dir
        model1_input_file = os.path.join( input_stats_path, input_filename1 )
        model2_input_file = os.path.join( input_stats_path, input_filename2 )
                            
        # --- START: FILE EXISTENCE CHECK ---
                            
        model1_exists = os.path.exists(model1_input_file)
        model2_exists = os.path.exists(model2_input_file)

        if not model1_exists or not model2_exists:
            # Log a debug info for missing file(s) and skip to the next lead time
            if not model1_exists:
                logger.info(
                    f"Missing file: {model1_name} for lead {fhr}hrs, level {plevel} {os.path.basename(model1_input_file)}"
                )
            if not model2_exists:
                logger.info(
                    f"Missing file: {model2_name} for lead {fhr}hrs, level {plevel} {os.path.basename(model2_input_file)}"
                )
            continue # Skip to the next 'fhr' iteration
        
        else:
            # Read the dataframes once per lead time (scorecard_read_stat_file should set index to FCST_VALID_BEG)

            modelA_stat_file_df = scorecard_read_stat_file(logger, model1_input_file, met_version_line_type_col_list)
            modelB_stat_file_df = scorecard_read_stat_file(logger, model2_input_file, met_version_line_type_col_list)
                    
            # --- DATA ALIGNMENT ---
            # 1. Find the dates common to both data sets
            common_dates = modelA_stat_file_df.index.intersection(modelB_stat_file_df.index)
                    
            # 2. Filter both dataframes to use only common dates
            modelA_df_aligned = modelA_stat_file_df.loc[common_dates].copy()
            modelB_df_aligned = modelB_stat_file_df.loc[common_dates].copy()
                    
            aligned_df_length = len(common_dates)
            ## logger.info(f"Using {aligned_df_length} common valid dates for calculation.")
            # --- END DATA ALIGNMENT ---
                            
            # Pass the ALIGNED DastaFrames to the processing function

            calculate_scorecard_avg_ci(
                logger, line_type, metric, fhr, aligned_df_length,
                modelA_df_aligned, modelB_df_aligned, model1_name, model2_name, 
                ci_method, average_method, input_filename2, output_stat_path,
                file_write_tracker
            )
    logger.info("\n--- Processing Complete ---")

if __name__ == '__main__':
    main()
