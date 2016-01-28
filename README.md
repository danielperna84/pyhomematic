# pyhomematic
Proof of concept Python 3 Interface to interact with Homematic devices

This module is aimed to provide easy control of Homematic devices hooked up to a regular CCU or Homegear.
It includes a XML-RPC server to receive events emitted by devices. If a callbackfunction is passed to the server-object, it is possible to react to events using this function.
Compatibility is only given for Python 3, but it should be easy to make it work with Python 2.7 as well.

As of now, usage is as follows (with homegear running on the same machine):
```python
import pyhomematic
s = pyhomematic.create_server() #Create server
s.devices['id_of_rollershutter_interface'].move_down() #Move rollershutter down
s.stop() #Shutdown and quit
```

This sample connects to the Homegear-server running on the same machine, closes the window blind using the rollershutter device, then stops the server because a sample doesn't need to do more. 

Currently supported Homematic devices:
* HM-Sec-SC-2 (Door contact - open/closed sensor)
* HM-CC-RT-DN (Thermostat)
* HM-CC-RT-DN-BoM (Thermostat)
* ZEL STG RM FEP 230V (Rollershutter, by Roto Tronic)
* HM-LC-Bl1-FM * (Rollershutter, looks exactly like ZEL STG RM FEP 230V, so maybe they're compatible. Add it to pyhomematic.DEVICETYPES to test it)
