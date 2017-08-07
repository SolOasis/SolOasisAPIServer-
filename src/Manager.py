#!/usr/bin/env python
"""
Manager class to access drones.
"""

# from drones.ParrotDrones import ParrotDiscovery as Discovery
# from ..test.drones.TestDrones import TestDiscovery as Discovery
from Monitor import Monitor
from drones.Drone import DroneStateTransitionError, FState
import sys
import pygame
import PIL.Image
from loggingConfig import setup_logger, LOG_DIR, log_debug
# from drones.ParrotDrones import BebopDrone as Drone
# import cv2
manager_log_file = LOG_DIR + '/manager.log'
manager_logger = setup_logger('Manager', manager_log_file,
                              shownInConsole=log_debug)


class Manager:
    """ Manager for all drones. """

    def __init__(self):
        self.all_devices = dict()
        self.all_drones = dict()
        self.monitor = Monitor(self)
        self.discovery = Discovery()

    def searchAllDevices(self):
        """ Search AND CONNECT all drones. """
        # Need to initialize to clear all connected drones,
        # Or the same drone would be connected twice
        # If there is drone.connection_status,
        # this part may be rewrite
        if len(self.all_devices):
            manager_logger.warning("Already searched!")
            return self.all_devices
        self.__init__()
        self.monitor.lock.acquire()
        manager_logger.info("Searching all devices ..")
        self.all_devices = self.discovery.searchAllDevices()
        self.monitor.lock.release()
        for assignedID in range(len(self.all_devices)):
            self.monitor.lock.acquire()
            manager_logger.info("Connecting to device with ID %d" % assignedID)
            drone = self.discovery.connectToDevice(assignedID)
            self.monitor.lock.release()
            if not drone:
                manager_logger.warning('Unable to assign drone %d' %
                                       assignedID)
                continue
            self.all_drones[assignedID] = drone
            self.monitor.addDrone(assignedID, drone)

        return self.all_devices

    def reconnectDrone(self, droneID, last_state):
        """ Used when losing connection of a drone. """
        manager_logger.info("Reconnect to drone %d .." % droneID)
        try:
            self.all_drones[droneID] = \
                    self.discovery.reconnectToDevice(droneID)
        except ValueError as e:
            manager_logger.error(e)
            return e
        else:
            try:
                self.all_drones[droneID].resumeState(last_state)
            except DroneStateTransitionError as e:
                manager_logger.error(e.message)
                self.navigateHome(droneID)
            return self.all_drones[droneID].getAssignedState()

    def releaseAllDevices(self):
        """ Used when turning off the server. Disconnect all drones. """
        # NOTE: should modify to ensure all standby.
        manager_logger.info("Releasing all devices  ..")
        for assignedID in range(len(self.all_devices)):
            drone = self.getDrone(assignedID)
            if drone.getAssignedState() != FState.STANDBY or \
                    drone.getAssignedState() != FState.ASSIGNED:
                self.navigateHome(assignedID)
                self.monitor.lock.acquire()
                manager_logger.warning("*** Warning: Releasing Drone " +
                                       str(drone.ID) + " with state: " +
                                       drone.getAssignedState() + " ***")
                self.monitor.lock.release()
            self.monitor.releaseDrone(assignedID)
            if drone:
                self.monitor.lock.acquire()
                manager_logger.warning("Drone %d shut down" % drone.ID)
                drone.shut_down()
                self.monitor.lock.release()
        # self.monitor.__init__(self)
        self.__init__()
        manager_logger.info("Released success.")
        return True

    def assignDrone(self):
        """ Assign a drone to the client if available. """
        # NOTE: this part should connect to some algorithm later.
        states = ["Invalid:"]
        for droneID, drone in self.all_drones.items():
            if drone.assign():
                manager_logger.info("Assign drone %d" % droneID)
                return droneID
            else:
                states.append(str(droneID) + ":" +
                              str(drone.getAssignedState()))
        return states

    def getAllDroneStatus(self):
        """ Get droneID, name and assigned status of all drones. """
        drones = dict()
        for key in self.all_drones:
            each_drone = self.all_drones[key]
            if not each_drone:
                continue
            (ID, name, drone_type,
             assignedState,
             assignedStateHistory) = each_drone.getInfo()
            state = self.getDroneState(ID)
            battery = self.getDroneBattery(ID)
            location = each_drone.get_location()
            threadMessage = self.monitor.getThreadMessage(ID)
            estimateNavTime = each_drone.estimate_nav_time()
            info = {
                    'droneID': ID,
                    'Name': name,
                    'Drone_Type': drone_type,
                    'AssignedState': assignedState,
                    'AssignedStateHistory': assignedStateHistory,
                    'Location': location,
                    'Battery': battery,
                    'State': state,
                    'ThreadMessage': threadMessage,
                    'EstimateNavigationTime': estimateNavTime
                    }
            drones[ID] = info
        return drones

    def getDrone(self, droneID):
        """ Get a given drone. """
        try:
            droneID = int(droneID)
        except:
            return False
        if not (droneID in self.all_drones):
            manager_logger.warning('Unable to get drone %d, \
                                   all drones: %s ' %
                                   (droneID, self.all_drones))
            return False
        return self.all_drones[droneID]

    def regainDrone(self, droneID):
        """ Regain control of given drone. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        manager_logger.info("Regaining drone %d .." % droneID)
        self.navigateHome(droneID)
        return True

    def getDroneBattery(self, droneID):
        """ Get battery percentage of given drone. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_battery()

    def getDroneState(self, droneID):
        """ Get state of given drone. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_state()

    def takePicture(self, droneID):
        """ Take a picture. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.take_picture()

    def getPicture(self, droneID):
        """ Get picture from the drone. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.get_picture()

    def startVideo(self, droneID):
        """ Start video recording.

        Video would store in the drone."""
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.start_video()

    def stopVideo(self, droneID):
        """ Stop video recording. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.stop_video()

    def takeOff(self, droneID):
        """ Take off. Should be at home position. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.take_off()

    def land(self, droneID):
        """ Landing. Should be at home position. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.land()

    def emergency(self, droneID):
        """ Emergency. May let the drone crash. """
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.emergency()

    def navigate(self, droneID, destination):
        """ Navigate to given GPS position with specific mode. """
        drone = self.getDrone(droneID)
        if not drone:
            return "Could not get drone. May be unassigned"
        manager_logger.info("Drone %d navigating to %s .." %
                            (droneID,  str(destination)))
        return drone.navigate(destination)

    def navigateHome(self, droneID):
        """ Navigate to home position. """
        # NOTE: not yet tested!!!
        manager_logger.info("DroneID %d returning home .. " % droneID)
        drone = self.getDrone(droneID)
        if not drone:
            return False
        return drone.navigate_home()


