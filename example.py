#!/usr/bin/python3
import time, sys
import logging
logging.basicConfig(level=logging.INFO)

import homematic
try:
    # Create server
    s = homematic.create_server(interface_id="myserver",
                                autostart=True)
except:
    sys.exit(1)

sleepcounter = 0

def eventcallback(address, interface_id, key, value):
    print("%s, %s, %s, %s" % (address, interface_id, key, value))

if s:
    while not s.devices and sleepcounter < 20:
        print("Waiting for devices")
        sleepcounter += 1
        time.sleep(1)
    print(s.devices)
    print(s.devices['address_of_rollershutter_device'].level) # Level of rollershutter from 0.0 to 1.0
    s.devices['address_of_rollershutter_device'].level = 0.5 # Set level of rollershutter to 50%
    time.sleep(10)
    s.devices['address_of_rollershutter_device'].move_down() # Move rollershutter down
    time.sleep(10)
    print(s.devices_all['address_of_rollershutter_device:1'].getValue("LEVEL")) # Level of rollershutter from 0.0 to 1.0 directly from channel
    
    print(s.devices['address_of_doorcontact'].is_open) # True or False, depending on state
    print(s.devices_all['address_of_doorcontact:1'].getValue("STATE")) # True or False, depending on state
    s.devices['address_of_doorcontact'].setEventCallback(eventcallback)
    time.sleep(10)
    print("Open / close doorcontact and watch the eventcallback being called.")
    s.stop()
sys.exit(0)