import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)

class HelperSabotage(HMDevice):
    """This helper adds sabotage detection."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ERROR": self.ELEMENT})

    def sabotage(self, channel=None):
        """Returns True if the devicecase has been opened."""
        return bool(self.getAttributeData("ERROR", channel))

class HelperSabotageIP(HMDevice):
    """This helper adds sabotage detection."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"SABOTAGE": [0]})

    # pylint: disable=unused-argument
    def sabotage(self, channel=None):
        """Returns True if the devicecase has been opened."""
        return bool(self.getAttributeData("SABOTAGE", 0))

class HelperLowBat(HMDevice):
    """This Helper adds easy access to read the LOWBAT state"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOWBAT": [0]})

    def low_batt(self, channel=None):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOWBAT", channel)

class HelperLowBatIP(HMDevice):
    """This Helper adds easy access to read the LOWBAT state"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOW_BAT": [0]})

    # pylint: disable=unused-argument
    def low_batt(self, channel=None):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOW_BAT", 0)


class HelperOperatingVoltageIP(HMDevice):
    """This Helper adds easy access to read the OPERATING_VOLTAGE state"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"OPERATING_VOLTAGE": [0]})

    # pylint: disable=unused-argument
    def operation_voltage(self, channel=None):
        """ Returns the operating voltage. """
        return float(self.getAttributeData("OPERATING_VOLTAGE", 0))


class HelperWorking(HMDevice):
    """This helper provides access to the WORKING state of some devices."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"WORKING": self.ELEMENT})

    def is_working(self, channel=None):
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
        self.BINARYNODE.update({"STATE": self.ELEMENT})

    def get_state(self, channel=None):
        """ Returns current state of handle """
        return bool(self.getBinaryData("STATE", channel))


class HelperSensorState(HMDevice):
    """Return the state of binary sensors."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"STATE": self.ELEMENT})

    def get_state(self, channel=None):
        """ Returns current state of handle """
        return self.getSensorData("STATE", channel)


class HelperActorState(HMDevice):
    """Return the binary state of an actor."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"STATE": self.ELEMENT})

    def get_state(self, channel=None):
        """ Returns if state is 'on' or 'off'. """
        return bool(self.getWriteData("STATE", channel))

    def set_state(self, onoff, channel=None):
        """Turn state on/off"""
        try:
            onoff = bool(onoff)
        except Exception as err:
            LOG.debug("HelperActorState.set_state: Exception %s" % (err,))
            return False

        self.writeNodeData("STATE", onoff, channel)


class HelperActorLevel(HMDevice):
    """
    Generic level functions
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"LEVEL": self.ELEMENT})

    def get_level(self, channel=None):
        """Return current level. Return value is float() from 0.0 to 1.0."""
        return self.getWriteData("LEVEL", channel)

    def set_level(self, position, channel=None):
        """Seek a specific value by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("HelperLevel.set_level: Exception %s" % (err,))
            return False

        self.writeNodeData("LEVEL", position, channel)


class HelperInhibit(HMDevice):
    """
    Generic inhibit functions
    Inhibit causes an actor to be in locked state, refusing to accept commands except from CCU or API
    This is only supported for HomeMatic components NOT for HomeMatic IP.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"INHIBIT": self.ELEMENT})

    def get_inhibit(self, channel=None):
        """Return current inhibit status. Return value is 'on' or 'off'."""
        return self.getWriteData("INHIBIT", channel)

    def set_inhibit(self, inhibit, channel=None):
        """Turn inhibit 'on' or 'off'."""
        try:
            inhibit = bool(inhibit)
        except Exception as err:
            LOG.debug("HelperInhibit.set_inhibit: Exception %s" % (err,))
            return False
        self.writeNodeData("INHIBIT", inhibit, channel)


class HelperActorBlindTilt(HMDevice):
    """
    Generic shutter level functions
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"LEVEL_2": self.ELEMENT,
                               "LEVEL": self.ELEMENT})

    def get_cover_tilt_position(self, channel=None):
        """Return current level. Return value is float() from 0.0 to 1.0."""
        return self.getWriteData("LEVEL_2", channel)

    def set_cover_tilt_position(self, position, channel=None):
        """Seek a specific value by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("HelperActorBlindTilt.set_level_2: Exception %s" % (err,))
            return False

        level = self.getWriteData("LEVEL", channel)

        self.writeNodeData("LEVEL_2", position, channel)

        # set level after level_2 to have level_2 updated
        self.writeNodeData("LEVEL", level, channel)


class HelperActionOnTime(HMDevice):
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"ON_TIME": self.ELEMENT})

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

        self.ACTIONNODE.update({"PRESS_SHORT": self.ELEMENT,
                                "PRESS_LONG": self.ELEMENT})

    def press_long(self, channel=None):
        """Simulat a button press long."""
        self.actionNodeData("PRESS_LONG", 1, channel)

    def press_short(self, channel=None):
        """Simulat a button press short."""
        self.actionNodeData("PRESS_SHORT", 1, channel)


class HelperEventPress(HMDevice):
    """Remote handle buttons."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS": self.ELEMENT})


class HelperEventRemote(HMDevice):
    """Remote handle buttons."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS_SHORT": self.ELEMENT,
                               "PRESS_LONG": self.ELEMENT,
                               "PRESS_CONT": self.ELEMENT,
                               "PRESS_LONG_RELEASE": self.ELEMENT})

class HelperWired(HMDevice):
    """Remove the RSSI-related attributes"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self.ATTRIBUTENODE.pop("RSSI_PEER", None)
        self.ATTRIBUTENODE.pop("RSSI_DEVICE", None)


class HelperRssiDevice(HMDevice):
    """Used for devices which report their RSSI value through RSSI_DEVICE"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self.ATTRIBUTENODE["RSSI_DEVICE"] = [0]

    def get_rssi(self, channel=0):
        return self.getAttributeData("RSSI_DEVICE", channel)


class HelperRssiPeer(HMDevice):
    """Used for devices which report their RSSI value through RSSI_PEER"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self.ATTRIBUTENODE["RSSI_PEER"] = [0]

    def get_rssi(self, channel=0):
        return self.getAttributeData("RSSI_PEER", channel)


class HelperDeviceTemperature(HMDevice):
    """Used for devices that report their actual device temperature values (such as the HmIP Wired devices)"""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self.ATTRIBUTENODE["ACTUAL_TEMPERATURE"] = [0]

    def get_device_temperature(self, channel=0):
        return self.getAttributeData("ACTUAL_TEMPERATURE", channel)
