'''
Program Name: format_iabp_data_for_ascii2nc.py
Contact(s): Mallory Row
Abstract: This script creates a various ice related vx masks
          from observation data.
'''

from __future__ import (print_function, division)
import os
import numpy as np
import netCDF4 as netcdf
import glob

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
DATE = os.environ['DATE']
obtype = os.environ['obtype']
sea_ice_thresh = float(os.environ['sea_ice_thresh'])

# Get data files
obtype_data_dir = os.path.join(DATA, RUN, 'data', obtype)
obtype_file_list = glob.glob(
    os.path.join(obtype_data_dir, obtype+'.'+DATE+'*')
)

def write_vx_mask_nc_file(obtype, obtype_file,
                          vx_mask_name, vx_mask_values, vx_mask_ncattrs_dict):
    """! This sets up the basic netCDF file information for
         the vx masking file

         Args:
             obtype               - string of observation type/name
             obtype_file          - string of full path to
                                    observation data file to create
                                    vx mask from
             vx_name_name         - string of vx mask name
             vx_mask_values       - array of 0s and 1s defining the vx mask
             vx_mask_ncattrs_dict - dictionary with attributes for vx mask
                                    variable

         Returns:
    """
    vx_mask_file = obtype_file+'_'+vx_mask_name.lower()+'_vx_mask.nc'
    print("Saving vx mask file for"+vx_mask_name+" as "+vx_mask_file)
    obtype_data = netcdf.Dataset(obtype_file)
    vx_mask_nc = netcdf.Dataset(vx_mask_file, 'w', format='NETCDF4')
    if obtype in ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl']:
        vx_mask_nc.setncattr(
            'MET_version', 'V'+os.environ['MET_version']
        )
        vx_mask_nc.setncattr('Projection', 'LatLon')
        vx_mask_nc.setncattr(
            'lat_ll', str(obtype_data.getncattr('southernmost_latitude'))+' '
            +str(obtype_data.getncattr('geospatial_lat_units'))
        )
        vx_mask_nc.setncattr(
            'lon_ll', str(obtype_data.getncattr('westernmost_longitude'))+' '
            +str(obtype_data.getncattr('geospatial_lon_units'))
        )
        vx_mask_nc.setncattr(
            'delta_lat', obtype_data.getncattr('spatial_resolution')
        )
        vx_mask_nc.setncattr(
            'delta_lon', obtype_data.getncattr('spatial_resolution')
        )
        vx_mask_nc.setncattr(
            'Nlat', str(len(obtype_lat))+' grid_points'
        )
        vx_mask_nc.setncattr(
            'Nlon', str(len(obtype_lon))+' grid_points'
        )
    for dim in ['lat', 'lon']:
        dim_values = obtype_data.variables[dim][:]
        dim_dimensions = obtype_data.variables[dim].dimensions
        dim_datatype = obtype_data.variables[dim].datatype
        vx_mask_nc.createDimension(dim, len(dim_values))
        vx_mask_nc_dim = vx_mask_nc.createVariable(
            dim, dim_datatype, dim_dimensions
        )
        for attr in obtype_data.variables[dim].ncattrs():
            dim_ncattrs_dict = {}
            if attr in ['long_name', 'units', 'standard_name']:
                dim_ncattrs_dict[attr] = (
                    obtype_data.variables[dim].getncattr(attr)
                )
            vx_mask_nc_dim.setncatts(dim_ncattrs_dict)
        vx_mask_nc_dim[:] = dim_values
    vx_mask_nc_vx_mask = vx_mask_nc.createVariable(
        vx_mask_name, dim_datatype, ('lat', 'lon',)
    )
    vx_mask_nc_vx_mask.setncatts(vx_mask_ncattrs_dict)
    vx_mask_nc_vx_mask[:] = vx_mask_values
    vx_mask_nc.close()

