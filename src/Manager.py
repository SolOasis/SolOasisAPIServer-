#!/usr/bin/env python
"""
Manager class to access drones.
"""

import Drone
import cv2


class Manager:

    def __init__(self):
        self.all_devices = dict()
        self.all_drones = dict()
        self.discovery = Drone.Discovery()

    def searchAllDevices(self):
        self.all_devices = self.discovery.searchAllDevices()

    def assignDrone(self):
        assignedID = len(self.all_drones)
        drone = self.discovery.connectToDevice(assignedID)
        if not drone:
            print ('Unable to assign a drone')
            return False
        self.all_drones[assignedID] = drone
        return assignedID

    def getDrone(self, droneID):
        if not (droneID in self.all_drones):
            return False
        return self.all_drones[droneID]

    def regainDrone(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        drone.stop()
        del self.all_drones[droneID]
        return True

    def getDroneBattery(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_battery()

    def getDroneState(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_state()

    def takePicture(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.take_picture()


if __name__ == "__main__":
    drone_manager = Manager()
    drone_manager.searchAllDevices()
    drone = drone_manager.assignDrone()
    ardrone3 = drone_manager.getDroneState(drone)['ardrone3']
    for each in ardrone3:
        print (each, ardrone3[each])
        print ("")
    print ("Taking picture..")
    print (drone_manager.takePicture(drone))
    # print (drone_manager.getDroneState(drone))

    """
    cam = cv2.VideoCapture("./bebop.sdp")
    while True:
        ret, frame = cam.read()
        print (frame)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
    """
    drone_manager.regainDrone(drone)
