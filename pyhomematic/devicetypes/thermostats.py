import logging
from . import generic

LOG = logging.getLogger(__name__)


class Thermostat(generic.HMDevice):
    """
    HM-CC-RT-DN, HM-CC-RT-DN-BoM
    ClimateControl-RadiatorThermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    AUTO_MODE = 0
    MANU_MODE = 1
    PARTY_MODE = 2
    BOOST_MODE = 3

    @property
    def actual_temperature(self):
        """ Returns the current temperature. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':4', 'ACTUAL_TEMPERATURE')
        else:
            return self.CHILDREN[4].getValue('ACTUAL_TEMPERATURE')

    @property
    def set_temperature(self):
        """ Returns the current temperature. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':4', 'SET_TEMPERATURE')
        else:
            return self.CHILDREN[4].getValue('SET_TEMPERATURE')

    @set_temperature.setter
    def set_temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("Thermostat.set_temperature: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':4', 'SET_TEMPERATURE', target_temperature)
        else:
            self.CHILDREN[4].setValue('SET_TEMPERATURE', target_temperature)

    @property
    def turnoff(self):
        """ Turn off Thermostat. """
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':4', 'SET_TEMPERATURE', 4.5)
        else:
            self.CHILDREN[4].setValue('SET_TEMPERATURE', 4.5)

    @property
    def mode(self):
        """ Return mode. """
        if self._PARENT:
            # 1 Manu, 0 Auto, 3 Boost
            return self._proxy.getValue(self._PARENT + ':4', 'CONTROL_MODE')
        else:
            return self.CHILDREN[4].getValue("CONTROL_MODE")

    @mode.setter
    def mode(self, setmode):
        """ Set mode. """
        if setmode == self.AUTO_MODE:
            mode = 'AUTO_MODE'
        elif setmode == self.MANU_MODE:
            mode = 'MANU_MODE'
        elif setmode == self.PARTY_MODE:
            mode = 'PARTY_MODE'
        elif setmode == self.BOOST_MODE:
            mode = 'BOOST_MODE'
        else:
            return False
        if self._PARENT:
            return self._proxy.setValue(self._PARENT + ':4', mode, True)
        else:
            return self.CHILDREN[4].setValue(mode, True)

    @property
    def automode(self):
        """ Return auto mode state. """
        return self.mode == self.AUTO_MODE

    @automode.setter
    def automode(self, setauto):
        """ Turn on auto mode. """
        self.mode = self.AUTO_MODE

    @property
    def manumode(self):
        """ Return manual mode state. """
        return self.mode == self.MANU_MODE

    @manumode.setter
    def manumode(self, setmanu):
        """ Turn on manual mode. """
        self.mode = self.MANU_MODE

    @property
    def partymode(self):
        """ Return party mode state. """
        return self.mode == self.PARTY_MODE

    @partymode.setter
    def partymode(self, partymode):
        """ Turn on paty mode. """
        self.mode = self.PARTY_MODE

    @property
    def boostmode(self):
        """ Return boost state. """
        return self.mode == self.BOOST_MODE

    @boostmode.setter
    def boostmode(self, setboost):
        """ Turn on boost mode. """
        self.mode = self.BOOST_MODE

    @property
    def battery_state(self):
        """ Returns the current battery state. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':4', 'BATTERY_STATE')
        else:
            return self.CHILDREN[4].getValue('BATTERY_STATE')

    @property
    def valve_state(self):
        """ Returns the current valve state. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':4', 'VALVE_STATE')
        else:
            return self.CHILDREN[4].getValue('VALVE_STATE')


class MAXThermostat(generic.HMDevice):
    """
    BC-RT-TRX-CyG, BC-RT-TRX-CyG-2, BC-RT-TRX-CyG-3, BC-RT-TRX-CyG-4
    ClimateControl-RadiatorThermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    AUTO_MODE = 0
    MANU_MODE = 1
    PARTY_MODE = 2
    BOOST_MODE = 3

    @property
    def actual_temperature(self):
        """ Returns the current temperature. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'ACTUAL_TEMPERATURE')
        else:
            return self.CHILDREN[1].getValue('ACTUAL_TEMPERATURE')

    @property
    def set_temperature(self):
        """ Returns the current temperature. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'SET_TEMPERATURE')
        else:
            return self.CHILDREN[1].getValue('SET_TEMPERATURE')

    @set_temperature.setter
    def set_temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("Thermostat.set_temperature: Exception %s" % (err,))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'SET_TEMPERATURE', target_temperature)
        else:
            self.CHILDREN[1].setValue('SET_TEMPERATURE', target_temperature)

    @property
    def turnoff(self):
        """ Turn off Thermostat. """
        if self._PARENT:
            self._proxy.setValue(self._PARENT + ':1', 'SET_TEMPERATURE', 4.5)
        else:
            self.CHILDREN[1].setValue('SET_TEMPERATURE', 4.5)

    @property
    def mode(self):
        """ Return mode. """
        if self._PARENT:
            # 1 Manu, 0 Auto, 3 Boost
            return self._proxy.getValue(self._PARENT + ':1', 'CONTROL_MODE')
        else:
            return self.CHILDREN[1].getValue("CONTROL_MODE")

    @mode.setter
    def mode(self, setmode):
        """ Set mode. """
        if setmode == self.AUTO_MODE:
            mode = 'AUTO_MODE'
        elif setmode == self.MANU_MODE:
            mode = 'MANU_MODE'
        elif setmode == self.PARTY_MODE:
            mode = 'PARTY_MODE'
        elif setmode == self.BOOST_MODE:
            mode = 'BOOST_MODE'
        else:
            return False
        if self._PARENT:
            return self._proxy.setValue(self._PARENT + ':1', mode, True)
        else:
            return self.CHILDREN[1].setValue(mode, True)

    @property
    def automode(self):
        """ Return auto mode state. """
        return self.mode == self.AUTO_MODE

    @automode.setter
    def automode(self, setauto):
        """ Turn on auto mode. """
        self.mode = self.AUTO_MODE

    @property
    def manumode(self):
        """ Return manual mode state. """
        return self.mode == self.MANU_MODE

    @manumode.setter
    def manumode(self, setmanu):
        """ Turn on manual mode. """
        self.mode = self.MANU_MODE

    @property
    def partymode(self):
        """ Return party mode state. """
        return self.mode == self.PARTY_MODE

    @partymode.setter
    def partymode(self, partymode):
        """ Turn on paty mode. """
        self.mode = self.PARTY_MODE

    @property
    def boostmode(self):
        """ Return boost state. """
        return self.mode == self.BOOST_MODE

    @boostmode.setter
    def boostmode(self, setboost):
        """ Turn on boost mode. """
        self.mode = self.BOOST_MODE

    @property
    def battery_state(self):
        """ Returns the current battery state. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':0', 'LOWBAT')
        else:
            return self.CHILDREN[0].getValue('LOWBAT')

DEVICETYPES = {
    "HM-CC-RT-DN": Thermostat,
    "HM-CC-RT-DN-BoM": Thermostat,
    "BC-RT-TRX-CyG": MAXThermostat,
    "BC-RT-TRX-CyG-2": MAXThermostat,
    "BC-RT-TRX-CyG-3": MAXThermostat,
    "BC-RT-TRX-CyG-4": MAXThermostat
}
