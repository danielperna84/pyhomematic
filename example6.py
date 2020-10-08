#!/usr/bin/python3
import time
import sys
import logging
import pprint
logging.basicConfig(level=logging.DEBUG)

def syscb(src, *args):
    pprint.pprint(src)
    for arg in args:
        #print('')
        pprint.pprint(arg)

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


from pyhomematic import HMConnection

#pyhomematic = HMConnection(remote="192.168.178.39", remoteport=2001, systemcallback=syscb)
pyhomematic = HMConnection(
                               systemcallback=syscb,
                               remotes={
                                   "HmIP":{
                                   "ip":"192.168.178.39",
                                   "username":"PmaticAdmin", 
                                   "password": "EPIC-SECRET-PW",
                                   "resolvenames": "json",
                                   "port": 2010}
                                   }
                                   )


#from xml.dom import minidom

# parse an xml file by name
# mydoc = minidom.parse('tclrega-script.xml')

# items = mydoc.getElementsByTagName('item')  

from xmlrpc.client import ServerProxy
p = ServerProxy("http://192.168.178.39:2010")
t = p.getDeviceDescription("001658A99FD1E2:1")
print (t)
t = p.getParamsetDescription("001658A99FD1E2:1", "MASTER")
print (t)
t = p.getParamsetDescription("001718A9A77FBC:4", "VALUES")
print (t)
t = p.getParamset("001718A9A77FBC:4", "MASTER")
print (t)
t = p.getParamsetId("001718A9A77FBC:4", "MASTER")
print (t)




print('DEVICES: ' + str(pyhomematic.devices))

pyhomematic.stop()

sys.exit(0)
