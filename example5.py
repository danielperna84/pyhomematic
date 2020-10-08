#!/usr/bin/python3
import time
import sys
import logging
from pyhomematic import HMConnection

logging.basicConfig(level=logging.INFO)

DEVICE1 = '001718A9A77FBC:1'  # e.g. KEQ7654321
DEVICE2 = '001718A9A77FBC'  # e.g. LEQ1234567
DEVICE3 = 'address_of_thermostat'

def systemcallback(src, *args):
    print("hier:", src)
    for arg in args:
        print(arg)
import pmatic

ccu = pmatic.CCU(address="http://192.168.178.39", credentials=("PmaticAdmin", "EPIC-SECRET-PW"))
test = ccu.api.interface_get_paramset(interface="HmIP-RF",
                                         address="001718A9A77FBC:1", paramsetKey="MASTER")
print(test)
result = ccu.api.interface_init(interface="HmIP-RF",
            url="http://192.168.178.35:9124", interfaceId="HmIP-RF")
test = ccu.api.interface_get_paramset(interface="HmIP-RF",
                                         address="001718A9A77FBC:1", paramsetKey="MASTER")
print(test)

test = pmatic.events.EventListener(ccu)
test._register_with_ccu(interface = "HmIP-RF", interfaceId = "HmIP-RF")
test = ccu.api.interface_get_paramset(interface="HmIP-RF",
                                         address="001718A9A77FBC:1", paramsetKey="MASTER")
print(test)


for room in ccu.rooms:
    print("%-30s %d devices" % (room.name, len(room.devices)))



try:
    # Create a server that listens on 127.0.0.1:7080 and identifies itself as myserver.
    # Connect to Homegear at 127.0.0.1:2001
    # Automatically start everything. Without autostart, pyhomematic.start() can be called.
    # We add a systemcallback so we can see what else happens besides the regular events.
    pyhomematic = HMConnection(
#        interface_id="myserver",
                               autostart=True,
#                               local="192.168.178.35",
#                               localport="9400",
                               systemcallback=systemcallback,
                               remotes={
                                   "wired":{
                                   "ip":"192.168.178.39",
                                   "port": 2000,
                                   "resolvenames": "json",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW"},
                                   "Funk":{
                                   "ip":"192.168.178.39",
                                   "port": 2001,
                                   "resolvenames": "json",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW"},
                                   "HmIP":{
                                   "ip":"192.168.178.39",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW",
                                   "resolvenames": "json",
                                   "port": 2010},
                                   "CUxD":{
                                   "ip":"192.168.178.39",
                                   "resolvenames": "json",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW",
                                   "port": 8701},
                                   "groups":{
                                   "ip":"192.168.178.39",
                                   "resolvenames": "json",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW",
                                   "path": "/groups",
                                   "port": 9292}
                                   }
                                   ),
except Exception:
    sys.exit(1)

sleepcounter = 0

def eventcallback(address, interface_id, key, value):
    print("CALLBACK: %s, %s, %s, %s" % (address, interface_id, key, value))

print("start devices")
test = ccu.api.interface_get_paramset(interface="HmIP-RF",
                                         address="001718A9A77FBC:1", paramsetKey="MASTER")
print(test)
print(pyhomematic.getAllSystemVariables("HmIP"))
print(pyhomematic.listBidcosInterfaces("Funk"))
print(pyhomematic.devices['ip'])

# Get level of rollershutter from 0.0 to 1.0.
print(pyhomematic.devices[DEVICE1].get_level())

# Set level of rollershutter to 50%.
pyhomematic.devices[DEVICE1].set_level(0.5)
time.sleep(10)

# Move rollershutter down.
pyhomematic.devices[DEVICE1].move_down()
time.sleep(10)

# Get level of rollershutter from 0.0 to 1.0 directly from channel.
print(pyhomematic.devices_all[DEVICE1 + ':1'].getValue("LEVEL"))

# Check if doorcontact is open by querying the device.
print(pyhomematic.devices[DEVICE2].is_open())

# Check if doorcontact is open or closed by querying the device-channel. True or False, depending on state.
print(pyhomematic.devices_all[DEVICE2 + ':1'].getValue("STATE"))

# Get Actual Temperature
print(pyhomematic.devices[DEVICE3].actual_temperature)

# Get Set Temperature
print(pyhomematic.devices[DEVICE3].set_temperature)

# Get Battery State
print(pyhomematic.devices[DEVICE3].battery_state)

# Set an eventcallback for the doorcontact that should be called when events occur.
pyhomematic.devices[DEVICE2].setEventCallback(eventcallback)
time.sleep(10)
# Now open / close doorcontact and watch the eventcallback being called.

# Stop the server thread so Python can exit properly.
pyhomematic.stop()

sys.exit(0)
