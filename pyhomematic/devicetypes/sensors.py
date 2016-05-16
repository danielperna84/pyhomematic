import logging
from . import generic

LOG = logging.getLogger(__name__)


class ShutterContact(generic.HMDevice):
    """
    HM-Sec-SC, HM-Sec-SC-2, ZEL STG RM FFK
    Door / Window contact that emits its open/closed state.
    """

    @property
    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        if self._PARENT:
            error = self._proxy.getValue(self._PARENT + ':1', 'ERROR')
        else:
            error = self.CHILDREN[1].getValue('ERROR')
        if error == 7:
            return True
        else:
            return False

    @property
    def low_batt(self):
        """ Returns if the battery is low. """
        return self.getValue('LOWBAT')

    @property
    def is_open(self):
        """ Returns if the contact is open. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return self.CHILDREN[1].getValue('STATE')

    @property
    def is_closed(self):
        """ Returns if the contact is closed. """
        if self._PARENT:
            return not self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return not self.CHILDREN[1].getValue('STATE')

    @property
    def state(self):
        """ Returns if the contact is 'open' or 'closed'. """
        if self.is_closed:
            return 'closed'
        else:
            return 'open'


class RotaryHandleSensor(generic.HMDevice):
    """
    HM-Sec-RHS, ZEL STG RM FDK, HM-Sec-RHS-2, HM-Sec-xx
    Window handle contact
    """
    @property
    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        if self._PARENT:
            error = self._proxy.getValue(self._PARENT + ':1', 'ERROR')
        else:
            error = self.CHILDREN[1].getValue('ERROR')
        if error == 1:
            return True
        else:
            return False

    @property
    def low_batt(self):
        """ Returns if the battery is low. """
        return self.getValue('LOWBAT')

    @property
    def is_open(self):
        """ Returns if the handle is open. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE') == 2
        else:
            return self.CHILDREN[1].getValue('STATE') == 2

    @property
    def is_closed(self):
        """ Returns if the handle is closed. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE') == 0
        else:
            return self.CHILDREN[1].getValue('STATE') == 0

    @property
    def is_tilted(self):
        """ Returns if the handle is tilted. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE') == 1
        else:
            return self.CHILDREN[1].getValue('STATE') == 1

    @property
    def state(self):
        """ Returns current state of handle (0=closed, 1=tilted, 2=open) """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT + ':1', 'STATE')
        else:
            return self.CHILDREN[1].getValue('STATE')


class Remote(generic.HMDevice):
    pass


DEVICETYPES = {
    "HM-Sec-SC": ShutterContact,
    "HM-Sec-SC-2": ShutterContact,
    "ZEL STG RM FFK": ShutterContact,
    "HM-Sec-RHS": RotaryHandleSensor,
    "ZEL STG RM FDK": RotaryHandleSensor,
    "HM-Sec-RHS-2": RotaryHandleSensor,
    "HM-Sec-xx": RotaryHandleSensor,
    "HM-RC-8": Remote
}