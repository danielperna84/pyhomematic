import logging
from pyhomematic.devicetypes.generic import HMDevice

LOG = logging.getLogger(__name__)


class HMSensor(HMDevice):
    pass


class HMBinarySensor(HMDevice):
    @property
    def get_state(self, channel=1):
        """ Returns current state of handle """
        for name in self.BINARYNODE:
            return self.getBinaryData(name, channel)
        return None


class DefaultBinarySensor(HMBinarySensor):
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(self, device_description, proxy, resolveparamsets)

        self.BINARYNODE.update({"STATE": 1})
        self.ATTRIBUTENODE.update({"LOWBAT": None, "ERROR": 1})

    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        error = self.getAttributData("ERROR")
        if error == 1:
            return True
        else:
            return False

    def low_batt(self):
        """ Returns if the battery is low. """
        bat = self.getAttributData("LOWBAT")
        if bat is None:
            return 0
        return bat


class ShutterContact(DefaultBinarySensor):
    """
    HM-Sec-SC, HM-Sec-SC-2, ZEL STG RM FFK
    Door / Window contact that emits its open/closed state.
    """
    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        error = self.getAttributData("ERROR")
        if error == 7:
            return True
        else:
            return False

    def is_open(self):
        """ Returns if the contact is open. """
        return self.get_state()

    def is_closed(self):
        """ Returns if the contact is closed. """
        return not self.get_state()


class RotaryHandleSensor(DefaultBinarySensor):
    """
    HM-Sec-RHS, ZEL STG RM FDK, HM-Sec-RHS-2, HM-Sec-xx
    Window handle contact
    """
    def is_open(self):
        """ Returns if the handle is open. """
        return self.get_state() == 2

    def is_closed(self):
        """ Returns if the handle is closed. """
        return self.get_state() == 0

    def is_tilted(self):
        """ Returns if the handle is tilted. """
        return self.get_state() == 1


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