# Read observation data and create vx masks
for obtype_file in obtype_file_list:
    # Read observation data
    obtype_data = netcdf.Dataset(obtype_file)
    if obtype in ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl']:
        obtype_lat = obtype_data.variables['lat'][:]
        obtype_lon = obtype_data.variables['lon'][:]
        obtype_sea_ice_fraction = (
            obtype_data.variables['sea_ice_fraction'][0,:,:]
        )
        if not np.ma.is_masked(obtype_sea_ice_fraction):
            obtype_sea_ice_fraction = np.ma.masked_array(
                obtype_sea_ice_fraction
            )
        obtype_sea_ice_fraction.set_fill_value(0)
        obtype_sea_ice_fraction = obtype_sea_ice_fraction.filled()
        obtype_mask = obtype_data.variables['mask'][0,:,:]
    obtype_data.close()
    # Create ice vx mask
    print("Creating sea ice mask for values >="+str(sea_ice_thresh)+" "
          +"from "+obtype_file)
    ice_vx_mask_name = 'SEA_ICE'
    obtype_sea_ice_fraction_lt_thresh_mask = np.ma.getmask(
        np.ma.masked_less(obtype_sea_ice_fraction, sea_ice_thresh)
    )
    ice_vx_mask_values = np.ones_like(obtype_sea_ice_fraction)
    ice_vx_mask_values = np.ma.masked_where(
        obtype_sea_ice_fraction_lt_thresh_mask, ice_vx_mask_values
    )
    ice_vx_mask_values.set_fill_value(0)
    ice_vx_mask_values = ice_vx_mask_values.filled()
    ice_vx_mask_ncattrs_dict = {
        'long_name': obtype+' ice fraction >= '+str(sea_ice_thresh)+' '
            +' on '+DATE,
    }
    write_vx_mask_nc_file(obtype, obtype_file,
                          ice_vx_mask_name,
                          ice_vx_mask_values,
                          ice_vx_mask_ncattrs_dict)
    # Create ice free vx mask
    print("Creating sea ice free mask for values <"+str(sea_ice_thresh)+" "
          +"from "+obtype_file)
    ice_free_vx_mask_name = 'SEA_ICE_FREE'
    obtype_sea_ice_fraction_ge_thresh_mask = np.ma.getmask(
        np.ma.masked_greater_equal(obtype_sea_ice_fraction, sea_ice_thresh)
    )
    ice_free_vx_mask_values = np.ones_like(obtype_sea_ice_fraction)
    ice_free_vx_mask_values = np.ma.masked_where(
        obtype_sea_ice_fraction_ge_thresh_mask, ice_free_vx_mask_values
    )
    if obtype in ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl']:
        ice_free_vx_mask_values = np.ma.masked_where(
            obtype_mask == 2, ice_free_vx_mask_values
        )
    ice_free_vx_mask_values.set_fill_value(0)
    ice_free_vx_mask_values = ice_free_vx_mask_values.filled()
    ice_free_vx_mask_ncattrs_dict = {
        'long_name': obtype+' ice fraction < '+str(sea_ice_thresh)+' '
            +' on '+DATE,
    }
    write_vx_mask_nc_file(obtype, obtype_file,
                          ice_free_vx_mask_name,
                          ice_free_vx_mask_values,
                          ice_free_vx_mask_ncattrs_dict)
    # Create ice polar vx mask
    print("Creating sea ice polar (60N-90N, 60S-90S) mask for values "
          +">="+str(sea_ice_thresh)+" from "+obtype_file)
    ice_polar_vx_mask_name = 'SEA_ICE_POLAR'
    polar_mask = np.ma.getmask(
        np.ma.masked_inside(obtype_lat, -60, 60)
    )
    ice_polar_vx_mask_values = ice_vx_mask_values
    ice_polar_vx_mask_values[polar_mask == True,:] = np.ma.masked
    ice_polar_vx_mask_ncattrs_dict = {
        'long_name': obtype+'polar (60N-90N, 60S-90S) ice fraction >= '
                     +str(sea_ice_thresh)+'  on '+DATE,
    }
    write_vx_mask_nc_file(obtype, obtype_file,
                          ice_polar_vx_mask_name,
                          ice_polar_vx_mask_values,
                          ice_polar_vx_mask_ncattrs_dict)
    # Create ice free polar vx mask
    print("Creating sea ice free polar (60N-90N, 60S-90S) mask for values "
          +"<"+str(sea_ice_thresh)+" from "+obtype_file)
    ice_free_polar_vx_mask_name = 'SEA_ICE_FREE_POLAR'
    polar_mask = np.ma.getmask(
        np.ma.masked_inside(obtype_lat, -60, 60)
    )
    ice_free_polar_vx_mask_values = ice_free_vx_mask_values
    ice_free_polar_vx_mask_values[polar_mask == True,:] = np.ma.masked
    ice_free_polar_vx_mask_ncattrs_dict = {
        'long_name': obtype+'polar (60N-90N, 60S-90S) ice fraction < '
                     +str(sea_ice_thresh)+'  on '+DATE,
    }
    write_vx_mask_nc_file(obtype, obtype_file,
                          ice_free_polar_vx_mask_name,
                          ice_free_polar_vx_mask_values,
                          ice_free_polar_vx_mask_ncattrs_dict)

print("END: "+os.path.basename(__file__))
