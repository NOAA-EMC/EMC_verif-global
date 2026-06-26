<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>Home</title>
<link href="http://fonts.googleapis.com/css?family=Source+Sans+Pro:200,300,400,600,700,900" rel="stylesheet" />
<link href="main.css" rel="stylesheet" type="text/css" media="all" />
<link href="fonts.css" rel="stylesheet" type="text/css" media="all" />
<script src="https://d3js.org/d3.v4.min.js"></script>
</head>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>
<?php include "globalvars.php"; ?>

<body>
<div id="pageTitle">
NCEP/EMC <?php echo $model; ?> Experiment Verification
</div>
<div id="pageContents">
<center>
<img src="images/gfs4c.png" alt="" width="150" />
<br><br>The NCEP’s Global Forecast System (GFS) is the cornerstone of NCEP’s operational production suite of numerical guidance. NCEP’s global forecasts provide deterministic and probabilistic guidance out to 16 days. The GFS provides initial and/or boundary conditions for NCEP’s other models for regional, ocean and wave prediction systems.
<br><br>Verification is done using <a href="https://github.com/NOAA-EMC/EMC_verif-global" target="_blank">EMC_verif-global</a>, which uses <a href="https://github.com/dtcenter/METplus" target="_blank">METplus</a>.
</center>
</div>
</body>
</html>