def main():
    """ Test basic functions of Manager """
    drone_manager = Manager()
    drone_manager.searchAllDevices()
    drone = drone_manager.assignDrone()
    for each in drone_manager.getDroneState(drone):
        print each

    print ("Navigating ..")
    destination = (30, 30, 30, 1, 2.4)
    print (drone_manager.navigate(drone, destination))

    size = width, height = 800, 600
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print ("Existing ..")
                    running = False
                elif event.key == pygame.K_t:
                    print ("Taking picture..")
                    print (drone_manager.takePicture(drone))
                elif event.key == pygame.K_g:
                    print ("Getting picture ..")
                    picStringIO = drone_manager.getPicture(drone)
                    pic = PIL.Image.open(picStringIO)
                    pic = pic.resize(size, PIL.Image.ANTIALIAS)
                    pic = pygame.image.fromstring(pic.tobytes(),
                                                  size, pic.mode)
                    screen.blit(pic, (0, 0))
                    pygame.display.flip()

                elif event.key == pygame.K_s:
                    print ("Start video .. ")
                    print (drone_manager.startVideo(drone))

                elif event.key == pygame.K_p:
                    print ("Stop video .. ")
                    print (drone_manager.stopVideo(drone))

                elif event.key == pygame.K_a:
                    print ("Getting state .. ")
                    ardrone3 = drone_manager.getDroneState(drone)['ardrone3']
                    for each in ardrone3:
                        print (each, ardrone3[each])
                        print ("")

    """
    cam = cv2.VideoCapture("./bebop.sdp")
    while True:
        ret, frame = cam.read()
        print (frame)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
    """
    # drone_manager.regainDrone(drone)
    drone_manager.releaseAllDevices()
    sys.exit()


# Run as test script
if __name__ == "__main__":
    # Run test drone
    if (len(sys.argv) > 1):
        from drones.TestDrones import TestDiscovery as Discovery
        """
        if __package__ is None:
            from os import path
            sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
            from test.drones.TestDrones import TestDiscovery as Discovery
        else:
            from ..test.drones.TestDrones import TestDiscovery as Discovery
        """
    else:
        from drones.ParrotDrones import ParrotDiscovery as Discovery

    main()
# Run as a module
else:
    # from os import path
    # sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from drones.TestDrones import TestDiscovery as Discovery

    # from test.drones.TestDrones import TestDiscovery as Discovery
    # from drones.ParrotDrones import ParrotDiscovery as Discovery
