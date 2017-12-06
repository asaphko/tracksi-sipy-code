#first - beep!
import audiovisual
from audiovisual import AV
av = AV()
av.beep()

#WiFi - setup known nets:
known_nets = [('MEO-D9555F', '2F8811E281')]

from machine import UART
import machine
import os
import time

#WiFi setup
if machine.reset_cause() != machine.SOFT_RESET: #needed to avoid losing connection after a soft reboot
	from network import WLAN
	wl = WLAN()
	wl.mode(WLAN.STA)
	available_nets = wl.scan()
	nets = frozenset([e.ssid for e in available_nets])

	known_nets_names = frozenset([e[0] for e in known_nets])
	net_to_use = list(nets & known_nets_names)

	try:
		net_to_use = net_to_use[0]
		pwd = dict(known_nets) [net_to_use]
		sec = [e.sec for e in available_nets if e.ssid == net_to_use][0]
		wl.connect(net_to_use, (sec, pwd), timeout=2000)
		print('Connected to wifi!')
	except:
		print('Could not connect to wifi........')

#initiates the UART (USB) connection
uart = UART(0, baudrate=115200)
os.dupterm(uart)

#sleep for 1 SEC
time.sleep(1)

#continue
machine.main('main.py')
