import logging
from . import generic
from . import sensors
from . import thermostats
from . import switches


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
