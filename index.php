<!DOCTYPE HTML>
	
<html>

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>LogBook - entry</title>
	<link rel="stylesheet" type="text/css" href="files/style.css" media="screen" />
	<link rel="shortcut icon" href="files/fuel.ico" />
</head>

<body>

<section id=main>
<article>

<header>
<h1>LogBook - Vstupní Formulář</h1>
</header>

<form action="fuel_input.php" target="_blank">
	Vozidlo:
	<select name="auto" size="1">
	<?php
		$con = mysqli_connect("localhost","root","1234","logbook");
		
		$sql = "SELECT id,name FROM machine WHERE active=1";
		
		if ($result=mysqli_query($con,$sql))
		{
			// get field information
			while($fielddata=mysqli_fetch_array($result))
			{
				printf("<option value=\"%d\">%s\n",$fielddata[0],$fielddata[1]);
			}
			// free result set
			mysqli_free_result($result);
		}
		else
		{
			echo "<option value=\"1\">RRrrrRRR\n";
			echo "<option value=\"2\">Aaauujo\n";
			echo "<option value=\"3\">Vrrrran\n";
		}
		
		mysqli_close($con);
	?>
	</select><a href=#>jiné</a><br>
	Najeto (celková hodnota): <input type="text" size="10" name="najeto" value="123456">km<br>
	Natankováno: <input type="text" size="10" name="natankovano" value="50.0">l<br>
	Čerpací stanice:
	<select name="cerpacka" size="1">
		<option value="1">Neznámá
		<option value="2">LukOil Trutnov
		<option value="3">OMW Moravská Třebová
	</select><a href=#>jiná</a><br>
	Poznámka: <textarea rows="4" cols="15" name="poznamka"></textarea><br>
</form>

</article>
</section><!--main-->

</body>

</html>