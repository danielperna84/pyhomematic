
import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.sensors import HMSensor
from pyhomematic.devicetypes.misc import HMEvent
from pyhomematic.devicetypes.helper import (
    HelperWorking, HelperActorState, HelperActorLevel, HelperActorBlindTilt, HelperActionOnTime,
    HelperActionPress, HelperEventRemote, HelperWired, HelperRssiPeer, HelperRssiDevice, HelperDeviceTemperature,
    HelperInhibit, HelperLowBatIP)

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


class Blind(GenericBlind, HelperInhibit, HelperWorking, HelperRssiPeer):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"STOP": self.ELEMENT})


class IPBlind(GenericBlind, HelperRssiPeer):
    """
    Blind switch that raises and lowers roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"ACTIVITY_STATE": self.ELEMENT,
                                   "LEVEL_STATUS": self.ELEMENT,
                                   "SECTION": self.ELEMENT})
        self.ACTIONNODE.update({"STOP": self.ELEMENT})
        self.SENSORNODE.update({"LEVEL": [3]})
        self.WRITENODE.update({"LEVEL": self.ELEMENT})


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


class IPKeyBlind(IPBlind, HelperActionPress):
    """
    Blind switch that raises and lowers homematic ip roller shutters or window blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})

    @property
    def ELEMENT(self):
        return [4]


class IPKeyBlindMulti(KeyBlind):
    """
    Multi-blind actor HmIP-DRBLI4
    """

    @property
    def ELEMENT(self):
        return [10, 14, 18, 22]


class IPKeyBlindTilt(IPKeyBlind, HelperActorBlindTilt):
    """
    Blind switch that raises, lowers and adjusts the slat position of shutters or blinds.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"LEVEL_2": [3]})

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


class Dimmer(GenericDimmer, HelperInhibit, HelperWorking):
    """
    Dimmer switch that controls level of light brightness.
    """
    @property
    def ELEMENT(self):
        if "Dim2L" in self._TYPE or "Dim2T" in self._TYPE  or self._TYPE == "HM-DW-WM":
            return [1, 2]
        return [1]


class KeyDimmer(GenericDimmer, HelperInhibit, HelperWorking, HelperActionPress):
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


class IPKeyDimmer(GenericDimmer, HelperActionPress):
    """
    IP Dimmer with buttons switch that controls level of light brightness.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        channels = []
        if "HMIP-DRDI3" in self.TYPE.upper():
            channels = [1, 2, 3]
        else:
            channels = [1, 2]

        # init metadata
        self.EVENTNODE.update({"PRESS_SHORT": channels,
                               "PRESS_LONG": channels})

    @property
    def ELEMENT(self):
        if "HMIP-DRDI3" in self.TYPE.upper():
            return [5, 9, 13]
        else:
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


class Rain(GenericSwitch, HelperInhibit, HelperWorking):
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


class Switch(GenericSwitch, HelperInhibit, HelperWorking, HelperRssiPeer):
    """
    Switch turning plugged in device on or off.
    """
    @property
    def ELEMENT(self):
        if "LC-Sw2" in self.TYPE or "Sec-SFA-SM" in self.TYPE:
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

class IOSwitchWireless(GenericSwitch, HelperInhibit, HelperWorking, HelperEventRemote, HelperRssiPeer):
    """
    Switch turning attached device on or off. Can controll relais and buttons independently.
    """
    @property
    def ELEMENT(self):
        return [1, 2]


