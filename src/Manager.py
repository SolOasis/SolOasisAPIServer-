#!/usr/bin/env python
import sys
from Bybop_Discovery import Discovery, get_name, DeviceID
import Bybop_Device


class Manager:

    def __init__(self):
        self.all_devices = dict()
        self.all_drones = dict()
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"

    def searchAllDevices(self):
        print ('Searching for devices')
        discovery = Discovery(DeviceID.ALL)
        discovery.wait_for_change()
        self.all_devices = discovery.get_devices()
        print (self.all_devices)
        discovery.stop()
        if not self.all_devices:
            print ("Error in Manager::searchAllDevices()")
            return False
        return self.all_devices

    def assignDrone(self):
        device = self.all_devices.itervalues().next()
        print ("Connect to ", get_name(device))
        drone = Bybop_Device.create_and_connect(device,
                                                self.d2c_port,
                                                self.controller_type,
                                                self.controller_name)
        print (drone)
        self.all_drones[get_name(device)] = drone
        if drone is None:
            print ('Unable to connect to a product')
            sys.exit(1)
        return get_name(device)

    def getDrone(self, droneName):
        if not (droneName in self.all_drones):
            return False
        return self.all_drones[droneName]

    def regainDrone(self, droneName):
        drone = self.getDrone(droneName)
        if not drone:
            return False
        drone.stop()
        del self.all_drones[droneName]
        return True

    def getDroneBattery(self, droneName):
        drone = self.getDrone(droneName)
        if not drone:
            return False
        return drone.get_battery()

    def getDroneState(self, droneName):
        drone = self.getDrone(droneName)
        if not drone:
            return False
        return drone.get_state()


if __name__ == "__main__":
    print ("Manager")
