# EMC_verif-global
Package that uses MET and METplus for verifying the GFS.

This verification package was created to support the efforts at EMC to move to using the METplus authoritative verification repository, as directed under NGGPS. Previously, EMC had been using the NCEP-EMC Global NWP Model Verification Package, which uses Verification Statistics DataBase (VSDB) as its verification code.

This package has been designed to initially recreate all the verification capabilities that were present within the VSDB Global Verification Package:
1. Grid-to-Grid Verification: The first step in this verification is producing regular and anomalous partial sums for various variables at various pressure levels, as well as surface fields. Gridded model forecasts are verified aganist a gridded analysis. The second step invloves creating statistical plots and scorecard from the archived regular and anomalous partial sum files. Additionally, these plots can be sent, along with a website template, to a web server for easy display.
2. Grid-to-Observations Verification: The first step in this verification is producing regular partial sums for various variables at various pressure levels, as well as surface fields. Gridded model forecasts are verified aganist observations. The second step invloves creating statistical plots from the archived regular partial sum files. Additionally, these plots can be sent, along with a website template, to a web server for easy display.
3. Precipitation Verification: The first step in this verification is producing contingency table counts for precipitation accumulations at various thresholds. Gridded model forecasts are verified against observations. At this time only 24 hour preciptation accumulations compared to CCPA are supported. The second step invloves creating statistical plots from the archived contingency table count files. Additionally, these plots can be sent, along with a website template, to a web server for easy display.
4. Satellite Verification: The first step in this verification is producing regular partial sums for SST and sea-ice coverage. Gridded model forecasts are verified against satellite analysis files. The second step involves creating statistical plots from the archive regular partial sum files. Additionally, these plots can be sent, along with a website template, to a web server for easy display.
6. 2D Lat-Lon Maps Verification: Model forecasts for various variables are compared amongst other models and observations. The mean errors are displayed on a lat-lon grid as well as zonal means.
7. Data Assimilation Verification: Similar to the 2D lat-lon maps verification, but the model GDAS analysis increments and ensemble mean and spread are plotted.

This package can be run standalone. It has also been incorporated to run the first steps for grid-to-grid, grid-to-observations, and precipitation verification within GFS version 16 Global Workflow (https://github.com/NOAA-EMC/global-workflow).

EMC_verif-global depends on the following prerequisites to be available on the system:
* workload management platform / scheduler - LSF or SLURM
* python version 3.11.7 or 3.12.2 or newer
* MET version 12.0.1 (https://github.com/dtcenter/MET)
* METplus version 6.0.0 (https://github.com/dtcenter/METplus)
* NCEPLIBS-grib_util
* NCEPLIBS-prod_util
* NetCDF (Network Common Data Form)
* NetCDF Operators (NCO)

EMC_verif-global is supported on the following machines:
* WCOSS2 (Cactus and Dogwood)
* Ursa
* Gaea-C6

For questions or issues, please e-mail Mallory Row (mallory.row@noaa.gov).

# Running EMC-verif-global
## 1. Set up configuration file
There is an example configuration file in parm/config named *config.vrfy* to serve as a reference for users. Users can copy and make their own configuration files for their verification needs and can have numerous configuration files for various uses and experiments. Users are free to name their configuration files however they wish. Within the configuration file are switches to run the various types of verifications listed above. To run, set the switch to YES, if not set the switch to NO. Then, follows a section of settings that generally apply to running all the verification types. Finally, each verification type/switch has its own section of settings specifically related to it. Setting up a configuration file is the only change a user needs to do to run EMC_verif-global.

## 2. Run
To run, users will move to the /ush directory. Here is the script *drive_emc_verif_global.py* that runs EMC_verif-global. It takes one run time agrument which is the path to the configuration file that the user wants to run with. An example run time command may look like below

```
python drive_emc_verif_global.py ../parm/config/config.vrfy
```

# Known issues
Pandas library versions 2.1.0 and greater will return warnings when running Python plotting scripts about incompatible dtypes. These warnings can be ignored, but note that future versions of Pandas (v3.0.0) will turn these warnings into errors. Avoid using Pandas v3.0.0 until EMC_verif-global has been updated to be compatible.
