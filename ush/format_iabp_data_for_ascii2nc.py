'''
Program Name: format_iabp_data_for_ascii2nc.py
Contact(s): Mallory Row
Abstract: This script format IABP data into a 
          ascii2nc compliant text file
'''

from __future__ import (print_function, division)
import os
import datetime
import pandas as pd

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
DATE = os.environ['DATE']
DATE_dt = datetime.datetime.strptime(DATE, '%Y%m%d')
DATE_YYYY = DATE_dt.strftime('%Y')
DATE_DOY = DATE_dt.strftime('%j')

# Set up information
iabp_DATE_data_dir = os.path.join(DATA, RUN, 'data',
                                  'iabp', DATE)
iabp_DATE_file = os.path.join(iabp_DATE_data_dir, '..', 'iabp.'+DATE)
iabp_var_list = ['BP', 'Ts', 'Ta']
ascii2nc_file_cols = ['Message_Type', 'Station_ID', 'Valid_Time', 'Lat', 'Lon',
                      'Elevation', 'Variable_Name', 'Level', 'Height',
                      'QC_String', 'Observation_Value']

# Combine and format for ascii2nc
iabp_DATE_ascii2nc_data = pd.DataFrame(columns=ascii2nc_file_cols)
nfiles_iabp_DATE_data_dir = len(os.listdir(iabp_DATE_data_dir))
if nfiles_iabp_DATE_data_dir != 0:
    for iabp_region_DATE_filename in os.listdir(iabp_DATE_data_dir):
        iabp_region_DATE_file = os.path.join(iabp_DATE_data_dir,
                                             iabp_region_DATE_filename)
        iabp_region_DATE_data = pd.read_csv(iabp_region_DATE_file, sep=";",
                                            skipinitialspace=True, header=0,
                                            dtype=str)
        iabp_region_DATE_cols = list(iabp_region_DATE_data.columns)
        iabp_region_DATE_ascii2nc = pd.DataFrame(columns=ascii2nc_file_cols)
        idx_ascii2nc = 0
        for idx in iabp_region_DATE_data.index:
            iabp_region_DATE_data_idx = iabp_region_DATE_data.loc[idx,:]
            iabp_region_DATE_data_idx_Year = (
                iabp_region_DATE_data_idx.loc['Year']
            )
            iabp_region_DATE_data_idx_DOY = (
                iabp_region_DATE_data_idx.loc['DOY']
            )
            iabp_region_DATE_data_idx_Hour = (
                iabp_region_DATE_data_idx.loc['Hour']
            )
            iabp_region_DATE_data_idx_Min = (
                iabp_region_DATE_data_idx.loc['Min']
            )
            iabp_region_DATE_data_idx_BuoyID = (
                iabp_region_DATE_data_idx.loc['BuoyID']
            )
            iabp_region_DATE_data_idx_Lat = (
                iabp_region_DATE_data_idx.loc['Lat']
            )
            iabp_region_DATE_data_idx_Lon = (
                iabp_region_DATE_data_idx.loc['Lon']
            )
            iabp_region_DATE_data_idx_datetime = datetime.datetime.strptime(
                iabp_region_DATE_data_idx_Year+' '
                +str(int(float(iabp_region_DATE_data_idx_DOY)))+' '
                +iabp_region_DATE_data_idx_Hour+' '
                +iabp_region_DATE_data_idx_Min,
                '%Y %j %H %M'
            )
            if float(iabp_region_DATE_data_idx_Year) == float(DATE_YYYY) \
                    and float(iabp_region_DATE_data_idx_DOY) \
                    >= float(DATE_DOY) \
                    and float(iabp_region_DATE_data_idx_DOY) \
                    < (float(DATE_DOY)+1):
                for iabp_var in iabp_var_list:
                    iabp_region_DATE_data_idx_col_val_str = (
                        iabp_region_DATE_data_idx.loc[iabp_var]
                    )
                    if iabp_var == 'BP':
                        iabp_var_grib_name = 'PRES'
                        iabp_var_grib_level = '0'
                    elif iabp_var == 'Ts':
                        iabp_var_grib_name = 'TMP'
                        iabp_var_grib_level = '0'
                    elif iabp_var == 'Ta':
                        iabp_var_grib_name = 'TMP'
                        iabp_var_grib_level = '2'
                    if iabp_region_DATE_data_idx_col_val_str == '-999.00':
                        iabp_region_DATE_data_idx_col_val = 'NA'
                    else:
                        if iabp_var in ['Ts', 'Ta']:
                            iabp_region_DATE_data_idx_col_val = str(
                                float(iabp_region_DATE_data_idx_col_val_str)
                                +273.15
                            )
                        else:
                            iabp_region_DATE_data_idx_col_val = str(
                                float(iabp_region_DATE_data_idx_col_val_str)
                                *100
                            )
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Message_Type'
                    ] = 'SFCSHP'
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Station_ID'
                    ] = iabp_region_DATE_data_idx_BuoyID
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Valid_Time'
                    ] = iabp_region_DATE_data_idx_datetime.strftime('%Y%m%d_%H%M%S')
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Lat'
                    ] = iabp_region_DATE_data_idx_Lat
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Lon'
                    ] = iabp_region_DATE_data_idx_Lon
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Elevation'
                    ] = '0'
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Variable_Name'
                    ] = iabp_var_grib_name
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Level'
                    ] = 'NA'
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Height'
                    ] = iabp_var_grib_level
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'QC_String'
                    ] = 'NA'
                    iabp_region_DATE_ascii2nc.loc[
                        idx_ascii2nc, 'Observation_Value'
                    ] = iabp_region_DATE_data_idx_col_val
                    idx_ascii2nc+=1
        iabp_DATE_ascii2nc_data = (
            iabp_DATE_ascii2nc_data \
            .append(iabp_region_DATE_ascii2nc) \
            .reset_index(drop=True)
        )
iabp_DATE_ascii2nc_data_string = (
    iabp_DATE_ascii2nc_data.to_string(header=False, index=False)
)
with open(iabp_DATE_file,'a') as output_file:
    output_file.write(iabp_DATE_ascii2nc_data_string)

print("END: "+os.path.basename(__file__))
