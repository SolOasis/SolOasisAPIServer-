#!/usr/bin/env python
"""
Base class for all devices.
"""


class Discovery:
    """ Abstract class for all types of drones discovering. """

    def __init__(self):
        raise NotImplementedError("Discovery is an abstract class")
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"
        self.discovery = None
        self.all_devices = None

    def searchAllDevices(self):
        raise NotImplementedError("Discovery is an abstract class")

    def connectToDevice(self, assignedID, deviceName=None, deviceType=None):
        raise NotImplementedError("Discovery is an abstract class")


class Drone:
    """ Abstract class for all types of drones. """

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        raise NotImplementedError("Drone is an abstract class")
        self.ID = ID
        self.name = name
        self.drone = None

    def stop(self):
        self.drone.stop()

    def get_battery(self):
        return self.drone.get_battery()

    def get_state(self):
        return self.drone.get_state()

    def take_picture(self):
        return self.drone.take_picture()

    def get_picture(self):
        return self.drone.get_picture()


if __name__ == '__main__':
    print (__doc__)