class IOSwitchNoInhibit(GenericSwitch, HelperWorking, HelperEventRemote, HelperWired):
    """
    Switch turning attached device on or off and not having a inhibit function.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        self._doc = []
        super().__init__(device_description, proxy, resolveparamsets)
        if "HMW-IO-12-FM" in self.TYPE:
            for chan in range(1, 13):
                if self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("BEHAVIOUR", None) == 1:
                    self._doc.append(chan)

    @property
    def ELEMENT(self):
        if "HMW-IO-12-FM" in self.TYPE:
            return self._doc
        return [1]


class IOSwitch(GenericSwitch, HelperInhibit, HelperWorking, HelperEventRemote, HelperWired):
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


class IPWSwitch(GenericSwitch, HelperDeviceTemperature, HelperWired):
    """
    IP-Wired Switch units turning attached device on or off.
    """
    @property
    def ELEMENT(self):
        if "HmIPW-DRS4" in self.TYPE:
            # Address correct switching channels for each relais
            return [2, 6, 10, 14]
        elif "HmIPW-DRS8" in self.TYPE:
            # Address correct switching channels for each relais
            return [2, 6, 10, 14, 18, 22, 26, 30]
        return [1]


class IPWDimmer(GenericDimmer, HelperDeviceTemperature, HelperWired):
    """
    IP-Wired Dimmer switch that controls level of light brightness.
    """
    @property
    def ELEMENT(self):
        if "HmIPW-DRD3" in self._TYPE:
            # Address correct switching channels for each relais
            return [2, 6, 10]
        return [1]

class IPWKeyBlindMulti(KeyBlind, HelperActorBlindTilt,HelperDeviceTemperature, HelperWired):
    """
    Multi-blind actor HmIPW-DRBL4
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self._shutter_channels = []
        self._blind_channels = []

        # Get Operation Mode for Input Channels
        for chan in self.ELEMENT:
            address_channel = "%s:%i" % (self._ADDRESS, chan -1)
            try:
                channel_paramset = self._proxy.getParamset(address_channel, "MASTER", 0)
                channel_operation_mode = channel_paramset.get("CHANNEL_OPERATION_MODE") if "CHANNEL_OPERATION_MODE" in channel_paramset else 1
                if channel_operation_mode == 0:
                    self._blind_channels.append(chan)
                    self.WRITENODE.pop("LEVEL_2", None)
                else:
                    self._shutter_channels.append(chan)
            except Exception as err:
                LOG.error("IPWKeyBlindMulti: Failure to determine channel mode of IPWKeyBlindMulti %s %s", address_channel, err)

        # init metadata
        self.ATTRIBUTENODE.update({"ACTIVITY_STATE": self.ELEMENT,
                                   "LEVEL_STATUS": self.ELEMENT,
                                   "SECTION": self.ELEMENT})
        self.ACTIONNODE.update({"STOP": self.ELEMENT})
        self.WRITENODE.update({"LEVEL": self.ELEMENT})

        if len(self._shutter_channels) > 0:
            self.WRITENODE.update({"LEVEL_2": self._shutter_channels})
            self.SENSORNODE.update({"LEVEL_2": self._shutter_channels})

    def close_slats(self, channel=None):
        """Move the shutter up all the way."""
        self.set_cover_tilt_position(0.0, channel)

    def open_slats(self, channel=None):
        """Move the shutter down all the way."""
        self.set_cover_tilt_position(1.0, channel)

    @property
    def ELEMENT(self):
        return [2, 6, 10, 14]

