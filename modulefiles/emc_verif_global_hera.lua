help([[
Load environment to run EMC_verif-global on Hera using Intel
]])

hpss_ver=os.getenv("hpss_ver") or ""
load(pathJoin("hpss", hpss_ver))

gnu_ver=os.getenv("gnu_ver") or "9.2.0b"
load(pathJoin("gnu", gnu_ver))

intel_tools_ver=os.getenv("intel_tools_ver") or "2023.2.0"
load(pathJoin("intel-tools",intel_tools_ver))

netcdf_ver=os.getenv("netcdf_ver","4.7.2")
load(pathJoin("netcdf",netcdf_ver))

nco_ver=os.getenv("nco_ver","5.1.6")
load(pathJoin("nco",nco_ver))

grads_ver=os.getenv("grads_ver","2.2.3")
load(pathJoin("grads",grads_ver))

imagemagick_ver=os.getenv("imagemagick_ver","7.1.1-11")
load(pathJoin("imagemagick",imagemagick_ver))

prepend_path("MODULEPATH", "/scratch2/NCEPDEV/nwprod/hpc-stack/libs/hpc-stack/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.1.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "2022.1.2"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2018.0.4"
load(pathJoin("hpc-impi", impi_ver))

prod_util_ver=os.getenv("prod_util_ver") or "1.2.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.3"
load(pathJoin("grib_util", grib_util_ver))

prepend_path("MODULEPATH", "/contrib/anaconda/modulefiles")

anaconda_ver=os.getenv("anaconda_ver") or "latest"
load(pathJoin("anaconda", anaconda_ver))

prepend_path("MODULEPATH", "/contrib/met/modulefiles")

met_ver=os.getenv("met_ver") or "9.1"
load(pathJoin("met", met_ver))

prepend_path("MODULEPATH", "/contrib/METplus/modulefiles")

metplus_ver=os.getenv("metplus_ver") or "3.1"
load(pathJoin("metplus", metplus_ver))
