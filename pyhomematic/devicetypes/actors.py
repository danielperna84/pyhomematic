import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.sensors import HMSensor
from pyhomematic.devicetypes.misc import HMEvent
from pyhomematic.devicetypes.helper import (
    HelperWorking, HelperActorState, HelperActorLevel, HelperActorBlindTilt, HelperActionOnTime,
    HelperActionPress, HelperEventRemote, HelperWired, HelperRssiPeer, HelperRssiDevice)

LOG = logging.getLogger(__name__)


class HMActor(HMDevice):
    """
    Generic HM Actor Object
    """


class GenericBlind(HMActor, HelperActorLevel):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """

    def move_up(self, channel=None):
        """Move the shutter up all the way."""
        self.set_level(1.0, channel)

    def move_down(self, channel=None):
        """Move the shutter down all the way."""
        self.set_level(0.0, channel)

    def stop(self, channel=None):
        """Stop moving."""
        self.actionNodeData("STOP", True, channel)


class Blind(GenericBlind, HelperWorking, HelperRssiPeer):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"STOP": self.ELEMENT})


class KeyBlind(Blind, HelperActionPress, HelperWired):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"LEVEL": self.ELEMENT})
        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})

    @property
    def ELEMENT(self):
        return [3]


class IPKeyBlind(KeyBlind):
    """
    Blind switch that raises and lowers homematic ip roller shutters or window blinds.
    """

    @property
    def ELEMENT(self):
        return [4]


class IPKeyBlindTilt(IPKeyBlind, HelperActorBlindTilt):

    def close_slats(self, channel=None):
        """Move the shutter up all the way."""
        self.set_cover_tilt_position(0.0, channel)

    def open_slats(self, channel=None):
        """Move the shutter down all the way."""
        self.set_cover_tilt_position(1.0, channel)


class GenericDimmer(HMActor, HelperActorLevel):
    """
    Dimmer switch that controls level of light brightness.
    """

    def on(self, channel=None):
        """Turn light to maximum brightness."""
        self.set_level(1.0, channel)

    def off(self, channel=None):
        """Turn light off."""
        self.set_level(0.0, channel)


class Dimmer(GenericDimmer, HelperWorking):
    """
    Dimmer switch that controls level of light brightness.
    """
    @property
    def ELEMENT(self):
        if "Dim2L" in self._TYPE or "Dim2T" in self._TYPE:
            return [1, 2]
        return [1]


class KeyDimmer(GenericDimmer, HelperWorking, HelperActionPress):
    """
    Dimmer switch that controls level of light brightness.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG_RELEASE": [1, 2]})

    @property
    def ELEMENT(self):
        return [3]


class IPDimmer(GenericDimmer):
    """
    IP Dimmer switch that controls level of light brightness.
    """
    @property
    def ELEMENT(self):
        if "PDT" in self._TYPE:
            return [3]
        return [2]