class IPWInputDevice(HMEvent, HelperDeviceTemperature, HelperWired):
    """
    IP-Wired component to support long / short press events and state report (e.g. if window contact or on/off switch)
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self._hmipw_keypress_event_channels = []
        self._hmipw_binarysensor_channels = []

        for chan in self.ELEMENT:
            address_channel = "%s:%i" % (self._ADDRESS, chan)
            try:
                channel_paramset = self._proxy.getParamset(address_channel, "MASTER", 0)
                channel_operation_mode = channel_paramset.get("CHANNEL_OPERATION_MODE") if "CHANNEL_OPERATION_MODE" in channel_paramset else 1

                if channel_operation_mode == 1:
                    self._hmipw_keypress_event_channels.append(chan)
                elif channel_operation_mode in [2, 3]:
                    self._hmipw_binarysensor_channels.append(chan)
            except Exception as err:
                LOG.error("IPWInputDevice: Failure to determine input channel operations mode of HmIPW input device %s: %s", address_channel, err)

        self.EVENTNODE.update({"PRESS_SHORT": self._hmipw_keypress_event_channels,
                               "PRESS_LONG": self._hmipw_keypress_event_channels})
        self.BINARYNODE.update({"STATE": self._hmipw_binarysensor_channels})

    @property
    def ELEMENT(self):
        """ General channel definition """
        if "HmIPW-DRI16" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        elif "HmIPW-DRI32" in self.TYPE:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        return [1]


class IPWIODevice(HMEvent, GenericSwitch, HelperWired):
    """
    IP-Wired I/O component to support long / short press events and state report (e.g. if window contact or on/off switch)
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)
        self._hmipw_keypress_event_channels = []
        self._hmipw_binarysensor_channels = []
        self._ic = [1]

        # Set Input Channels depending on Device
        if "HmIPW-FIO6" in self.TYPE:
            self._ic = [1, 2, 3, 4, 5, 6]

        # Get Operation Mode for Input Channels
        for chan in self._ic:
            try:
                if self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("CHANNEL_OPERATION_MODE", None) == 1:
                    self._hmipw_keypress_event_channels.append(chan)
                else:
                    self._hmipw_binarysensor_channels.append(chan)
            except Exception as err:
                LOG.error("IPWIODevice: Failure to determine input channel operations mode of HmIPW input device %s:%i %s", self._ADDRESS, chan, err)

        self.ACTIONNODE.update({"PRESS_SHORT": self._hmipw_keypress_event_channels,
                                "PRESS_LONG": self._hmipw_keypress_event_channels})
        self.BINARYNODE.update({"STATE": self._hmipw_binarysensor_channels})

    @property
    def ELEMENT(self):
        """ General output channel definition """
        if "HmIPW-FIO6" in self.TYPE:
            return [8, 12, 16, 20, 24, 28]
        return [1]


class RFSiren(GenericSwitch, HelperInhibit, HelperWorking, HelperRssiPeer):
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


class KeyMatic(HMActor, HelperInhibit, HelperActorState, HelperRssiPeer):
    """
    Lock, Unlock or Open KeyMatic.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ACTIONNODE.update({"OPEN": self.ELEMENT})
        self.ATTRIBUTENODE.update({"STATE_UNCERTAIN": self.ELEMENT,
                                   "ERROR": self.ELEMENT,
                                   "LOWBAT": self.ELEMENT})

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
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        channels = []
        if "HMIP-PS" in self.TYPE.upper() or "HmIP-PCBS" in self.TYPE or "HmIP-DRSI1" in self.TYPE or "HmIP-FSI16" in self.TYPE:
            channels = [1]
        elif "HmIP-MOD-OC8" in self.TYPE:
            channels = [1,2,3,4,5,6,7,8]
        elif "HmIP-DRSI4" in self.TYPE:
            channels = [1,2,3,4]

        if channels:
            self.EVENTNODE.update({"PRESS_SHORT": channels,
                                   "PRESS_LONG": channels})

    @property
    def ELEMENT(self):
        if "HmIP-BSM" in self.TYPE:
            return [4]
        elif "HmIP-PCBS2" in self.TYPE:
            return [4, 8]
        elif "HmIP-FSM" in self.TYPE or "HmIP-FSM16" in self.TYPE:
            return [2]
        elif "HmIP-MOD-OC8" in self.TYPE:
            return [10, 14, 18, 22, 26, 30, 34, 38]
        elif "HmIP-DRSI4" in self.TYPE:
            return [6, 10, 14, 18]
        else:
            return [3]


class IPSwitchBattery(GenericSwitch, HelperActionOnTime, HelperLowBatIP):
    """
    Battery powered switch turning attached device on or off.
    """
    @property
    def ELEMENT(self):
        return [3]


class IPKeySwitch(IPSwitch, HMEvent, HelperActionPress):
    """
    Switch turning plugged in device on or off and measuring energy consumption.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})

    @property
    def ELEMENT(self):
        return [4]


