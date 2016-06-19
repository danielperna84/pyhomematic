import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)

class HelperSabotage(HMDevice):
    """This helper adds sabotage detection."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ERROR": 'c'})

    def sabotage(self, channel=1):
        """Returns True if the devicecase has been opened."""
        return bool(self.getAttributeData("ERROR", channel))


class HelperLowBat(HMDevice):
    """This Helper adds easy access to read the LOWBAT state"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOWBAT": 'c'})

    def low_batt(self, channel=1):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOWBAT", channel)


class HelperWorking(HMDevice):
    """This helper provides access to the WORKING state of some devices."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"WORKING": 'c'})

    def is_working(self, channel=1):
        """Return True of False if working or not"""
        return self.getAttributeData("WORKING", channel)


class HelperBatteryState(HMDevice):
    """View the current state of the devices battery if available."""
    def battery_state(self):
        """ Returns the current battery state. """
        return float(self.getAttributeData("BATTERY_STATE"))


class HelperValveState(HMDevice):
    """View the valve state of thermostats and valve controllers."""
    def valve_state(self):
        """ Returns the current valve state. """
        return int(self.getAttributeData("VALVE_STATE"))

class HelperBinaryState(HMDevice):
    """Return the state of binary sensors."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"STATE": 'c'})

    def get_state(self, channel=2):
        """ Returns current state of handle """
        return self.getBinaryData("STATE", channel)


class HelperSwitch(HMDevice):
    """
    Generic HM Switch Object
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"STATE": 'c'})

    def is_on(self, channel=1):
        """ Returns True if switch is on. """
        return self.get_state(channel)

    def is_off(self, channel=1):
        """ Returns True if switch is off. """
        return not self.get_state(channel)

    def get_state(self, channel=1):
        """ Returns if switch is 'on' or 'off'. """
        return bool(self.getWriteData("STATE", channel))

    def set_state(self, onoff, channel=1):
        """Turn switch on/off"""
        try:
            onoff = bool(onoff)
        except Exception as err:
            LOG.debug("HelperSwitch.set_state: Exception %s" % (err,))
            return False

        self.writeNodeData("STATE", onoff, channel)

    def on(self, channel=1):
        """Turn switch on."""
        self.set_state(True, channel)

    def off(self, channel=1):
        """Turn switch off."""
        self.set_state(False, channel)


class HelperLevel(HMDevice):
    """
    Generic level functions
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"LEVEL": 'c'})

    def get_level(self, channel=1):
        """Return current level. Return value is float() from 0.0 to 1.0."""
        return self.getWriteData("LEVEL", channel)

    def set_level(self, position, channel=1):
        """Seek a specific value by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("HelperLevel.set_level: Exception %s" % (err,))
            return False

        self.writeNodeData("LEVEL", position, channel)
