from pyhomematic.devicetypes.generic import HMDevice


class HelperSabotage(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ERROR": 0})

    def sabotage(self, channel=1):
        """ Returns if the devicecase has been opened. """
        return bool(self.getAttributeData("ERROR", channel))


class HelperLowBat(HMDevice):
    """
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOWBAT": None})

    def low_batt(self, channel=1):
        """ Returns if the battery is low. """
        return selfgetAttributeDataa("LOWBAT", channel)


class SimpleBinarySensor(HelperSabotage, HelperLowBat):
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"STATE": 1})

    def get_state(self, channel=1):
        """ Returns current state of handle """
        return self.getBinaryData("STATE", channel)
