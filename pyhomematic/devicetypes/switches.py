import logging
from . import generic

LOG = logging.getLogger(__name__)


class Blind(generic.HMDevice):
    """
    HM-LC-Bl1-SM, HM-LC-Bl1-FM, HM-LC-Bl1-PB-FM, ZEL STG RM FEP 230V, 263 146, HM-LC-BlX
    Blind switch that raises and lowers roller shutters or window blinds.
    """

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super(Blind, self).__init__(device_description, proxy, resolveparamsets)
        self._working = None

        def working_callback(device, caller, attribute, value):
            attribute = str(attribute).upper()
            if attribute == 'WORKING':
                self._working = value

        self.setEventCallback(working_callback, True)

    @property
    def level(self):
        """Return current position. Return value is float() from 0.0 (0% open) to 1.0 (100% open)."""
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'LEVEL')
        else:
            return self.CHILDREN[1].getValue('LEVEL')

    @level.setter
    def level(self, position):
        """Seek a specific position by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("RollerShutter.level: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'LEVEL', position)
        else:
            self.CHILDREN[1].setValue('LEVEL', position)

    def move_up(self):
        """Move the shutter up all the way."""
        self.level = 1.0

    def move_down(self):
        """Move the shutter down all the way."""
        self.level = 0.0

    def stop(self):
        """Stop moving."""
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'STOP', True)
        else:
            self.CHILDREN[1].setValue('STOP', True)

    @property
    def working(self):
        """Return True of False if working or not"""
        if self._PARENT:
            if self._working is None:
                self._working = self._proxy.getValue(self._PARENT + ':1', 'WORKING')
            return self._working
        else:
            if self.CHILDREN[1]._working is None:
                self.CHILDREN[1]._working = self.CHILDREN[1].getValue('WORKING')
            return self.CHILDREN[1]._working


class Dimmer(generic.HMDevice):
    """
    HM-LC-Dim1L-Pl, HM-LC-Dim1L-CV, HM-LC-Dim1L-Pl-3, HM-LC-Dim1L-CV-2
    Dimmer switch that controls level of light brightness.
    """

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super(Dimmer, self).__init__(device_description, proxy, resolveparamsets)
        self._working = None

        def working_callback(device, caller, attribute, value):
            attribute = str(attribute).upper()
            if attribute == 'WORKING':
                self._working = value

        self.setEventCallback(working_callback, True)

    @property
    def level(self):
        """Return current brightness level. Return value is float() from 0.0 (0% off) to 1.0 (100% maximum brightness)."""
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'LEVEL')
        else:
            return self.CHILDREN[1].getValue('LEVEL')

    @level.setter
    def level(self, brightness):
        """Set e brightness by specifying a float() from 0.0 to 1.0."""
        try:
            brightness = float(brightness)
        except Exception as err:
            LOG.debug("Dimmer.level: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'LEVEL', brightness)
        else:
            self.CHILDREN[1].setValue('LEVEL', brightness)

    def on(self):
        """Turn light to maximum brightness."""
        self.level = 1.0

    def off(self):
        """Turn light off."""
        self.level = 0.0

    @property
    def working(self):
        """Return True of False if working or not"""
        if self._PARENT:
            if self._working is None:
                self._working = self._proxy.getValue(self._PARENT + ':1', 'WORKING')
            return self._working
        else:
            if self.CHILDREN[1]._working is None:
                self.CHILDREN[1]._working = self.CHILDREN[1].getValue('WORKING')
            return self.CHILDREN[1]._working


class Switch(generic.HMDevice):
    """
    HM-LC-Sw1-Pl, HM-LC-Sw1-Pl-2, HM-LC-Sw1-SM, HM-LC-Sw2-SM, HM-LC-Sw4-SM, HM-LC-Sw4-PCB, HM-LC-Sw4-WM, HM-LC-Sw1-FM,
    263 130, HM-LC-Sw2-FM, HM-LC-Sw1-PB-FM, HM-LC-Sw2-PB-FM, HM-LC-Sw4-DR, HM-LC-Sw2-DR, ZEL STG RM FZS,
    ZEL STG RM FZS-2, HM-LC-SwX
    Switch turning plugged in device on or off.
    """

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super(Switch, self).__init__(device_description, proxy, resolveparamsets)
        self._working = None

        def working_callback(device, caller, attribute, value):
            attribute = str(attribute).upper()
            if attribute == 'WORKING':
                self._working = value

        self.setEventCallback(working_callback, True)

    @property
    def is_on(self):
        """ Returns if switch is on. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return self.CHILDREN[1].getValue('STATE')

    @property
    def is_off(self):
        """ Returns if switch is off. """
        if self._PARENT:
            return not self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return not self.CHILDREN[1].getValue('STATE')

    @property
    def state(self):
        """ Returns if switch is 'on' or 'off'. """
        if self.is_off:
            return False
        else:
            return True

    @state.setter
    def state(self, onoff):
        """Turn switch on/off"""
        try:
            onoff = bool(onoff)
        except Exception as err:
            LOG.debug("Switch.state: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'STATE', onoff)
        else:
            self.CHILDREN[1].setValue('STATE', onoff)

    def on(self):
        """Turn switch on."""
        self.state = True

    def off(self):
        """Turn switch off."""
        self.state = False

    @property
    def working(self):
        """Return True of False if working or not"""
        if self._PARENT:
            if self._working is None:
                self._working = self._proxy.getValue(self._PARENT + ':1', 'WORKING')
            return self._working
        else:
            if self.CHILDREN[1]._working is None:
                self.CHILDREN[1]._working = self.CHILDREN[1].getValue('WORKING')
            return self.CHILDREN[1]._working


class SwitchPowermeter(generic.HMDevice):
    """
    HM-ES-PMSw1-Pl, HM-ES-PMSw1-Pl-DN-R1, HM-ES-PMSw1-Pl-DN-R2, HM-ES-PMSw1-Pl-DN-R3, HM-ES-PMSw1-Pl-DN-R4
    HM-ES-PMSw1-Pl-DN-R5, HM-ES-PMSw1-DR, HM-ES-PMSw1-SM, HM-ES-PMSwX
    Switch turning plugged in device on or off and measuring energy consumption.
    """

    @property
    def is_on(self):
        """ Returns if switch is on. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return self.CHILDREN[1].getValue('STATE')

    @property
    def is_off(self):
        """ Returns if switch is off. """
        if self._PARENT:
            return not self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return not self.CHILDREN[1].getValue('STATE')

    @property
    def state(self):
        """ Returns if switch is 'on' or 'off'. """
        if self.is_off:
            return False
        else:
            return True

    @state.setter
    def state(self, onoff):
        """Turn switch on/off"""
        try:
            onoff = bool(onoff)
        except Exception as err:
            LOG.debug("SwitchPowermeter.state: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'STATE', onoff)
        else:
            self.CHILDREN[1].setValue('STATE', onoff)

    def on(self):
        """Turn switch on."""
        self.state = True

    def off(self):
        """Turn switch off."""
        self.state = False

    @property
    def is_working(self):
        """ Returns if switch is working or not. """
        if self._PARENT:
            return not self._proxy.getValue(self._PARENT + ':1', 'WORKING')
        else:
            return not self.CHILDREN[1].getValue('WORKING')

    def set_ontime(self, ontime):
        """Set duration th switch stays on when toggled. """
        try:
            ontime = float(ontime)
        except Exception as err:
            LOG.debug("SwitchPowermeter.set_ontime: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'ON_TIME', ontime)
        else:
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