class IPKeySwitchLevel(GenericDimmer, GenericSwitch, HMEvent, HelperActionPress, HelperActorLevel):
    """
    Switch with two independent controllable LEDs, turning plugged in device on or off.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.WRITENODE.update({"STATE": [4],
                               "COLOR": [8, 12],
                               "LEVEL": [8, 12]})
        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})

    def on(self, channel=None):
        """Turn light/switch on."""
        if channel in self.WRITENODE["LEVEL"]:
            self.set_level(1.0, channel)
        else:
            self.set_state(True, channel)

    def off(self, channel=None):
        """Turn light/switch off."""
        if channel in self.WRITENODE["LEVEL"]:
            self.set_level(0.0, channel)
        else:
            self.set_state(False, channel)

    def get_hs_color(self, channel=None):
        """
        Return the color of the light as HSV color without the "value" component for the brightness.

        Returns (hue, saturation) tuple with values in range of 0-1, representing the H and S component of the
        HSV color system.
        """

        # Get the color from homematic. This is one of the predefined colors, that need to be converted to h/s value
        hm_color = self.getCachedOrUpdatedValue("COLOR", channel)

        if hm_color == 7: #WHITE
            return 0, 0
        elif hm_color == 6: #YELLOW
            return 60/360, 1
        elif hm_color == 2: #GREEN
            return 120/360, 1
        elif hm_color == 3: #TURQUOISE / CYAN
            return 180/360, 1
        elif hm_color == 1: #BLUE
            return 240/360, 1
        elif hm_color == 5: #PURPLE
            return 300/360, 1
        elif hm_color == 4: #RED
            return 0, 1
        else:
            return 1, 1  #No way to specify "black", so just pick a different shade of red

    def set_hs_color(self, hue: float, saturation: float, channel=None):
        """
        Set a fixed color.

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

        hue = hue * 360
        if saturation < 0.1:  # Special case (white)
            hm_color = 'WHITE'
        elif hue in range(30, 89):
            hm_color = 'YELLOW'
        elif hue in range(90, 149):
            hm_color = 'GREEN'
        elif hue in range(150, 209):
            hm_color = 'TURQUOISE' # actually cyan
        elif hue in range(210, 269):
            hm_color = 'BLUE'
        elif hue in range(270, 329):
            hm_color = 'PURPLE' # actually magenta
        else:
            hm_color = 'RED'

        self.setValue(key="COLOR", value=hm_color, channel=channel)


    @property
    def ELEMENT(self):
        return [4, 8, 12]


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

        self.EVENTNODE.update({"PRESS_SHORT": [1, 2],
                               "PRESS_LONG": [1, 2]})

        # init metadata
        sensorIndex = None
        if "HmIP-FSM" in self.TYPE or "HmIP-FSM16" in self.TYPE:
            sensorIndex = 5
        elif "HMIP-PSM" in self.TYPE or "HmIP-PSM" in self.TYPE or "HmIP-USBSM" in self.TYPE or "HmIP-PSM-CH" in self.TYPE:
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


class IPGarage(GenericSwitch, GenericBlind, HMSensor):
    """
    HmIP-MOD-HO and HmIP-MOD-TM Garage actor
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"DOOR_STATE": [1]})

    def is_closed(self, state):
        """Returns whether the door is closed"""
        # States:
        # 0: closed
        # 1: open
        # 2: ventilation
        # 3: unknown
        if state in [2, 3]:
            return None
        return state == 0

    def move_up(self, channel=1):
        """Opens the garage"""
        # channel needs to be hardcoded to "1"; home assistant somehow calls the cover entity with channel=2
        # and then the command does not work.
        return self.setValue("DOOR_COMMAND", 1, channel=1)

    def stop(self, channel=1):
        """Stop motion"""
        # channel needs to be hardcoded to "1"; home assistant somehow calls the cover entity with channel=2
        # and then the command does not work.
        return self.setValue("DOOR_COMMAND", 2, channel=1)

    def move_down(self, channel=1):
        """Close the garage"""
        # channel needs to be hardcoded to "1"; home assistant somehow calls the cover entity with channel=2
        # and then the command does not work.
        return self.setValue("DOOR_COMMAND", 3, channel=1)

    def vent(self):
        """Go to ventilation position"""
        return self.setValue("DOOR_COMMAND", 4, channel=1)

    @property
    def ELEMENT(self):
        return [2]


class IPGarageSwitch(GenericSwitch, HelperEventRemote, HMSensor):
    """
    HmIP-WGC Garage Actor
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "OPERATING_VOLTAGE": [0],
                                   "RSSI_DEVICE": [0],
                                   "RSSI_PEER": [0]})

    @property
    def ELEMENT(self):
        return [3]


