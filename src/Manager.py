#!/usr/bin/env python
import sys
from Bybop_Discovery import Discovery, get_name, DeviceID
import Bybop_Device
from flask import Flask, jsonify

class Manager:

    def __init__(self):
        self.all_devices = dict()
        self.all_drones = dict()
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"
        pass

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
        return self.all_drones[droneName]
        """
        devices = self.all_devices.itervalues()
        device = devices.next()
        while device:
            if not device:
                return False
            if (droneName == get_name(device)):
                return device
            device = devices.next()

        """
        """
        for each_device in self.all_devices:
            if (droneName == get_name(each_device)):
                return each_device
        return False
        """

    def regainDrone(self, droneName):
        drone = self.getDrone(droneName)
        drone.stop()
        del self.all_drones[droneName]

    def getDroneBattery(self, droneName):
        drone = self.getDrone(droneName)
        if (drone):
            return drone.get_battery()
        return False

    def getDroneState(self, droneName):
        drone = self.getDrone(droneName)
        if (drone):
            return drone.get_state()
        return False


if __name__ == "__main__":
    print ("Manager")