class IPKeyDimmer(GenericDimmer, HelperWorking, HelperActionPress):
    """
    IP Dimmer with buttons switch that controls level of light brightness.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG_RELEASE": [1, 2]})

    @property
    def ELEMENT(self):
        return [4]


class GenericSwitch(HMActor, HelperActorState):
    """
    Switch turning plugged in device on or off.
    """

    def is_on(self, channel=None):
        """ Returns True if switch is on. """
        return self.get_state(channel)

    def is_off(self, channel=None):
        """ Returns True if switch is off. """
        return not self.get_state(channel)

    def on(self, channel=None):
        """Turn switch on."""
        self.set_state(True, channel)

    def off(self, channel=None):
        """Turn switch off."""
        self.set_state(False, channel)


class Rain(GenericSwitch, HelperWorking):
    """Rain / Heat sensor with heating switch"""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        # init metadata
        self.BINARYNODE.update({"STATE": [1]})

    def is_rain(self, channel=None):
        """ Returns True when raining. """
        return self.get_state(channel)

    @property
    def ELEMENT(self):
        return [2]


class Switch(GenericSwitch, HelperWorking, HelperRssiPeer):
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


class IOSwitch(GenericSwitch, HelperWorking, HelperEventRemote, HelperWired):
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


class HMWIOSwitch(GenericSwitch, HelperWired):
    """
    Wired IO module controlling and sensing attached devices.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        # Output channels (digital)
        self._doc = [1, 2, 3, 4, 5, 6]
        # Output channels (digital/analog)
        self._daoc = [7, 8, 9, 10, 11, 12, 13, 14]
        # Output channels (analog), how do we expose these?
        self._aoc = []
        # Input channels (digital/frequency)
        self._dfic = [15, 16, 17, 18, 19, 20]
        # Input channels (digital/analog)
        self._daic = [21, 22, 23, 24, 25, 26]
        # Input channels (digital)
        self._dic = []
        # Input channels (frequency)
        self._fic = []
        # Input channels (analog)
        self._aic = []

        super().__init__(device_description, proxy, resolveparamsets)
        # Need to know the operational mode to return digital switch channels with ELEMENT-property
        for chan in self._daoc:
            if self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("BEHAVIOUR", None) == 1:
                # We add the digital channels to self._doc
                self._doc.append(chan)
            else:
                # We add the analog channels to self._aoc
                self._aoc.append(chan)

        # We also want to know how the inputs are configured
        for chan in self._dfic:
            if self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("BEHAVIOUR", None) == 1:
                # We add the digital channels to self._dic
                self._dic.append(chan)
            else:
                # We add the frequency channels to self._fic
                self._fic.append(chan)

        for chan in self._daic:
            if self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("BEHAVIOUR", None) == 1:
                # We add the digital channels to self._dic
                self._dic.append(chan)
            else:
                # We add the analog channels to self._aic
                self._aic.append(chan)

        # init metadata
        self.BINARYNODE.update({"STATE": self._dic})
        self.SENSORNODE.update({"FREQUENCY": self._fic,  # mHz, from 0.0 to 350000.0
                                "VALUE": self._aic})  # No specific unit, float from 0.0 to 1000.0

    @property
    def ELEMENT(self):
        return self._doc


class RFSiren(GenericSwitch, HelperWorking, HelperRssiPeer):
    """
    HM-Sec-Sir-WM Siren
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ERROR_SABOTAGE": self.ELEMENT,
                                   "LOWBAT": self.ELEMENT})
        self.SENSORNODE.update({"ARMSTATE": [4]})
        self.WRITENODE.update({"ARMSTATE": [4]})

    @property
    def ELEMENT(self):
        return [1, 2, 3]


class KeyMatic(HMActor, HelperActorState, HelperRssiPeer):
    """
    Lock, Unlock or Open KeyMatic.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"OPEN": self.ELEMENT})
        self.BINARYNODE.update({"STATE_UNCERTAIN": self.ELEMENT})
        self.SENSORNODE.update({"ERROR": self.ELEMENT})

    def is_unlocked(self, channel=None):
        """ Returns True if KeyMatic is unlocked. """
        return self.get_state(channel)

    def is_locked(self, channel=None):
        """ Returns True if KeyMatic is locked. """
        return not self.get_state(channel)

    def unlock(self, channel=None):
        """Unlocks the door lock."""
        return self.set_state(True, channel)

    def lock(self, channel=None):
        """Locks the door lock"""
        return self.set_state(False, channel)

    def open(self):
        """Opens the door.
           Keep in mind that in most cases the door can only be closed physically.
           If the KeyMatic is in locked state it will unlock first.
           After opening the door the state of KeyMatic is unlocked.
        """
        return self.setValue("OPEN", True)

    @property
    def ELEMENT(self):
        return [1]


class IPSwitch(GenericSwitch, HelperActionOnTime):
    """
    Switch turning attached device on or off.
    """

    @property
    def ELEMENT(self):
        if "HmIP-BSM" in self.TYPE:
            return [4]
        elif "HmIP-FSM" in self.TYPE or "HmIP-FSM16" in self.TYPE:
            return [2]
        else:
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
                                "FREQUENCY": [2],
                                "ENERGY_COUNTER": [2]})

    @property
    def ELEMENT(self):
        return [1]


