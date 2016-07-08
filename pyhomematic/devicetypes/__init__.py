import logging
from pyhomematic.devicetypes import generic, misc, sensors, actors, thermostats

LOG = logging.getLogger(__name__)

try:
    UNSUPPORTED = generic.HMDevice
    SUPPORTED = {}
    SUPPORTED.update(actors.DEVICETYPES)
    SUPPORTED.update(sensors.DEVICETYPES)
    SUPPORTED.update(thermostats.DEVICETYPES)
    SUPPORTED.update(misc.DEVICETYPES)
except Exception as err:
    LOG.critical("devicetypes Exception: %s" % (err,))
    UNSUPPORTED = False
    SUPPORTED = {}
