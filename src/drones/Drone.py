#!/usr/bin/env python
"""
Base class for all devices.
"""
from enum import Enum
import time


class FState(Enum):
    """ Finite state of the drone. """
    SHUTDOWN = 0
    RECHARGING = 1
    STANDBY = 2
    ASSIGNED = 3
    HEADING = 4
    OCCUPIED = 5
    RETURNING = 6
    DISCONNECTED = 7
    UNKNOWNED = 8


class DroneStateMachine:
    """ Finite state machine of the drone. """

    def __init__(self, init_state):
        self.state = init_state
        self.lastState = FState.SHUTDOWN
        self.stateHistory = list()
        self.addRecord()

    def addRecord(self):
        """ Add time and state record to history. """
        record = time.strftime("%Y-%m-%d %H:%M:%S"), self.state
        self.stateHistory.append(record)

    def toShutdown(self):
        """ Transite to shutdown state. """
        if self.state != FState.STANDBY:
            raise IOError("Only shut down when standby, not". self.sate)
        self.lastState = self.state
        self.state = FState.SHUTDOWN
        self.addRecord()

    def toRecharging(self):
        """ Transite to recharging state. """
        if self.state != FState.STANDBY and \
                self.state != FState.RETURNING and \
                self.state != FState.SHUTDOWN:
            raise IOError("Only recharge in the station \
                    (after returning, standby or shutdown) \
                    not,", self.state)
        self.lastState = self.state
        self.state = FState.RECHARGING
        self.addRecord()

    def toStandby(self):
        """ Transite to standby state. """
        self.lastState = self.state
        self.state = FState.STANDBY
        self.addRecord()


    def toAssigned(self):
        """ Transite to assigned state. """
        if self.state != FState.STANDBY and \
                self.state != FState.RETURNING and \
                self.state != FState.RECHARGING and \
                self.state != FState.DISCONNECTED:
            raise IOError("Only head when standby, not", self.state)
        self.lastState = self.state
        self.state = FState.ASSIGNED
        self.addRecord()

    def toHeading(self):
        """ Transite to heading state. """
        if self.state != FState.ASSIGNED and \
                self.state != FState.DISCONNECTED:
            raise IOError("Only head when assigned, not", self.state)
        self.lastState = self.state
        self.state = FState.HEADING
        self.addRecord()

    def toOccupied(self):
        """ Transite to occupied state. """
        if self.state != FState.HEADING and \
                self.state != FState.DISCONNECTED:
            raise IOError("Only occupied after heading, not", self.state)
        self.lastState = self.state
        self.state = FState.OCCUPIED
        self.addRecord()

    def toReturning(self):
        """ Transite to returning state. """
        self.lastState = self.state
        self.state = FState.RETURNING
        self.addRecord()

    def toDisconnected(self):
        """ Transite to disconnected state. """
        if self.state == FState.SHUTDOWN:
            raise IOError("Shut down must be disconnected.")
        self.lastState = self.state
        self.state = FState.DISCONNECTED
        self.addRecord()

    def resume(self, last_state):
        """ Transite to last_stae. Used after reconnection. """
        self.lastState = FState.DISCONNECTED
        self.state = last_state
        del self.stateHistory[-1]  #Delete reconnection standby
        self.addRecord()


    def getState(self):
        """ Get current state. """
        return self.state

    def getRecord(self):
        """ Get stateHistory. """
        return self.stateHistory

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
