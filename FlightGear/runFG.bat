
 ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
 ::
 :: Copyright (c) 2016 UAV Navigation, S.L. All Rights Reserved.
 ::
 :: This computer software is owned by UAV Navigation, S.L. and is
 :: protected by U.S. copyright laws and other laws and by international
 :: treaties. The right to copy, distribute, or use this software in any
 :: form is absolutely restricted to UAV Navigation, S.L.
 ::
 :: UAV Navigation, S.L.
 :: Av Pirineos 7, B11
 :: SS de los Reyes, 28703 Madrid - SPAIN
 :: http://www.uavnavigation.com/
 ::
 ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::
:: This script file is used to invoke FlightGear together with the necessary
:: options to run together with the VECTOR-HIL simulator platform.
::
:: Please modify the paths below according to your installation.
::

C:
cd C:\Program Files\FlightGear 2018.2.2
set FG_ROOT=C:\Program Files\FlightGear 2018.2.2\data

start .\\bin\fgfs ^
	--aircraft=ZivkoEdge540 ^
	--airport=LEMD ^
	--generic=socket,in,60,127.0.0.1,5502,udp,FG_protocol ^
	--timeofday=noon ^
	--fdm=null