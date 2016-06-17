import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.helper import HelperLowBat, HelperSabotage, SimpleBinarySensor

LOG = logging.getLogger(__name__)


class HMSensor(HMDevice):
    pass


class HMBinarySensor(HMDevice):
    pass


class ShutterContact(SimpleBinarySensor):
    """
    HM-Sec-SC, HM-Sec-SC-2, ZEL STG RM FFK, HM-Sec-SCo
    Door / Window contact that emits its open/closed state.
    """
    def is_open(self, channel=1):
        """ Returns if the contact is open. """
        return bool(self.get_state(channel))

    def is_closed(self, channel=1):
        """ Returns if the contact is closed. """
        return not bool(self.get_state(channel))


class RotaryHandleSensor(SimpleBinarySensor):
    """
    HM-Sec-RHS, ZEL STG RM FDK, HM-Sec-RHS-2, HM-Sec-xx
    Window handle contact
    """
    def is_open(self, channel=1):
        """ Returns if the handle is open. """
        return self.get_state(channel) == 2

    def is_closed(self, channel=1):
        """ Returns if the handle is closed. """
        return self.get_state(channel) == 0

    def is_tilted(self, channel=1):
        """ Returns if the handle is tilted. """
        return self.get_state(channel) == 1


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

    @property
    def ELEMENT(self):
        if "RC-2" in self.TYPE or "PB-2" in self.TYPE:
            return 2
        if "Sec3" in self.TYPE or "Key3" in self.TYPE:
            return 3
        if "RC-4" in self.TYPE or "PB-4" in self.TYPE:
            return 4
        if "Sec4" in self.TYPE or "Key4" in self.TYPE:
            return 4
        if "PB-6" in self.TYPE:
            return 6
        if "RC-8" in self.TYPE:
            return 8
        if "RC-12" in self.TYPE:
            return 12
        if "RC-19" in self.TYPE:
            return 19
        return 1


class Motion(HMBinarySensor, HMSensor):
    """
    HM-Sen-MDIR-SM, HM-Sen-MDIR-O, HM-MD, HM-Sen-MDIR-O-2
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION": 0})
        self.SENSORNODE.update({"BRIGHTNESS": 0})

    def is_motion(self, channel=1):
        """ Return is motion is detected """
        return bool(self.getBinaryData("MOTION", channel))

    def get_brightness(self, channel=1):
        """ Return brightness """
        return self.getSensorData("BRIGHTNESS", channel)


class MotionV2(Motion, HelperSabotage):
    """
    HM-Sec-MDIR-3, HM-Sec-MDIR-2, HM-Sec-MDIR, 263 162, HM-Sec-MD
    """
    pass


class RemoteMotion(Remote, Motion):
    """
    HM-Sen-MDIR-WM55
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION": 3,
                                "PRESS_SHORT": 0,
                                "PRESS_LONG": 0})
        self.SENSORNODE.update({"BRIGHTNESS": 3})

    @property
    def ELEMENT(self):
        return 2


DEVICETYPES = {
    "HM-Sec-SC": ShutterContact,
    "HM-Sec-SC-2": ShutterContact,
    "HM-Sec-SCo": ShutterContact,
    "ZEL STG RM FFK": ShutterContact,
    "HM-Sec-RHS": RotaryHandleSensor,
    "ZEL STG RM FDK": RotaryHandleSensor,
    "HM-Sec-RHS-2": RotaryHandleSensor,
    "HM-Sec-xx": RotaryHandleSensor,
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
    "ZEL STG RM HS 4": Remote,
    "HM-Sen-MDIR-WM55": RemoteMotion,
    "HM-Sen-MDIR-SM": Motion,
    "HM-Sen-MDIR-O": Motion,
    "HM-MD": Motion,
    "HM-Sen-MDIR-O-2": Motion,
    "HM-Sec-MDIR-3": MotionV2,
    "HM-Sec-MDIR-2": MotionV2,
    "HM-Sec-MDIR": MotionV2,
    "263 162": MotionV2,
    "HM-Sec-MD": MotionV2
}
