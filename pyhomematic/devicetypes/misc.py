import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.helper import HelperActionPress, HelperEventRemote, HelperEventPress

LOG = logging.getLogger(__name__)


class HMEvent(HMDevice):
    pass


class HMCCU(HMDevice):
    pass


class RemoteVirtual(HMCCU, HelperActionPress):
    """For virtual remote from ccu/homegear or simple devices with just PRESS_SHORT and PRESS_LONG."""

    @property
    def ELEMENT(self):
        return [c for c in range(1, 51)]


class Remote(HMEvent, HelperEventRemote, HelperActionPress):
    """Remote handle buttons."""

    @property
    def ELEMENT(self):
        if "RC-2" in self.TYPE or "PB-2" in self.TYPE or "WRC2" in self.TYPE:
            return [1, 2]
        if "HM-Dis-WM55" in self.TYPE or "HM-Dis-EP-WM55" in self.TYPE:
            return [1, 2]
        if "HM-RC-Dis-H-x-EU" in self.TYPE:
            return [c for c in range(1, 21)]
        if "Sec3" in self.TYPE or "Key3" in self.TYPE:
            return [1, 2, 3]
        if "RC-4" in self.TYPE or "PB-4" in self.TYPE:
            return [1, 2, 3, 4]
        if "HM-PBI-4-FM" in self.TYPE or "ZEL STG RM FST UP4" in self.TYPE or "263 145" in self.TYPE or "HM-PBI-X" in self.TYPE:
            return [1, 2, 3, 4]
        if "Sec4" in self.TYPE or "Key4" in self.TYPE:
            return [1, 2, 3, 4]
        if "PB-6" in self.TYPE or "WRC6" in self.TYPE:
            return [1, 2, 3, 4, 5, 6]
        if "RC-8" in self.TYPE or "HM-MOD-EM-8" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8]
        if "RC-12" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if "HM-OU-LED16" in self.TYPE:
            return [c for c in range(1, 16)]
        if "RC-19" in self.TYPE or "HM-PB-4Dis-WM" in self.TYPE:
            return [c for c in range(1, 20)]
        if "HMW-IO-4-FM" in self.TYPE:
            return [1, 2, 3, 4]
        if "HMW-IO-12-FM" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if "HmIP-RC8" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8]
        return [1]


class RemotePress(HMEvent, HelperEventPress, HelperActionPress):
    """Remote handle buttons."""

    @property
    def ELEMENT(self):
        return [1, 2, 3]


DEVICETYPES = {
    "HM-RCV-50": RemoteVirtual,
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
    "HM-PB-2-FM": Remote,
    "HM-PB-2-WM": Remote,
    "BC-PB-2-WM": RemotePress,
    "HM-PB-4-WM": Remote,
    "HM-PB-6-WM55": Remote,
    "HM-PB-2-WM55-2": Remote,
    "HM-PB-2-WM55": Remote,
    "HM-PBI-4-FM": Remote,
    "HM-PBI-X": Remote,
    "HM-Dis-WM55": Remote,
    "HM-Dis-EP-WM55": Remote,
    "HM-MOD-EM-8": Remote,
    "RC-H": Remote,
    "BRC-H": Remote,
    "atent": Remote,
    "ZEL STG RM WT 2": Remote,
    "ZEL STG RM HS 4": Remote,
    "ZEL STG RM FST UP4": Remote,
    "263 145": Remote,
    "263 135": Remote,
    "HM-OU-LED16": Remote,
    "HM-PB-4Dis-WM": Remote,
    "HM-PB-4Dis-WM-2": Remote,
    "HMW-IO-4-FM": Remote,
    "HMW-IO-12-FM": Remote,
    "HMIP-WRC2": Remote,
    "HmIP-WRC2": Remote,
    "HmIP-WRC6": Remote,
    "HM-SwI-3-FM": RemotePress,
    "ZEL STG RM FSS UP3": RemotePress,
    "263 144": RemotePress,
    "HM-SwI-X": RemotePress,
    "HMW-RCV-50": RemoteVirtual,
    "HmIP-RC8": Remote,
}
