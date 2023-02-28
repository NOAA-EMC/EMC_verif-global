help([[
Load environment to run EMC_verif-global on Jet using Intel
]])

hpss_ver=os.getenv("hpss_ver") or ""
load(pathJoin("hpss", hpss_ver))

prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hfv3gfs/role.epic/hpc-stack/libs/intel-2022.1.2/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.2.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "2022.1.2"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2022.1.2"
load(pathJoin("hpc-impi", impi_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.10.6"
load(pathJoin("hdf5", hdf5_ver))

netcdf_ver=os.getenv("netcdf_ver") or "4.7.4"
load(pathJoin("netcdf", netcdf_ver))

nco_ver=os.getenv("nco_ver") or "4.9.1"
load(pathJoin("nco", nco_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))

prod_util_ver=os.getenv("prod_util_ver") or "1.2.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.4"
load(pathJoin("grib_util", grib_util_ver))

grads_ver=os.getenv("grads_ver") or "2.2.1"
load(pathJoin("grads", grads_ver))

prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hfv3gfs/role.epic/miniconda3/modulefiles")
miniconda3_ver=os.getenv("miniconda3_ver") or "4.12.0"
load(pathJoin("miniconda3", miniconda3_ver))

-- activate ufswm on load, deactivate on unload
if (mode() == "load") then
  local load_cmd = "conda activate ufswm"
  execute{cmd=load_cmd, modeA={"load"}}
else
  if (mode() == "unload") then
    local unload_cmd = "conda deactivate"
    execute{cmd=unload_cmd, modeA={"unload"}}
  end
end

met_ver=os.getenv("met_ver") or "9.1.3"
load(pathJoin("met", met_ver))

metplus_ver=os.getenv("metplus_ver") or "3.1.1"
load(pathJoin("metplus", metplus_ver))
