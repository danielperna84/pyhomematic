pyhomematic
===========

Proof of concept Python 3 Interface to interact with Homematic devices

This module is aimed to provide easy control of Homematic devices hooked up to a regular CCU or Homegear.
It includes a XML-RPC server to receive events emitted by devices. If a callbackfunction is passed to the server-object, it is possible to react to events using this function.
Compatibility is only given for Python 3, but it should be easy to make it work with Python 2.7 as well.

As of now, usage is as follows (with homegear running on the same machine):
    >>> import homematic
    >>> s = homematic.create_server() # Create server
    >>> s.devices['address_of_rollershutter_device'].move_down() # Move rollershutter down
    >>> s.devices_all['address_of_doorcontact:1'].getValue("STATE") # True or False, depending on state
    >>> s.stop() #Shutdown to finish the server thread and quit

This sample connects to the Homegear-server running on the same machine, closes the window blind using the rollershutter device, queries the state of a door contact, then stops the server because a sample doesn't need to do more. 

Theoretically all Homematic devices will be automatically detected and directly provide the getValue and setValue methods needed to perform any action.
Additionally the following devices provide convenince methods to easily perform certain tasks:

- HM-Sec-SC-2 (Door contact - open/closed sensor)
- HM-CC-RT-DN (Thermostat)
- HM-CC-RT-DN-BoM (Thermostat)
- ZEL STG RM FEP 230V (Rollershutter, by Roto Tronic)
- HM-LC-Bl1-FM * (Rollershutter, looks exactly like ZEL STG RM FEP 230V, so maybe they're compatible. Add it to _devices.DEVICETYPES to test it)

More devices might be supported in the future.