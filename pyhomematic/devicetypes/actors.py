import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.sensors import HMSensor
from pyhomematic.devicetypes.helper import (
    HelperWorking, HelperActorState, HelperActorLevel, HelperActionOnTime,
    HelperActionPress, HelperEventRemote)

LOG = logging.getLogger(__name__)


class HMActor(HMDevice):
    """
    Generic HM Actor Object
    """
    pass

class Blind(HMActor, HelperActorLevel, HelperWorking):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"STOP": self.ELEMENT})

    def move_up(self, channel=1):
        """Move the shutter up all the way."""
        self.set_level(1.0, channel)

    def move_down(self, channel=1):
        """Move the shutter down all the way."""
        self.set_level(0.0, channel)

    def stop(self, channel=1):
        """Stop moving."""
        self.actionNodeData("STOP", True, channel)


class KeyBlind(HMActor, HelperActorLevel, HelperWorking, HelperActionPress):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"STOP": self.ELEMENT})
        self.EVENTNODE.update({"PRESS_SHORT": self.ELEMENT,
                               "PRESS_LONG_RELEASE": self.ELEMENT})

    @property
    def ELEMENT(self):
        return [1, 2]

    def move_up(self, channel=3):
        """Move the shutter up all the way."""
        self.set_level(1.0, channel)

    def move_down(self, channel=3):
        """Move the shutter down all the way."""
        self.set_level(0.0, channel)

    def stop(self, channel=3):
        """Stop moving."""
        self.actionNodeData("STOP", True, channel)


class Dimmer(HMActor, HelperActorLevel, HelperWorking):
    """
    Dimmer switch that controls level of light brightness.
    """
    @property
    def ELEMENT(self):
        if "Dim2L" in self._TYPE:
            return [1, 2]
        return [1]

    def on(self, channel=1):
        """Turn light to maximum brightness."""
        self.set_level(1.0, channel)

    def off(self, channel=1):
        """Turn light off."""
        self.set_level(0.0, channel)


class KeyDimmer(HMActor, HelperActorLevel, HelperWorking, HelperActionPress):
    """
    Dimmer switch that controls level of light brightness.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.EVENTNODE.update({"PRESS_SHORT": self.ELEMENT,
                               "PRESS_LONG_RELEASE": self.ELEMENT})
    @property
    def ELEMENT(self):
        return [1, 2]

    def on(self, channel=3):
        """Turn light to maximum brightness."""
        self.set_level(1.0, channel)

    def off(self, channel=3):
        """Turn light off."""
        self.set_level(0.0, channel)


class Switch(HMActor, HelperActorState, HelperWorking):
    """
    Switch turning plugged in device on or off.
    """
    @property
    def ELEMENT(self):
        if "LC-Sw2" in self.TYPE:
            return [1, 2]
        elif "LC-Sw4" in self.TYPE:
            return [1, 2, 3, 4]
        elif "Re-8" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8]
        elif "HM-OU-CFM-Pl" in self.TYPE or "HM-OU-CFM-TW" in self.TYPE or "HM-OU-CF-Pl" in self.TYPE:
            return [1, 2]
        elif "HMW-IO-12-Sw14-DR" in self.TYPE:
            return [1, 2, 3, 4, 5, 6]
        elif "HMW-IO-12-Sw7-DR" in self.TYPE:
            return [13, 14, 15, 16, 17, 18, 19]
        return [1]

    def is_on(self, channel=1):
        """ Returns True if switch is on. """
        return self.get_state(channel)

    def is_off(self, channel=1):
        """ Returns True if switch is off. """
        return not self.get_state(channel)

    def on(self, channel=1):
        """Turn switch on."""
        self.set_state(True, channel)

    def off(self, channel=1):
        """Turn switch off."""
        self.set_state(False, channel)


class IOSwitch(HMActor, HelperActorState, HelperWorking, HelperEventRemote):
    """
    Switch turning attached device on or off.
    """

    @property
    def ELEMENT(self):
        if "HMW-IO-12-Sw7-DR" in self.TYPE:
            return [13, 14, 15, 16, 17, 18, 19]
        if "HMW-LC-Sw2-DR" in self.TYPE:
            return [3, 4]
        return [1]

    def is_on(self, channel=1):
        """ Returns True if switch is on. """
        return self.get_state(channel)

    def is_off(self, channel=1):
        """ Returns True if switch is off. """
        return not self.get_state(channel)

    def on(self, channel=1):
        """Turn switch on."""
        self.set_state(True, channel)

    def off(self, channel=1):
        """Turn switch off."""
        self.set_state(False, channel)


class KeyMatic(HMActor, HelperActorState):
    """
    Open or close KeyMatic.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"OPEN": self.ELEMENT})


class IPSwitch(HMActor, HelperActorState, HelperActionOnTime):
    """
    Switch turning attached device on or off.
    """

    @property
    def ELEMENT(self):
        return [3]


class SwitchPowermeter(Switch, HelperActionOnTime, HMSensor):
    """
    Switch turning plugged in device on or off and measuring energy consumption.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"POWER": [2],
                                "CURRENT": [2],
                                "VOLTAGE": [2],
                                "ENERGY_COUNTER": [2]})

    @property
    def ELEMENT(self):
        return [1]


class IPSwitchPowermeter(IPSwitch, HMSensor):
    """
    Switch turning plugged in device on or off and measuring energy consumption.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"POWER": [6],
                                "CURRENT": [6],
                                "VOLTAGE": [6],
                                "FREQUENCY": [6],
                                "ENERGY_COUNTER": [6]})


