import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)


class _working(HMDevice):
    def __init__(self, device_description, proxy, resolveparamsets=False):
        HMDevice.__init__(device_description, proxy, resolveparamsets)
        self._working = None

        def working_callback(device, caller, attribute, value):
            attribute = str(attribute).upper()
            if attribute == 'WORKING':
                self._working = value

        self.setEventCallback(working_callback, True)

    def isWorking(self, channel=1):
        """Return True of False if working or not"""
        if channel > self.ELEMENT:
            return False

        if self._working is None:
            self._working = self.CHILDREN[channel].getValue('WORKING')
        return self._working


class Blind(_working):
    """
    HM-LC-Bl1-SM, HM-LC-Bl1-FM, HM-LC-Bl1-PB-FM, ZEL STG RM FEP 230V, 263 146, HM-LC-BlX
    Blind switch that raises and lowers roller shutters or window blinds.
    """

    @property
    def level(self):
        """Return current position. Return value is float() from 0.0 (0% open) to 1.0 (100% open)."""
        return self.CHILDREN[1].getValue('LEVEL')

    @level.setter
    def level(self, position):
        """Seek a specific position by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("RollerShutter.level: Exception %s" % (err,))
            return False

        self.CHILDREN[1].setValue('LEVEL', position)

    def move_up(self):
        """Move the shutter up all the way."""
        self.level = 1.0

    def move_down(self):
        """Move the shutter down all the way."""
        self.level = 0.0

    def stop(self):
        """Stop moving."""
        self.CHILDREN[1].setValue('STOP', True)


class Dimmer(_working):
    """
    HM-LC-Dim1L-Pl, HM-LC-Dim1L-CV, HM-LC-Dim1L-Pl-3, HM-LC-Dim1L-CV-2
    HM-LC-Dim2L-SM, HM-LC-Dim2L-CV
    Dimmer switch that controls level of light brightness.
    """

    @property
    def ELEMENT(self):
        if "Dim2L" in self._TYPE:
            return 2

        return 1

    @property
    def level(self):
        """Return current brightness level. Return value is float() from 0.0 (0% off) to 1.0 (100% maximum brightness)."""
        return self.CHILDREN[1].getValue('LEVEL')

    @level.setter
    def level(self, brightness):
        """Set e brightness by specifying a float() from 0.0 to 1.0."""
        try:
            brightness = float(brightness)
        except Exception as err:
            LOG.debug("Dimmer.level: Exception %s" % (err,))
            return False

        self.CHILDREN[1].setValue('LEVEL', brightness)

    def on(self):
        """Turn light to maximum brightness."""
        self.level = 1.0

    def off(self):
        """Turn light off."""
        self.level = 0.0


class Switch(_working):
    """
    HM-LC-Sw1-Pl, HM-LC-Sw1-Pl-2, HM-LC-Sw1-SM, HM-LC-Sw2-SM, HM-LC-Sw4-SM, HM-LC-Sw4-PCB, HM-LC-Sw4-WM, HM-LC-Sw1-FM,
    263 130, HM-LC-Sw2-FM, HM-LC-Sw1-PB-FM, HM-LC-Sw2-PB-FM, HM-LC-Sw4-DR, HM-LC-Sw2-DR, ZEL STG RM FZS,
    ZEL STG RM FZS-2, HM-LC-SwX
    Switch turning plugged in device on or off.
    """

    @property
    def ELEMENT(self):
        if "Sw2" in self._TYPE:
            return 2
        elif "Sw4" in self._TYPE:
            return 4

        return 1

    def is_on(self, channel=1):
        """ Returns if switch is on. """
        return self.getState(channel=1)

    def is_off(self, channel=1):
        """ Returns if switch is off. """
        return not self.getState(channel=1)

    def getState(self, channel=1):
        """ Returns if switch is 'on' or 'off'. """
        if channel > self.ELEMENT:
            return false

        return self.CHILDREN[channel].getValue('STATE')

    def setState(self, onoff, channel=1):
        """Turn switch on/off"""
        try:
            onoff = bool(onoff)
            if channel > self.ELEMENT:
                raise
        except Exception as err:
            LOG.debug("Switch.setState: Exception %s" % (err,))
            return False

        self.CHILDREN[channel].setValue('STATE', onoff)

    def on(self, channel=1):
        """Turn switch on."""
        self.setState(True, channel)

    def off(self, channel=1):
        """Turn switch off."""
        self.setState(False, channel)


class SwitchPowermeter(Switch):
    """
    HM-ES-PMSw1-Pl, HM-ES-PMSw1-Pl-DN-R1, HM-ES-PMSw1-Pl-DN-R2, HM-ES-PMSw1-Pl-DN-R3, HM-ES-PMSw1-Pl-DN-R4
    HM-ES-PMSw1-Pl-DN-R5, HM-ES-PMSw1-DR, HM-ES-PMSw1-SM, HM-ES-PMSwX
    Switch turning plugged in device on or off and measuring energy consumption.
    """

    # Overwrite from Switch back to 1 element
    @property
    def ELEMENT(self):
        return 1

    def set_ontime(self, ontime):
        """Set duration th switch stays on when toggled. """
        try:
            ontime = float(ontime)
        except Exception as err:
            LOG.debug("SwitchPowermeter.set_ontime: Exception %s" % (err,))
            return False

        self.CHILDREN[1].setValue('ON_TIME', ontime)


DEVICETYPES = {
    "HM-LC-Bl1-SM": Blind,
    "HM-LC-Bl1-FM": Blind,
    "HM-LC-Bl1PBU-FM": Blind,
    "HM-LC-Bl1-PB-FM": Blind,
    "ZEL STG RM FEP 230V": Blind,
    "263 146": Blind,
    "HM-LC-BlX": Blind,
    "HM-LC-Dim1L-Pl": Dimmer,
    "HM-LC-Dim1L-Pl-3": Dimmer,
    "HM-LC-Dim1L-CV": Dimmer,
    "HM-LC-Dim1L-CV-2": Dimmer,
    "HM-LC-Sw1-Pl": Switch,
    "HM-LC-Sw1-Pl-2": Switch,
    "HM-LC-Sw1-SM": Switch,
    "HM-LC-Sw2-SM": Switch,
    "HM-LC-Sw4-SM": Switch,
    "HM-LC-Sw4-PCB": Switch,
    "HM-LC-Sw4-WM": Switch,
    "HM-LC-Sw1-FM": Switch,
    "263 130": Switch,
    "HM-LC-Sw2-FM": Switch,
    "HM-LC-Sw1-PB-FM": Switch,
    "HM-LC-Sw2-PB-FM": Switch,
    "HM-LC-Sw4-DR": Switch,
    "HM-LC-Sw2-DR": Switch,
    "ZEL STG RM FZS": Switch,
    "ZEL STG RM FZS-2": Switch,
    "HM-LC-SwX": Switch,
    "HM-ES-PMSw1-Pl": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R1": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R2": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R3": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R4": SwitchPowermeter,
    "HM-ES-PMSw1-Pl-DN-R5": SwitchPowermeter,
    "HM-ES-PMSw1-DR": SwitchPowermeter,
    "HM-ES-PMSw1-SM": SwitchPowermeter,
    "HM-ES-PMSwX": SwitchPowermeter
}
