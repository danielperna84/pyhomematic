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

    def get_state(self, channel=1):
        """ Returns current state of handle """
        return bool(self.getBinaryData("STATE", channel))


class HelperSensorState(HMDevice):
    """Return the state of binary sensors."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"STATE": 'c'})

    def get_state(self, channel=1):
        """ Returns current state of handle """
        return self.getSensorData("STATE", channel)


class HelperActorState(HMDevice):
    """
    Generic HM Switch Object
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"STATE": 'c'})

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


class HelperActorLevel(HMDevice):
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


class HelperActionOnTime(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"ON_TIME": 'c'})

    def set_ontime(self, ontime):
        """Set duration th switch stays on when toggled. """
        try:
            ontime = float(ontime)
        except Exception as err:
            LOG.debug("SwitchPowermeter.set_ontime: Exception %s" % (err,))
            return False

        self.actionNodeData("ON_TIME", ontime)


class HelperActionPress(HMDevice):
    """Helper for simulate press button."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.ACTIONNODE.update({"PRESS_SHORT": 'c',
                                "PRESS_LONG": 'c'})

    def press_long(self, channel=1):
        """Simulat a button press long."""
        self.actionNodeData("PRESS_LONG", 1, channel)

    def press_short(self, channel=1):
        """Simulat a button press short."""
        self.actionNodeData("PRESS_SHORT", 1, channel)
