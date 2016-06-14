import logging
from pyhomematic.devicetypes import generic
from pyhomematic.devicetypes import sensors
from pyhomematic.devicetypes import switches
from pyhomematic.devicetypes import thermostats

LOG = logging.getLogger(__name__)

try:
    UNSUPPORTED = generic.HMDevice
    SUPPORTED = {}
    SUPPORTED.update(switches.DEVICETYPES)
    SUPPORTED.update(sensors.DEVICETYPES)
    SUPPORTED.update(thermostats.DEVICETYPES)
except Exception as err:
    LOG.critical("devicetypes Exception: %s" % (err,))
    UNSUPPORTED = False
    SUPPORTED = {}
