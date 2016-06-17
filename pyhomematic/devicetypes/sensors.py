import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)


class HMSensor(HMDevice):
    pass


class HMBinarySensor(HMDevice):
    def get_state(self, channel=1):
        """ Returns current state of handle """
        for name in self.BINARYNODE:
            return self.getBinaryData(name, channel)
        return None


class DefaultBinarySensor(HMBinarySensor):
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"STATE": 1})
        self.ATTRIBUTENODE.update({"LOWBAT": None, "ERROR": 1})

    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        return bool(self.getAttributData("ERROR"))

    def low_batt(self):
        """ Returns if the battery is low. """
        return self.getAttributData("LOWBAT")


class ShutterContact(DefaultBinarySensor):
    """
    HM-Sec-SC, HM-Sec-SC-2, ZEL STG RM FFK, HM-Sec-SCo
    Door / Window contact that emits its open/closed state.
    """
    def is_open(self):
        """ Returns if the contact is open. """
        return self.get_state()

    def is_closed(self):
        """ Returns if the contact is closed. """
        return not self.get_state()


class RotaryHandleSensor(DefaultBinarySensor):
    """
    HM-Sec-RHS, ZEL STG RM FDK, HM-Sec-RHS-2, HM-Sec-xx
    Window handle contact
    """
    def is_open(self):
        """ Returns if the handle is open. """
        return self.get_state() == 2

    def is_closed(self):
        """ Returns if the handle is closed. """
        return self.get_state() == 0

    def is_tilted(self):
        """ Returns if the handle is tilted. """
        return self.get_state() == 1


class Remote(HMBinarySensor):
    """
    BRC-H, HM-RC-2-PBU-FM, HM-RC-Dis-H-x-EU, HM-RC-4, HM-RC-4-B, HM-RC-4-2,
    HM-RC-4-3, HM-RC-4-3-D, HM-RC-8, HM-RC-12, HM-RC-12-B, HM-RC-12-SW,
    HM-RC-19, HM-RC-19-B, HM-RC-19-SW, HM-RC-Key3, HM-RC-Key3-B, HM-RC-Key4-2,
    HM-RC-Key4-3, HM-RC-Sec3, HM-RC-Sec3-B, HM-RC-Sec4-2, HM-RC-Sec4-3,
    HM-RC-P1, HM-RC-SB-X, HM-RC-X, HM-PB-2-WM, HM-PB-4-WM, HM-PB-6-WM55
    Remote handle buttons
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        self.BINARYNODE.update({"PRESS_SHORT": 0, "PRESS_LONG": 0})


DEVICETYPES = {
    "HM-Sec-SC": ShutterContact,
    "HM-Sec-SC-2": ShutterContact,
    "HM-Sec-SCo": ShutterContact,
    "ZEL STG RM FFK": ShutterContact,
    "HM-Sec-RHS": RotaryHandleSensor,
    "ZEL STG RM FDK": RotaryHandleSensor,
    "HM-Sec-RHS-2": RotaryHandleSensor,
    "HM-Sec-xx": RotaryHandleSensor,
    "HM-RC-8": Remote,
    "BRC-H": Remote,
    "HM-RC-2-PBU-FM": Remote,
    "HM-RC-Dis-H-x-EU": Remote,
    "HM-RC-4": Remote,
    "HM-RC-4-B": Remote,
    "HM-RC-4-2": Remote,
    "HM-RC-4-3": Remote,
    "HM-RC-4-3-D": Remote,
    "HM-RC-8": Remote,
    "HM-RC-12": Remote,
    "HM-RC-12-B": Remote,
    "HM-RC-12-SW": Remote,
    "HM-RC-19": Remote,
    "HM-RC-19-B": Remote,
    "HM-RC-19-SW": Remote,
    "HM-RC-Key3": Remote,
    "HM-RC-Key3-B": Remote,
    "HM-RC-Key4-2": Remote,
    "HM-RC-Key4-3": Remote,
    "HM-RC-Sec3": Remote,
    "HM-RC-Sec3-B": Remote,
    "HM-RC-Sec4-2": Remote,
    "HM-RC-Sec4-3": Remote,
    "HM-RC-P1": Remote,
    "HM-RC-SB-X": Remote,
    "HM-RC-X": Remote,
    "HM-PB-2-WM": Remote,
    "HM-PB-4-WM": Remote,
    "HM-PB-6-WM55": Remote,
    "RC-H": Remote,
    "atent": Remote,
    "ZEL STG RM HS 4": Remote
}
