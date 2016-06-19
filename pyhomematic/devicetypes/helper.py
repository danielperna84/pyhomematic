from pyhomematic.devicetypes.generic import HMDevice


class HelperSabotage(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ERROR": 'c'})

    def sabotage(self, channel=1):
        """ Returns if the devicecase has been opened. """
        return bool(self.getAttributeData("ERROR", channel))


class HelperLowBat(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOWBAT": 'c'})

    def low_batt(self, channel=1):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOWBAT", channel)


class HelperWorking(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"WORKING": 'c'})

    def is_working(self, channel=1):
        """Return True of False if working or not"""
        return self.getAttributeData("WORKING", channel)


class HelperBatteryState(HMDevice):
    """
    """
    @property
    def battery_state(self):
        """ Returns the current battery state. """
        return self.getAttributeData("BATTERY_STATE")


class HelperValveState(HMDevice):
    """
    """
    @property
    def valve_state(self):
        """ Returns the current valve state. """
        return self.getAttributeData("VALVE_STATE")

class HelperBinaryState(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"STATE": 'c'})

    def get_state(self, channel=1):
        """ Returns current state of handle """
        return self.getBinaryData("STATE", channel)
