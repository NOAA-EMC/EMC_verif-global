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

<style>
#navbar {
  overflow: hidden;
  position: absolute;
  width: 100%;
  margin-top: 5px;
  margin-bottom: 5px;
}
#navbar a {
  float: left;
  display: block;
  color: #666;
  text-align: center;
  padding-right: 20px;
  text-decoration: none;
  font-size: 17px;
}
#navbar a:hover {
  background-color: #ddd;
  color: black;
}
#navbar a.active {
  background-color: #4CAF50;
  color: white;
  }

.button {
  padding: 1em 1em;
  width: 150px;
  text-align: center;
  text-decoration:  none;
  font-family: 'Source Sans Pro', sans-serif;
  font-size: 12pt;
  font-weight: 700;
  color: rgba(255,255,255,1);
  background-color: #112e51;
  padding: 1px;
  width: 150px;
  height: 100%;
}
</style>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>

<?php include "scorecard_globalvars.php"; ?>

<body>
<div id="pageTitle">
<?php echo $home_title; ?>
</div>
<div id="pageContents"  style="left: 0px; padding-top: 10px;">
<p align="center">
<iframe src="header.html" width="1100" height="65" style="border:none;" scrolling="no"></iframe>
<iframe src="scorecard.html" width="1100" height="750" style="border:none;" scrolling="yes"></iframe>
<iframe src="legend.html" width="1000" height="175" style="border:none;padding-left:75px;padding-top:10px" scrolling="no"></iframe>
</p>
</div>
</body>
</html>
