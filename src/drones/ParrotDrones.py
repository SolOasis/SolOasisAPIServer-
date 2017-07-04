#!/usr/bin/env python
"""
Derived class for Parrot devices.
"""
import bybop.Bybop_Discovery as Bybop_Discovery
import bybop.Bybop_Device as Bybop_Device
from Drone import Drone, Discovery


class ParrotDiscovery(Discovery):

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

    def connectToDevice(self, assignedID, deviceName=None, deviceType='Bebop'):
        if not len(self.all_devices):
            return False
        if (deviceName):
            device = self.all_devices[deviceName]
        else:
            device = self.all_devices.itervalues().next()
            deviceName = Bybop_Discovery.get_name(device)
        print ("Connect to ", deviceName)
        if (deviceType == 'Bebop'):
            drone = BebopDrone(
                    assignedID,
                    deviceName,
                    device,
                    self.d2c_port,
                    self.controller_type,
                    self.controller_name)
        else:
            return False

        return drone


class BebopDrone(Drone):

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

    def take_off(self):
        return self.drone.take_off()

    def land(self):
        return self.drone.land()

    def emergency(self):
        return self.drone.emergency()

    def navigate(self, destination):
        print ("Going to ", destination)
        try:
            return self.drone.navigate(destination)
        except:
            print ("Fuction navigate not implemented")
            return True


if __name__ == '__main__':
    print (__doc__)
