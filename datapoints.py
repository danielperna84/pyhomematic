#!/usr/bin/python3
import sys
import pprint
import random
import json
import xmlrpc.client

"""
Use this script to fetch the datapoints of the devices paired with your CCU.
Depending on the specified port different devices will be presented:
2000 -> BidCos-Wired
2001 -> BidCos-RF
2010 -> HmIP-RF

Availability of these ports may depend on the CCU version, and as of now,
Homegear has no HmIP support.

To use this script (on Linux with Python 3 installed) place it on the machines
filesystem, mark it executable (chmod 755 datapoints.py), and execute like this:
/path/to/file/datapoints.py http://ccu.ip.addr.ess:2001
This will print out all available details of your devices for you to analyze.
If you want to provide this data to someone else, append a filename (devices.json)
to the command above.
The raw JSON that's being saved isn't pretty to read, but can be imported and read
by capable applications.
Device-IDs, addresses etc. are being anonymized. So posting the results of this
script online shouldn't be an issue since no private data is leaked (unless I
forgot to overwrite something critical).

Note: this is a quick-and-dirty script with minor testing and no validation of
provided parameters. So as always, use at your own risk.
"""

args = sys.argv[1:]
if not args:
    print("Usage: ./datapoints.py http://ccu.ip.addr.ess:2001 [outfile.json]")
    sys.exit(1)

ccu = args[0]
if len(args) > 1:
    outfile = args[1]
else:
    outfile = False
proxy = xmlrpc.client.ServerProxy(ccu)

devices = proxy.listDevices()

for device in devices:
    paramsets = {}
    for i in range(len(device['PARAMSETS'])):
        try:
            paramsets[device['PARAMSETS'][i]] = proxy.getParamsetDescription(device['ADDRESS'], device['PARAMSETS'][i])
        except Exception:
            pass
    if 'CHILDREN' in device:
        for i in range(len(device['CHILDREN'])):
            device['CHILDREN'][i] = device['CHILDREN'][i][-3:]
    device['ADDRESS'] = device['ADDRESS'][-3:]
    if 'PARENT' in device:
        device['PARENT'] = device['PARENT'][-3:]
    r = random.randint(0, 5000)
    if 'PHYSICAL_ADDRESS' in device:
        device['PHYSICAL_ADDRESS'] = device['PHYSICAL_ADDRESS'] + r
    if 'RF_ADDRESS' in device:
        device['RF_ADDRESS'] = device['RF_ADDRESS'] + r
    device['PARAMSETS'] = paramsets

if not outfile:
    pprint.pprint(devices)
else:
    with open(outfile, 'w') as f:
        f.write(json.dumps(devices))
sys.exit(0)
