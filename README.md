# pyhomematic
PoC Interface to interact with Homematic devices

This module is aimed to provide easy control of Homematic devices hooked up to a regular CCU or Homegear.
It includes a XML-RPC server to receive events emitted by devices. If a callbackfunction is passed to the server-object, it is possible to react to events using this function.

As of now, usage is as follows (with homegear running on the same machine):
```python
import pyhomematic
s = pyhomematic.create_server() #Create server
s.devices['id_of_rollershutter_interface'].move_down() #Move rollershutter down
s.stop() #Shutdown and quit
```

This sample connects to the Homegear-server, closes the window blind using the rollershutter device, then stops the server because a sample doesn't need to do more. 