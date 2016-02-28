#!/usr/bin/python3
import time, sys
import logging
logging.basicConfig(level=logging.INFO)

import homematic
try:
    s = homematic.create_server(interface_id="myserver",
                                autostart=True)
except:
    sys.exit(1)

if s:
    time.sleep(10)
    print(s.devices)
    s.stop()
sys.exit(0)