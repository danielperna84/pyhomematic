import unittest
import os
import logging
import time
import socket
import json

from pyhomematic import vccu
from pyhomematic import HMConnection
from pyhomematic import devicetypes

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 2001
DEFAULT_INTERFACE_CLIENT = "test"
DEFAULT_REMOTE = "default"
SUPPORTED_DEVICES_JSON = "pyhomematic/devicetypes/json/device_details.json"
SCRIPT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
with open(os.path.join(BASE_DIR, SUPPORTED_DEVICES_JSON)) as fptr:
    DEVICES = json.load(fptr)

class Test_0_VCCU(unittest.TestCase):
    def setUp(self):
        LOG.info("TestVCCU.setUp")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        self.localport = s.getsockname()[1]
        s.close()
        self.vccu = vccu.ServerThread(local=DEFAULT_IP,
                                      localport=self.localport)
        self.vccu.start()

    def tearDown(self):
        LOG.info("TestVCCU.tearDown")
        self.vccu.stop()

    def test_vccu_startup(self):
        LOG.info("TestVCCU.test_vccu_startup")
        self.assertTrue(self.vccu.is_alive())

class Test_1_PyhomematicBase(unittest.TestCase):
    def setUp(self):
        LOG.debug("TestPyhomematicBase.setUp")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        self.localport = s.getsockname()[1]
        s.close()
        self.vccu = vccu.ServerThread(local=DEFAULT_IP,
                                      localport=self.localport)
        self.vccu.start()
        time.sleep(0.5)

    def tearDown(self):
        LOG.debug("TestPyhomematicBase.tearDown")
        self.vccu.stop()

    def test_0_pyhomematic_noinit(self):
        LOG.info("TestPyhomematicBase.test_0_pyhomematic_noinit")
        client = HMConnection(
            interface_id=DEFAULT_INTERFACE_CLIENT,
            autostart=False,
            remotes={
                DEFAULT_REMOTE: {
                    "ip": DEFAULT_IP,
                    "port": self.localport,
                    "connect": False
                }
            }
        )
        client.start()
        time.sleep(2)
        servicemessages = client.getServiceMessages(DEFAULT_REMOTE)
        self.assertEqual(len(servicemessages), 1)
        self.assertEqual(servicemessages[0][0], 'VCU0000001:1')
        client.stop()

    def test_1_pyhomematic_init(self):
        LOG.info("TestPyhomematicBase.test_1_pyhomematic_init")
        client = HMConnection(
            interface_id=DEFAULT_INTERFACE_CLIENT,
            autostart=False,
            remotes={
                DEFAULT_REMOTE: {
                    "ip": DEFAULT_IP,
                    "port": self.localport,
                    "connect": True
                }
            }
        )
        client.start()
        time.sleep(2)
        servicemessages = client.getServiceMessages(DEFAULT_REMOTE)
        self.assertEqual(len(servicemessages), 1)
        self.assertEqual(servicemessages[0][0], 'VCU0000001:1')
        self.assertIsInstance(client.devices, dict)
        devices = client.devices.get(DEFAULT_REMOTE)
        self.assertIsInstance(devices, dict)
        self.assertGreater(len(devices.keys()), 0)
        client.stop()

class Test_2_PyhomematicDevices(unittest.TestCase):
    def setUp(self):
        LOG.debug("TestPyhomematicDevices.setUp")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        self.localport = s.getsockname()[1]
        s.close()
        self.vccu = vccu.ServerThread(local=DEFAULT_IP,
                                      localport=self.localport)
        self.vccu.start()
        time.sleep(0.5)
        self.client = HMConnection(
            interface_id=DEFAULT_INTERFACE_CLIENT,
            autostart=False,
            remotes={
                DEFAULT_REMOTE: {
                    "ip": DEFAULT_IP,
                    "port": self.localport,
                    "connect": True
                }
            }
        )
        self.client.start()
        time.sleep(2)

    def tearDown(self):
        LOG.debug("TestPyhomematicDevices.tearDown")
        self.client.stop()
        self.vccu.stop()

    def test_0_pyhomematic_classes(self):
        LOG.info("TestPyhomematicDevices.test_0_pyhomematic_classes")
        devices = self.client.devices.get(DEFAULT_REMOTE)
        for _, deviceobject in devices.items():
            deviceclass = devicetypes.SUPPORTED.get(deviceobject.TYPE, None)
            devicedata = DEVICES.get(deviceobject.TYPE, {})
            if deviceclass:
                self.assertIsInstance(deviceobject, deviceclass)
            else:
                if not devicedata.get("supported", True):
                    LOG.info("Unsupported device: %s" % deviceobject.TYPE)
                else:
                    LOG.warning("Device class missing for: %s" % deviceobject.TYPE)

if __name__ == '__main__':
    unittest.main()
