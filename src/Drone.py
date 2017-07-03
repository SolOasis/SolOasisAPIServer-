#!/usr/bin/env python
"""
Wrapper class for all devices.
"""

import Bybop_Discovery
import Bybop_Device


class Discovery:

    def __init__(self):
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"
        self.discovery = None
        self.all_devices = None

    def searchAllDevices(self):
        print ('Searching for devices')
        self.discovery = Bybop_Discovery.Discovery(
                Bybop_Discovery.DeviceID.ALL)
        self.discovery.wait_for_change()
        self.all_devices = self.discovery.get_devices()
        print (self.all_devices)
        self.discovery.stop()
        if not self.all_devices:
            print ("Error: No device found.")
            return False
        return self.all_devices

    def connectToDevice(self, assignedID, deviceName=None):
        if not len(self.all_devices):
            return False
        if (deviceName):
            device = self.all_devices[deviceName]
        else:
            device = self.all_devices.itervalues().next()
            deviceName = Bybop_Discovery.get_name(device)
        print ("Connect to ", deviceName)
        drone = Drone(
                assignedID,
                deviceName,
                device,
                self.d2c_port,
                self.controller_type,
                self.controller_name)

        return drone


class Drone:

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        self.ID = ID
        self.name = name
        self.drone = Bybop_Device.create_and_connect(
                device,
                d2c_port,
                controller_type,
                controller_name)

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
