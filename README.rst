pyhomematic
===========

Python 3 Interface to interact with Homematic devices.

This module is aimed to provide easy (bi-directional) control of Homematic devices hooked up to a regular CCU or Homegear. The focus is to be able to receive events. If you are only interested in actively controlling devices, you can use the Python-built-in xmlrpc.client.ServerProxy (Python 3). See homematic._server.ServerThread.connect on how to connect to a CCU / Homegear as a client.
Included is a XML-RPC server to receive events emitted by devices. Multiple callback functions can be set for devices to handle events. You can choose to bequeath callbacks from devices to their channels or not. Channels can not bequeath to their parent devices. You can also pass a callback funtion when creating the server, which then will (additionally) receive all events emitted by any paired device.
You may specify a devicefile (JSON) to store known devices. This might speed up startup a bit. If you don't, paired devices will always be propagated upon startup. If devices get paired while the server is running, they should be automatically detected and usable. To get notified about such events, it is possible to pass a systemcallback(source, *args)-function while creating the server.
Compatibility currently is only given for Python 3, but it should be easy to make it work with Python 2.7 as well. Python 2.6, not so much.

As of now, usage is as follows (you could leave away the listening and remote addresses when everything is running on one machine):
    >>> def syscb(src, *args):
    >>>     print(src)
    >>>     for arg in args:
    >>>         print(arg)
    >>> def cb1(address, interface_id, key, value):
    >>>     print("CALLBACK WITH CHANNELS: %s, %s, %s, %s" % (address, interface_id, key, value))
    >>> def cb2(address, interface_id, key, value):
    >>>     print("CALLBACK WITHOUT CHANNELS: %s, %s, %s, %s" % (address, interface_id, key, value))
    >>> import homematic
    >>> homematic.create_server(local="192.168.1.12", localport=7080, remote="192.168.1.23", remoteport=2001, systemcallback=syscb) # Create server thread
    >>> homematic.start() # Start server thread, connect to homegear, initialize to receive events
    >>> homematic.devices['address_of_rollershutter_device'].move_down() # Move rollershutter down
    >>> homematic.devices_all['address_of_doorcontact:1'].getValue("STATE") # True or False, depending on state
    >>> homematic.devices['address_of_doorcontact'].setEventCallback(cb1) # Add first callback
    >>> homematic.devices['address_of_doorcontact'].setEventCallback(cb2, bequeath=False) # Add second callback
    >>> homematic.stop() # Shutdown to finish the server thread and quit

This example connects to the Homegear-server running on the same machine, closes the window shutter using the rollershutter device, queries the state of a door contact, adds callbacks for the door contact, then stops the server thread because a sample doesn't need to do more. The server has to be stopped because otherwise Python might hang.
An example.py can be found at https://github.com/danielperna84/pyhomematic

Theoretically all Homematic devices will be automatically detected and directly provide the getValue and setValue methods needed to perform any action.
Additionally the following devices provide convenience methods to easily perform certain tasks:

- HM-Sec-SC-2 (Door contact - open/closed sensor)
- HM-CC-RT-DN (Thermostat)
- HM-CC-RT-DN-BoM (Thermostat)
- ZEL STG RM FEP 230V (Rollershutter, by Roto Tronic)
- HM-LC-Bl1-FM * (Rollershutter, looks exactly like ZEL STG RM FEP 230V, so maybe they're compatible. Add it to _devices.DEVICETYPES to test it)

More devices might be supported in the future. 