class EcoLogic(Switch, HelperActionOnTime, HelperActionPress, HMSensor):
    """
    Switching device and humidity sensor for automatic watering
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"SENSOR": [3, 4]})
        self.EVENTNODE.update({"PRESS_SHORT": [5, 6, 7, 8, 9]})

    @property
    def ELEMENT(self):
        return [1, 2]


class IPSwitchPowermeter(IPSwitch, HMSensor, HelperRssiDevice):
    """
    Switch turning plugged in device on or off and measuring energy consumption.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        sensorIndex = None
        if "HmIP-FSM" in self.TYPE or "HmIP-FSM16" in self.TYPE:
            sensorIndex = 5
        elif "HMIP-PSM" in self.TYPE or "HmIP-PSM" in self.TYPE or "HmIP-PSM-CH" in self.TYPE:
            sensorIndex = 6
        elif "HmIP-BSM" in self.TYPE:
            sensorIndex = 7

        if sensorIndex is not None:
            self.SENSORNODE.update({"POWER": [sensorIndex],
                                    "CURRENT": [sensorIndex],
                                    "VOLTAGE": [sensorIndex],
                                    "FREQUENCY": [sensorIndex],
                                    "ENERGY_COUNTER": [sensorIndex]})


class IPKeySwitchPowermeter(IPSwitchPowermeter, HMEvent, HelperActionPress):
    """
    Switch turning plugged in device on or off and measuring energy consumption.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})


class IPGarage(GenericSwitch, HMSensor):
    """
    HmIP-MOD-TM Garage actor
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"DOOR_STATE": [1]})

    def move_up(self):
        """Opens the garage"""
        return self.setValue("DOOR_COMMAND", 1, channel=1)

    def stop(self):
        """Stop motion"""
        return self.setValue("DOOR_COMMAND", 2, channel=1)

    def move_down(self):
        """Close the garage"""
        return self.setValue("DOOR_COMMAND", 3, channel=1)

    def vent(self):
        """Go to ventilation position"""
        return self.setValue("DOOR_COMMAND", 4, channel=1)

    @property
    def ELEMENT(self):
        return [2]


class ColorEffectLight(Dimmer):
    """
    Color light with dimmer function and color effects.
    """
    _level_channel = 1
    _color_channel = 2
    _effect_channel = 3
    _light_effect_list = ['Off', 'Slow color change', 'Medium color change', 'Fast color change', 'Campfire',
                          'Waterfall', 'TV simulation']

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"COLOR": [self._color_channel], "PROGRAM": [self._effect_channel]})

    def get_hs_color(self):
        """
        Return the color of the light as HSV color without the "value" component for the brightness.

        Returns (hue, saturation) tuple with values in range of 0-1, representing the H and S component of the
        HSV color system.
        """
        # Get the color from homematic. In general this is just the hue parameter.
        hm_color = self.getCachedOrUpdatedValue("COLOR", channel=self._color_channel)

        if hm_color >= 200:
            # 200 is a special case (white), so we have a saturation of 0.
            # Larger values are undefined. For the sake of robustness we return "white" anyway.
            return 0, 0

        # For all other colors we assume saturation of 1
        return hm_color/200, 1

    def set_hs_color(self, hue: float, saturation: float):
        """
        Set a fixed color and also turn off effects in order to see the color.

        :param hue: Hue component (range 0-1)
        :param saturation: Saturation component (range 0-1). Yields white for values near 0, other values are
            interpreted as 100% saturation.

        The input values are the components of an HSV color without the value/brightness component.
        Example colors:
            * Green: set_hs_color(120/360, 1)
            * Blue: set_hs_color(240/360, 1)
            * Yellow: set_hs_color(60/360, 1)
            * White: set_hs_color(0, 0)
        """
        self.turn_off_effect()

        if saturation < 0.1:  # Special case (white)
            hm_color = 200
        else:
            hm_color = int(round(max(min(hue, 1), 0) * 199))

        self.setValue(key="COLOR", channel=self._color_channel, value=hm_color)

    def get_effect_list(self) -> list:
        """Return the list of supported effects."""
        return self._light_effect_list

    def get_effect(self) -> str:
        """Return the current color change program of the light."""
        effect_value = self.getCachedOrUpdatedValue("PROGRAM", channel=self._effect_channel)

        try:
            return self._light_effect_list[effect_value]
        except IndexError:
            LOG.error("Unexpected color effect returned by CCU")
            return "Unknown"

    def set_effect(self, effect_name: str):
        """Sets the color change program of the light."""
        try:
            effect_index = self._light_effect_list.index(effect_name)
        except ValueError:
            LOG.error("Trying to set unknown light effect")
            return False

        return self.setValue(key="PROGRAM", channel=self._effect_channel, value=effect_index)

    def turn_off_effect(self):
        return self.set_effect(self._light_effect_list[0])


