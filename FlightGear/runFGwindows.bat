C:
cd C:\Program Files\FlightGear 2018.3.2
set FG_ROOT=C:\Program Files\FlightGear 2018.3.2\data

start .\\bin\fgfs ^
	--aircraft=ZivkoEdge540 ^
	--airport=LEMD ^
	--generic=socket,in,60,127.0.0.1,5502,udp,FG_protocol ^
	--timeofday=noon ^
	--fdm=null