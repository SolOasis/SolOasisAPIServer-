#!/usr/bin/env python
"""
Base class for all devices.
"""


class Discovery:

    def __init__(self):
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"
        self.discovery = None
        self.all_devices = None

    def searchAllDevices(self):
        print ('Should not use this funcion before inheritance')
        return False

    def connectToDevice(self, assignedID, deviceName=None, deviceType=None):
        print ('Should not use this funcion before inheritance')
        return False


class Drone:

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
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
