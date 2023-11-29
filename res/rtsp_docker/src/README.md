 - There is multiple traansports (udp, multicast, tcp, http). tcp protocols are rather slow,
  but are used by go2rtc implementation (not sure if can be changed). The video players might
  select protocol (udp seems default)
    ffplay -an -rtsp_transport tcp -v debug  rtsp://ipepdvcompute3.ipe.kit.edu:5618/test
    cvlc -v --rtsp-tcp rtsp://ipepdvcompute3.ipe.kit.edu:5618/test

    ffmpeg -v debug -rtsp_transport udp -i "rtsp://ipepdvcompute3.ipe.kit.edu:5617/test" -c copy -f webm '1.vp8

  Generally I would use UDP whenever possible

 - Firewall, we need to open RTSP port, but also pairs of UDP ports which are allocated for client
   connetions. The range can be limited and this range should be open.
   
 - The problematic ports can be traced using 'firewall-cmd'
	firewall-cmd --set-log-denied=unicast
	
	firewall-cmd --zone public --add-port 5000-5010/udp
	firewall-cmd --list-ports
	
 - We might need here still to 
 