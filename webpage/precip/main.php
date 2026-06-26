<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>Home</title>
<link href="http://fonts.googleapis.com/css?family=Source+Sans+Pro:200,300,400,600,700,900" rel="stylesheet" />
<link href="../main.css" rel="stylesheet" type="text/css" media="all" />
<link href="../fonts.css" rel="stylesheet" type="text/css" media="all" />
<script src="https://d3js.org/d3.v4.min.js"></script>
</head>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>


<body>
<li>
Contingency tables counts are calculated for each model. The table definitions are:
Hits (a): where both forecast and observation are greater than or equal to a threshold;
False alarms (b): where forecast is above and observation is under a threshold;
Misses (c): where the observation is above and forecast is under a threshold;
No forecasts (d): where both forecast and observation are under the threshold.
</li>
<br>
<li>
All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid211.gif target="_blank">G211</a> grid. The model APCP 6 hour accumulation forecast files are combined to create a 24 hour forecast. These are compared to Climatology­Calibrated Precipitation Analysis (CCPA) 24 hour accumulation, valid 12Z to 12Z.
</li>
<br>
<li>
Verification statistics are computed from the contingency table counts.
Bias Score: BS=(a+b)/(a+c), measures over-forecasts (BS gt 1) or under-forecasts (BS lt 1) precipitation frequency over an area for a selected threshold.
Equitable Threat Score: ETS=(a - ar)/(a + b + c - ar), where ar is the expected number of correct forecasts above the threshold in a random forecast where forecast occurrence/non-occurrence is independent from observation/non-observation, ar=(a + b)*(a + c)/(a + b + c + d). ETS=1 means a perfect forecast. ETS le 0 means the forecast is useless. Statistical signifance is calculated using a Monte Carlo significance test using 10,000 resamples. For more information see <a href=https://www.emc.ncep.noaa.gov/users/verification/global/gfs/doc/precip_montecarlo_fyang.ppt target="_blank">here</a>.
<br>
</li>
<br>
<li>
The verification regions used for surface are:
                     <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid211.gif target="_blank">G211</a>,
                     <a href="../images/vx_masks/WEST.png" target="_blank">West</a> and
                     <a href="../images/vx_masks/EAST.png" target="_blank">East</a>.
</li>
</body>
</html>
