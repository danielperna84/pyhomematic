#!/usr/bin/python3

import time
import sys
import logging
from pyhomematic import HMConnection
logging.basicConfig(level=logging.INFO)
p = HMConnection(interface_id="myserver", autostart=True, remotes={"rf":{"ip":"192.168.1.23","port": 2001}})
#MEQ1585773