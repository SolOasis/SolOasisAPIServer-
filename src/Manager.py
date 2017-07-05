#!/usr/bin/env python
"""
Manager class to access drones.
"""

from drones.ParrotDrones import ParrotDiscovery as Discovery
from Monitor import Monitor
import sys
import pygame
import PIL.Image
# from drones.ParrotDrones import BebopDrone as Drone
# import cv2


class Manager:

    def __init__(self):
        self.all_devices = dict()
        self.all_drones = dict()
        self.monitor = Monitor()
        self.discovery = Discovery()

    def searchAllDevices(self):
        self.all_devices = self.discovery.searchAllDevices()

    def assignDrone(self):
        assignedID = len(self.all_drones)
        drone = self.discovery.connectToDevice(assignedID)
        if not drone:
            print ('Unable to assign a drone')
            return False
        self.all_drones[assignedID] = drone
        self.monitor.addDrone(assignedID, drone)
        # drone.setVerbose()
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

    def getPicture(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_picture()

    def takeOff(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.take_off()

    def land(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.land()

    def emergency(self, droneID):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.emergency()

    def navigate(self, droneID, destination):
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.navigate(destination)


if __name__ == "__main__":
    drone_manager = Manager()
    drone_manager.searchAllDevices()
    drone = drone_manager.assignDrone()
    for each in drone_manager.getDroneState(drone):
        print each
    ardrone3 = drone_manager.getDroneState(drone)['ardrone3']
    for each in ardrone3:
        print (each, ardrone3[each])
        print ("")

    print ("Navigating ..")
    destination = (30, 30, 30, 1, 2.4)
    print (drone_manager.navigate(drone, destination))
    print ("Taking picture..")
    print (drone_manager.takePicture(drone))

    img = drone_manager.getPicture(drone)
    basewidth = 400
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    pic = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    # pic = pic.resize((weight, height), PIL.Image.ANTIALIAS)

    pygame.init()
    mode = pic.mode
    size = pic.size
    data = pic.tobytes()
    pic = pygame.image.fromstring(data, size, mode)
    screen = pygame.display.set_mode(size)
    screen.blit(pic, (0, 0))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
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
    sys.exit()
