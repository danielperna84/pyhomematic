import logging
from pyhomematic.devicetypes import generic, sensors, actors, thermostats
from pyhomematic.devicetypes.actors import HMSwitch, HMDimmer
from pyhomematic.devicetypes.sensors import HMSensor, HMBinarySensor
from pyhomematic.devicetypes.thermostats import HMThermostat

LOG = logging.getLogger(__name__)

try:
    UNSUPPORTED = generic.HMDevice
    SUPPORTED = {}
    SUPPORTED.update(actors.DEVICETYPES)
    SUPPORTED.update(sensors.DEVICETYPES)
    SUPPORTED.update(thermostats.DEVICETYPES)
except Exception as err:
    LOG.critical("devicetypes Exception: %s" % (err,))
    UNSUPPORTED = False
    SUPPORTED = {}
