#!/usr/bin/env python
"""
Base class for all devices.
"""
import time


class FState:
    """ Finite state of the drone. """
    SHUTDOWN = "Shutdown"
    RECHARGING = "Recharging"
    STANDBY = "Standby"
    ASSIGNED = "Assigned"
    HEADING = "Heading"
    OCCUPIED = "Occupied"
    RETURNING = "Returning"
    DISCONNECTED = "Disconnected"
    UNKNOWN = "Unknown"


class DroneStateTransitionError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


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
            raise DroneStateTransitionError("Only shut down when standby, not %s" %  self.sate)
        self.lastState = self.state
        self.state = FState.SHUTDOWN
        self.addRecord()

    def toRecharging(self):
        """ Transite to recharging state. """
        if self.state != FState.STANDBY and \
                self.state != FState.RETURNING and \
                self.state != FState.SHUTDOWN:
            raise DroneStateTransitionError("Only recharge in the station \
                    (after returning, standby or shutdown) \
                    not, %s" % self.state)
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
            raise DroneStateTransitionError("Only assign when standby, not %s" % self.state)
        self.lastState = self.state
        self.state = FState.ASSIGNED
        self.addRecord()

    def toHeading(self):
        """ Transite to heading state. """
        if self.state != FState.ASSIGNED and \
                self.state != FState.DISCONNECTED:
            raise DroneStateTransitionError("Only head when assigned, not %s" % self.state)
        self.lastState = self.state
        self.state = FState.HEADING
        self.addRecord()

    def toOccupied(self):
        """ Transite to occupied state. """
        if self.state != FState.HEADING and \
                self.state != FState.DISCONNECTED:
            raise DroneStateTransitionError("Only occupied after heading, not %s " %  self.state)
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
            raise DroneStateTransitionError("Shut down must be disconnected.")
        self.lastState = self.state
        self.state = FState.DISCONNECTED
        self.addRecord()

    def resume(self, last_state):
        """ Transite to last_stae. Used after reconnection. """
        if last_state == FState.DISCONNECTED:
            raise DroneStateTransitionError("Disconnected to disconnected.")
        self.lastState = FState.DISCONNECTED
        self.state = last_state
        del self.stateHistory[-1]  #Delete reconnection standby
        self.addRecord()


    def getState(self):
        """ Get current state. """
        return self.state

    def getHistory(self):
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