DEVICETYPES = {
    "HM-LC-Bl1-SM": Blind,
    "HM-LC-Bl1-SM-2": Blind,
    "HM-LC-Bl1-FM": Blind,
    "HM-LC-Bl1-FM-2": Blind,
    "HM-LC-Bl1PBU-FM": Blind,
    "HM-LC-Bl1-PB-FM": Blind,
    "HM-LC-Ja1PBU-FM": Blind,
    "ZEL STG RM FEP 230V": Blind,
    "263 146": Blind,
    "263 147": Blind,
    "HM-LC-BlX": Blind,
    "HM-Sec-Win": Blind,
    "HmIP-BROLL": IPKeyBlind,
    "HmIP-FROLL": IPKeyBlind,
    "HmIP-BBL": IPKeyBlindTilt,
    "HM-LC-Dim1L-Pl": Dimmer,
    "HM-LC-Dim1L-Pl-2": Dimmer,
    "HM-LC-Dim1L-Pl-3": Dimmer,
    "HM-LC-Dim1L-CV": Dimmer,
    "HM-LC-Dim1L-CV-2": Dimmer,
    "HM-LC-Dim1T-Pl": Dimmer,
    "HM-LC-Dim1T-Pl-2": Dimmer,
    "HM-LC-Dim1T-Pl-3": Dimmer,
    "HM-LC-Dim1T-CV": Dimmer,
    "HM-LC-Dim1T-CV-2": Dimmer,
    "HM-LC-Dim1T-DR": Dimmer,
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
    "HM-LC-Sw1-PCB": Switch,
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
    "IT-Switch": Switch,
    "REV-Ritter-Switch": Switch,
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
    "HMW-IO-12-Sw14-DR": HMWIOSwitch,
    "HMW-LC-Sw2-DR": IOSwitch,
    "HMW-LC-Bl1-DR": KeyBlind,
    "HMW-LC-Bl1-DR-2": KeyBlind,
    "HMW-LC-Dim1L-DR": KeyDimmer,
    "HMIP-PS": IPSwitch,
    "HmIP-PS": IPSwitch,
    "HmIP-PCBS": IPSwitch,
    "HMIP-PSM": IPSwitchPowermeter,
    "HmIP-PSM": IPSwitchPowermeter,
    "HmIP-PSM-CH": IPSwitchPowermeter,
    "HmIP-FSM": IPSwitchPowermeter,
    "HmIP-FSM16": IPSwitchPowermeter,
    "HmIP-BSM": IPKeySwitchPowermeter,
    "HMIP-BDT": IPKeyDimmer,
    "HmIP-BDT": IPKeyDimmer,
    "HmIP-FDT": IPDimmer,
    "HmIP-PDT": IPDimmer,
    "HM-Sec-Key": KeyMatic,
    "HM-Sec-Key-S": KeyMatic,
    "HM-Sec-Key-O": KeyMatic,
    "HM-Sec-Key-Generic": KeyMatic,
    "HM-Sen-RD-O": Rain,
    "ST6-SH": EcoLogic,
    "HM-Sec-Sir-WM": RFSiren,
    "HmIP-MOD-TM": IPGarage,
    "HM-LC-RGBW-WM": ColorEffectLight,
}