class IPMultiIO(IPSwitch):
    """
    HmIP-MIOB Multi IO Box
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"CHANGE_OVER": [9, 10],
                                "EXTERNAL_CLOCK": [9, 10],
                                "HUMIDITY_LIMITER": [9, 10],
                                "STATE": [9, 10],
                                "TACTILE_SWITCH": [9, 10],
                                "TEMPERATURE_LIMITER": [9, 10]})
        self.SENSORNODE.update({"LEVEL": [11]})

    @property
    def ELEMENT(self):
        return [2, 3, 4, 6, 7, 8]


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

    # pylint: disable=unused-argument
    def get_hs_color(self, channel=None):
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

    # pylint: disable=unused-argument
    def set_hs_color(self, hue: float, saturation: float, channel=None):
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

class ColdWarmDimmer(Dimmer):
    """
    Dimmer with controls for Cold and Warm LEDs.
    """
    _level_channel = 1
    _temp_channel = 2

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.WRITENODE.update({"LEVEL": [self._level_channel, self._temp_channel]})

    # pylint: disable=unused-argument
    def get_color_temp(self, channel=None):
        """
        Return the color temperature.

        Returns the color temperature with 0 being the warmest and 1 the coldest value
        """
        return self.getCachedOrUpdatedValue("LEVEL", channel=self._temp_channel)

    # pylint: disable=unused-argument
    def set_color_temp(self, color_temp: float, channel=None):
        """
        Set the color temperature.

        :param color_temp: Color temperature (range 0:warmest - 1:coldest)
        """
        # Ensure color_temp is within range
        color_temp = max(0.0, color_temp)
        color_temp = min(1.0, color_temp)

        return self.setValue(key="LEVEL", channel=self._temp_channel, value=color_temp)


class IPMultiIOPCB(GenericSwitch, HelperRssiDevice, HelperRssiPeer):
    """HmIP-MIO16-PCB"""

    def __init__(self, device_description, proxy, resolveparamsets=False):

        # Input channels (analog inputs 0-12V)
        self._aic = [1, 4, 7, 10]
        # Input channels (digital low active inputs)
        self._dic = [13, 14, 15, 16]
        # Output channels
        # CH18, CH22, CH26, CH30: relay outputs (24 V/0,5 A)
        # CH34, CH38, CH42, CH46: open collector outputs (30 V/0,2 A)
        self._doc = [18, 22, 26, 30, 34, 38, 42, 46]

        super().__init__(device_description, proxy, resolveparamsets)

        self._keypress_event_channels = []
        self._binarysensor_channels = []
        self._channel_operation_mode = 0

        # Get Operation Mode for Input Channels
        for chan in self._dic:
            try:
                self._channel_operation_mode = self._proxy.getParamset("%s:%i" % (self._ADDRESS, chan), "MASTER").get("CHANNEL_OPERATION_MODE", None)

                if self._channel_operation_mode == 1:
                    self._keypress_event_channels.append(chan)
                elif self._channel_operation_mode != 0:
                    self._binarysensor_channels.append(chan)
            except Exception as err:
                LOG.error("IPMultiIOPCB: Failure to determine input channel operations mode of IPMultiIOPCB %s:%i %s", self._ADDRESS, chan, err)

        self.BINARYNODE.update({"STATE": self._binarysensor_channels})
        self.SENSORNODE.update({"VOLTAGE": self._aic})
        # button events not successfully implemented yet (SHORT_PRESS, LOMG_PRESS)

    def get_voltage(self, channel=None):
        """Return analog input in V"""
        return float(self.getSensorData("VOLTAGE", channel))

    @property
    def ELEMENT(self):
        return self._doc

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
    "HmIP-FBL": IPKeyBlindTilt,
    "HmIP-DRBLI4": IPKeyBlindMulti,
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
    "HM-Sec-SFA-SM": Switch,
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
    "HMW-IO-12-FM": IOSwitchNoInhibit,
    "HMW-LC-Sw2-DR": IOSwitch,
    "HB-LC-Sw2PBU-FM": IOSwitchWireless,
    "HMW-LC-Bl1-DR": KeyBlind,
    "HMW-LC-Bl1-DR-2": KeyBlind,
    "HMW-LC-Dim1L-DR": KeyDimmer,
    "HmIPW-DRS4": IPWSwitch,
    "HmIPW-DRS8": IPWSwitch,
    "HmIPW-DRI32": IPWInputDevice,
    "HmIPW-DRI16": IPWInputDevice,
    "HmIPW-FIO6": IPWIODevice,
    "HmIPW-DRD3": IPWDimmer,
    "HmIPW-DRBL4": IPWKeyBlindMulti,
    "HMIP-PS": IPSwitch,
    "HmIP-PS": IPSwitch,
    "HmIP-PS-CH": IPSwitch,
    "HmIP-PS-PE": IPSwitch,
    "HmIP-PS-UK": IPSwitch,
    "HmIP-PCBS": IPSwitch,
    "HmIP-PCBS2": IPSwitch,
    "HmIP-PCBS-BAT": IPSwitchBattery,
    "HmIP-PMFS": IPSwitch,
    "HmIP-MOD-OC8": IPSwitch,
    "HmIP-DRSI1": IPSwitch,
    "HmIP-DRSI4": IPSwitch,
    "HmIP-BSL": IPKeySwitchLevel,
    "HmIP-USBSM": IPSwitchPowermeter,
    "HMIP-PSM": IPSwitchPowermeter,
    "HmIP-PSM": IPSwitchPowermeter,
    "HmIP-PSM-CH": IPSwitchPowermeter,
    "HmIP-PSM-IT": IPSwitchPowermeter,
    "HmIP-PSM-PE": IPSwitchPowermeter,
    "HmIP-PSM-UK": IPSwitchPowermeter,
    "HmIP-FSI16": IPSwitch,
    "HmIP-FSM": IPSwitchPowermeter,
    "HmIP-FSM16": IPSwitchPowermeter,
    "HmIP-BSM": IPKeySwitchPowermeter,
    "HMIP-BDT": IPKeyDimmer,
    "HmIP-BDT": IPKeyDimmer,
    "HmIP-DRDI3": IPKeyDimmer,
    "HmIP-FDT": IPDimmer,
    "HmIP-PDT": IPDimmer,
    "HmIP-PDT-UK": IPDimmer,
    "HM-Sec-Key": KeyMatic,
    "HM-Sec-Key-S": KeyMatic,
    "HM-Sec-Key-O": KeyMatic,
    "HM-Sec-Key-Generic": KeyMatic,
    "HM-Sen-RD-O": Rain,
    "ST6-SH": EcoLogic,
    "HM-Sec-Sir-WM": RFSiren,
    "HmIP-MOD-HO": IPGarage,
    "HmIP-MOD-TM": IPGarage,
    "HmIP-WGC": IPGarageSwitch,
    "HM-LC-RGBW-WM": ColorEffectLight,
    "HmIP-MIOB": IPMultiIO,
    "HM-DW-WM": Dimmer,
    "HM-LC-DW-WM": ColdWarmDimmer,
    "HB-UNI-RGB-LED-CTRL": ColorEffectLight,
    "HmIP-MIO16-PCB": IPMultiIOPCB,
}