DEVICETYPES = {
    "HM-LC-Bl1-SM": Blind,
    "HM-LC-Bl1-SM-2": Blind,
    "HM-LC-Bl1-FM": Blind,
    "HM-LC-Bl1-FM-2": Blind,
    "HM-LC-Bl1PBU-FM": Blind,
    "HM-LC-Bl1-PB-FM": Blind,
    "ZEL STG RM FEP 230V": Blind,
    "263 146": Blind,
    "263 147": Blind,
    "HM-LC-BlX": Blind,
    "HM-LC-Dim1L-Pl": Dimmer,
    "HM-LC-Dim1L-Pl-2": Dimmer,
    "HM-LC-Dim1L-Pl-3": Dimmer,
    "HM-LC-Dim1L-CV": Dimmer,
    "HM-LC-Dim1L-CV-2": Dimmer,
    "HM-LC-Dim1T-Pl": Dimmer,
    "HM-LC-Dim1T-Pl-3": Dimmer,
    "HM-LC-Dim1T-CV": Dimmer,
    "HM-LC-Dim1T-CV-2": Dimmer,
    "HM-LC-Dim1T-FM": Dimmer,
    "HM-LC-Dim1T-FM-2": Dimmer,
    "HM-LC-Dim1T-FM-LF": Dimmer,
    "HM-LC-Dim1PWM-CV": Dimmer,
    "HM-LC-Dim1PWM-CV-2": Dimmer,
    "HM-LC-Dim1TPBU-FM": Dimmer,
    "HM-LC-Dim1TPBU-FM-2": Dimmer,
    "HM-LC-Dim2L-CV": Dimmer,
    "HM-LC-Dim2L-SM": Dimmer,
    "HM-LC-Dim2L-SM-2": Dimmer,
    "HM-LC-Dim2T-SM": Dimmer,
    "HM-LC-Dim2T-SM-2": Dimmer,
    "HSS-DX": Dimmer,
    "263 132": Dimmer,
    "263 133": Dimmer,
    "263 134": Dimmer,
    "HM-Dis-TD-T": Switch,
    "HM-OU-CF-Pl": Switch,
    "HM-OU-CM-PCB": Switch,
    "HM-OU-CFM-Pl": Switch,
    "HM-OU-CFM-TW": Switch,
    "HM-LC-Sw1-Pl": Switch,
    "HM-LC-Sw1-Pl-2": Switch,
    "HM-LC-Sw1-Pl-3": Switch,
    "HM-LC-Sw1-Pl-DN-R1": Switch,
    "HM-LC-Sw1-Pl-DN-R2": Switch,
    "HM-LC-Sw1-Pl-DN-R3": Switch,
    "HM-LC-Sw1-Pl-DN-R4": Switch,
    "HM-LC-Sw1-Pl-DN-R5": Switch,
    "HM-LC-Sw1-Pl-CT-R1": Switch,
    "HM-LC-Sw1-Pl-CT-R2": Switch,
    "HM-LC-Sw1-Pl-CT-R3": Switch,
    "HM-LC-Sw1-Pl-CT-R4": Switch,
    "HM-LC-Sw1-Pl-CT-R5": Switch,
    "HM-LC-Sw1-Pl-OM54": Switch,
    "HM-LC-Sw1-DR": Switch,
    "HM-LC-Sw1-SM": Switch,
    "HM-LC-Sw1-SM-2": Switch,
    "HM-LC-Sw1-FM": Switch,
    "HM-LC-Sw1-FM-2": Switch,
    "HM-LC-Sw1-PB-FM": Switch,
    "HM-LC-Sw1-Ba-PCB": Switch,
    "HM-LC-Sw1-SM-ATmega168": Switch,
    "HM-LC-Sw1PBU-FM": Switch,
    "HM-LC-Sw2-SM": Switch,
    "HM-LC-Sw2-FM": Switch,
    "HM-LC-Sw2-FM-2": Switch,
    "HM-LC-Sw2-DR": Switch,
    "HM-LC-Sw2-DR-2": Switch,
    "HM-LC-Sw2-PB-FM": Switch,
    "HM-LC-Sw2PBU-FM": Switch,
    "HM-LC-Sw4-Ba-PCB": Switch,
    "HM-LC-Sw4-SM": Switch,
    "HM-LC-Sw4-SM-2": Switch,
    "HM-LC-Sw4-SM-ATmega168": Switch,
    "HM-LC-Sw4-PCB": Switch,
    "HM-LC-Sw4-PCB-2": Switch,
    "HM-LC-Sw4-WM": Switch,
    "HM-LC-Sw4-WM-2": Switch,
    "HM-LC-Sw4-DR": Switch,
    "HM-LC-Sw4-DR-2": Switch,
    "263 130": Switch,
    "263 131": Switch,
    "ZEL STG RM FZS": Switch,
    "ZEL STG RM FZS-2": Switch,
    "HM-LC-SwX": Switch,
    "HM-MOD-Re-8": Switch,
    "HM-ES-PMSw1-Pl": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R1": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R2": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R3": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R4": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R5": SwitchPowermeter,
    "HM-ES-PMSw1-DR": SwitchPowermeter,
    "HM-ES-PMSw1-SM": SwitchPowermeter,
    "HM-ES-PMSwX": SwitchPowermeter,
    "HMW-IO-12-Sw7-DR": IOSwitch,
    "HMW-LC-Sw2-DR": IOSwitch,
    "HMW-LC-Bl1-DR": KeyBlind,
    "HMW-LC-Bl1-DR-2": KeyBlind,
    "HMW-LC-Dim1L-DR": KeyDimmer,
    "HMIP-PS": IPSwitch,
    "HMIP-PSM": IPSwitchPowermeter,
    "HM-Sec-Key": KeyMatic,
    "HM-Sec-Key-S": KeyMatic,
    "HM-Sec-Key-O": KeyMatic,
    "HM-Sec-Key-Generic": KeyMatic,
}
