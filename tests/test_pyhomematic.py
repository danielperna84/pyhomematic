import unittest
import logging
import time
import socket

from pyhomematic import vccu
from pyhomematic import HMConnection

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 2001
DEFAULT_INTERFACE_CLIENT = "test"
DEFAULT_REMOTE = "default"

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

class Test_1_Pyhomematic(unittest.TestCase):
    def setUp(self):
        LOG.info("TestPyhomematic.setUp")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        self.localport = s.getsockname()[1]
        s.close()
        self.vccu = vccu.ServerThread(local=DEFAULT_IP,
                                      localport=self.localport)
        self.vccu.start()
        time.sleep(0.5)

    def tearDown(self):
        LOG.info("TestPyhomematic.tearDown")
        self.vccu.stop()

    def test_0_pyhomematic_noinit(self):
        LOG.info("TestPyhomematic.test_0_pyhomematic_noinit")
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
        LOG.info("TestPyhomematic.test_1_pyhomematic_init")
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

if __name__ == '__main__':
    unittest.main()
