#!/bin/bash

/usr/games/fgfs --fg-root=/usr/share/games/flightgear \
	--aircraft=ZivkoEdge540 \
	--airport=LEMD \
	--generic=socket,in,60,127.0.0.1,5502,udp,FG_protocol \
	--timeofday=noon \
	--fdm=null