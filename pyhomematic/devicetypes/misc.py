import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)


class HMEvent(HMDevice):
    pass


class Remote(HMEvent):
    """
    Remote handle buttons
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS_SHORT": 'c',
                               "PRESS_LONG": 'c',
                               "PRESS_CONT": 'c',
                               "PRESS_LONG_RELEASE": 'c'})
        self.ACTIONNODE.update({"PRESS_SHORT": 'c',
                                "PRESS_LONG": 'c'})

    @property
    def ELEMENT(self):
        if "RC-2" in self.TYPE or "PB-2" in self.TYPE:
            return 2
        if "HM-Dis-WM55" in self.TYPE:
            return 2
        if "Sec3" in self.TYPE or "Key3" in self.TYPE:
            return 3
        if "RC-4" in self.TYPE or "PB-4" in self.TYPE:
            return 4
        if "Sec4" in self.TYPE or "Key4" in self.TYPE:
            return 4
        if "PB-6" in self.TYPE:
            return 6
        if "RC-8" in self.TYPE or "HM-MOD-EM-8" in self.TYPE:
            return 8
        if "RC-12" in self.TYPE:
            return 12
        if "RC-19" in self.TYPE:
            return 19
        return 1

    def press_long(self, channel=1):
        """Simulat a button press long."""
        self.actionNodeData("PRESS_LONG", 1, channel)

    def press_short(self, channel=1):
        """Simulat a button press short."""
        self.actionNodeData("PRESS_SHORT", 1, channel)


DEVICETYPES = {
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
    "HM-PB-2-WM55-2": Remote,
    "HM-PB-2-WM55": Remote,
    "HM-Dis-WM55": Remote,
    "HM-MOD-EM-8": Remote,
    "RC-H": Remote,
    "BRC-H": Remote,
    "atent": Remote,
    "ZEL STG RM WT 2": Remote,
    "ZEL STG RM HS 4": Remote,
    "263 135": Remote
}
