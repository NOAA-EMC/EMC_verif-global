help([[
Load environment to run EMC_verif-global on Hera using Intel
]])

hpss_ver=os.getenv("hpss_ver") or ""
load(pathJoin("hpss", hpss_ver))

prepend_path("MODULEPATH", "/scratch2/NCEPDEV/nwprod/hpc-stack/libs/hpc-stack/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.1.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "18.0.5.274"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2018.0.4"
load(pathJoin("hpc-impi", impi_ver))

netcdf_ver=os.getenv("netcdf_ver") or "4.7.4"
load(pathJoin("netcdf", netcdf_ver))

nco_ver=os.getenv("nco_ver") or "4.9.1"
load(pathJoin("nco", nco_ver))

prod_util_ver=os.getenv("prod_util_ver") or "1.2.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.2"
load(pathJoin("grib_util", grib_util_ver))

grads_ver=os.getenv("grads_ver") or "2.2.1"
load(pathJoin("grads", grads_ver))

prepend_path("MODULEPATH", "/contrib/anaconda/modulefiles")

anaconda_ver=os.getenv("anaconda_ver") or "latest"
load(pathJoin("anaconda", anaconda_ver))

prepend_path("MODULEPATH", "/contrib/met/modulefiles")

met_ver=os.getenv("met_ver") or "9.1"
load(pathJoin("met", met_ver))

prepend_path("MODULEPATH", "/contrib/METplus/modulefiles")

metplus_ver=os.getenv("metplus_ver") or "3.1"
load(pathJoin("metplus", metplus_ver))
