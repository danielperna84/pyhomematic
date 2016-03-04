#!/usr/bin/python3
import time, sys
import logging
logging.basicConfig(level=logging.INFO)

DEVICE1 = 'address_of_rollershutter_device' # e.g. KEQ7654321
DEVICE2 = 'address_of_doorcontact' # e.g. LEQ1234567
def systemcallback(src, *args):
    print(src)
    for arg in args:
        print(arg)

import homematic
try:
    # Create a server that listens on 127.0.0.1:7080 and identifies itself as myserver.
    # Connect to Homegear at 127.0.0.1:2001
    # Automatically start everything. Without autostart, homematic.start() can be called.
    # We add a systemcallback so we can see what else happens besides the regular events.
    homematic.create_server(interface_id="myserver",
                            local="127.0.0.1",
                            localport=7080,
                            remote="127.0.0.1",
                            remoteport=2001,
                            autostart=True,
                            systemcallback=systemcallback)
except:
    sys.exit(1)

sleepcounter = 0

def eventcallback(address, interface_id, key, value):
    print("CALLBACK: %s, %s, %s, %s" % (address, interface_id, key, value))

if homematic.Server:
    while not homematic.devices and sleepcounter < 20:
        print("Waiting for devices")
        sleepcounter += 1
        time.sleep(1)
    print(homematic.devices)
    
    # Get level of rollershutter from 0.0 to 1.0.
    print(homematic.devices[DEVICE1].level)
    
    # Set level of rollershutter to 50%.
    homematic.devices[DEVICE1].level = 0.5
    time.sleep(10)
    
    # Move rollershutter down.
    homematic.devices[DEVICE1].move_down()
    time.sleep(10)
    
    # Get level of rollershutter from 0.0 to 1.0 directly from channel.
    print(homematic.devices_all[DEVICE1 + ':1'].getValue("LEVEL"))
    
    # Check if doorcontact is open by querying the device.
    print(homematic.devices[DEVICE2].is_open)
    
    # Check if doorcontact is open or closed by querying the device-channel. True or False, depending on state.
    print(homematic.devices_all[DEVICE2 + ':1'].getValue("STATE"))
    
    # Set an eventcallback for the doorcontact that should be called when events occur.
    homematic.devices[DEVICE2].setEventCallback(eventcallback)
    time.sleep(10)
    # Now open / close doorcontact and watch the eventcallback being called.
    
    # Stop the server thread so Python can exit properly.
    homematic.stop()
sys.exit(0)