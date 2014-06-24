<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Pool Control</title>
<style type="text/css" media="screen">
body { background: #e7e7e7; font-family: Verdana, sans-serif; font-size: 11pt; }
#page { background: #ffffff; margin: 50px; border: 2px solid #c0c0c0; padding: 10px; }
#header { background: #4b6983; border: 2px solid #7590ae; text-align: center; padding: 10px; color: #ffffff; }
#header h1 { color: #ffffff; }
#body { padding: 10px; }
span.tt { font-family: monospace; }
span.bold { font-weight: bold; }
a:link { text-decoration: none; font-weight: bold; color: #C00; background: #ffc; }
a:visited { text-decoration: none; font-weight: bold; color: #999; background: #ffc; }
a:active { text-decoration: none; font-weight: bold; color: #F00; background: #FC0; }
a:hover { text-decoration: none; color: #C00; background: #FC0; }
</style>
</head>
<body>
<?php
	print "<p>Pool Control";
	print "<p>".$_GET["circuit"].",".$_GET["state"];
	if ($_GET["circuit"]=="" or $_GET["state"]=="") {
		print "<p>Getting Status";
		$command = "/usr/bin/python /var/www/poolread.py";
		exec($command,$output);
		foreach ($output as $o) {
			print "<p>$o\n";
		}
	} else {
		$command = "/usr/bin/python /var/www/poolcontrol.py ".$_GET["circuit"]." ".$_GET["state"];
		print "<p>$command<p>";
		print exec($command." >> /tmp/poolcontrol.log 2>&1");
	}
	//foreach ($output as $o) {
	//	print "<p>$o\n";
	//}

?>
</body>
</html>
