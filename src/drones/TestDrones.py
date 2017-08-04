#!/usr/bin/env python
""" Derived class for Test devices.

Should modify for Parrot or DJI drone later.
"""
import bybop.Bybop_Discovery as Bybop_Discovery
import bybop.Bybop_Device as Bybop_Device
from Drone import (Drone, Discovery, DroneStateMachine,
                   FState, DroneStateTransitionError)  # , cmpGPSLocation
import pickle
import os
import copy
from StringIO import StringIO
import random
import threading
import time
from loggingConfig import setup_logger, LOG_DIR_TODAY
testdrone_log_file = (LOG_DIR_TODAY + '/testdrone_' +
                      time.strftime("%Y-%m-%d_%H:%M") + '.log')
testdrone_logger = setup_logger('Testdrone', testdrone_log_file,
                                shownInConsole=False)

print (os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + '/../data/'
GPS_PRECISION = 0.0000005
GPS_TO_METER_RATIO = 110000
DRONE_SPEED = 10
DRONE_NAV_RANGE = 500
ALTITUDE_PRECISION = 1
TESTDRONE_UPDATE_PERIOD = 1


def readPickle(filename):
    """ Read from the testing data.

    Would not be used for production. """
    with open(filename, 'rb') as read_file:
        fileContent = pickle.load(read_file)
    print ("Read pickle from %s" % filename)
    return fileContent


def writePickle(filename, content):
    """ Write the testing data.

    Would not be used for production. """
    with open(filename, 'wb') as write_file:
        pickle.dump(content, write_file)
    print ("Write pickle into '%s'" % filename)


class TestDiscovery(Discovery):
    """ Derived class for discovering testing drones. """

    def __init__(self):
        self.d2c_port = 54321
        self.controller_type = "PC_test"
        self.controller_name = "bybop shell_test"
        self.discovery = None
        self.all_devices = dict()
        # Record connected devices,
        # (device_name: connected ID or "disconnected")
        self.all_devices_connection = dict()

    def searchAllDevices(self):
        """ Search all devices.

        Returns:
            A dictionary for all devices. """
        print ('Searching for devices')
        filename = DATA_DIR + "searchAllDevices.pickle"
        if os.path.isfile(filename):
            self.all_devices = readPickle(filename)
            device = copy.deepcopy(self.all_devices.itervalues().next())
            device.name = 'BebopDrone-Test001._arsdk-0901._udp.loca   '
            self.all_devices['BebopDrone-Test001 \
                    ._arsdk-0901._udp.local.'] = device
            device = copy.deepcopy(self.all_devices.itervalues().next())
            device.name = 'BebopDrone-Test002._arsdk-0901._udp.loca   '
            self.all_devices['BebopDrone-Test002. \
                    _arsdk-0901._udp.local.'] = device
            # self.all_devices_itv = self.all_devices.itervalues()
        else:
            self.discovery = Bybop_Discovery.Discovery(
                    Bybop_Discovery.DeviceID.ALL)
            self.discovery.wait_for_change()
            self.all_devices = self.discovery.get_devices()
            print (self.all_devices)
            self.discovery.stop()
            if not self.all_devices:
                print ("Error: No device found.")
                return False
            writePickle(filename, self.all_devices)
        for key, value in self.all_devices.items():
            self.all_devices_connection[key] = "disconnected"
        return self.all_devices

    def connectToDevice(self, assignedID, deviceName=None, deviceType='Bebop'):
        """ Connect to a device with assigned ID or device name.

        Returns:
            If Success: A connected drone.
            else: False. """
        if not len(self.all_devices):
            return False
        device = None
        if (deviceName):
            device = self.all_devices[deviceName]
        else:
            for key, value in self.all_devices.items():
                if self.all_devices_connection[key] == "disconnected":
                    self.all_devices_connection[key] = assignedID
                    device = value
                    deviceName = Bybop_Discovery.get_name(device)
                    break
            if not device:
                return False
        print ("Connect to " + str(deviceName))
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

    def reconnectToDevice(self, assignedID):
        """ Reconnect to given divice.

        Used by mananger when disconnected. """
        for key, value in self.all_devices_connection.items():
            if value == assignedID:
                deviceName = key
                drone = self.connectToDevice(assignedID, deviceName)
                if drone:
                    return drone
        raise ValueError("Not able to reconnect %d" % assignedID)


class BebopDrone(Drone):
    """ Derived class for testing Bebop drones manipulation.
    May have some difference with original Bebop drones"""

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        self.ID = ID
        self.name = name
        self.drone_type = 'Bebop'
        self.state = dict()
        self.start_position = None
        self.destination = None
        self.home_position = None
        self.GPS_precision = GPS_PRECISION
        self.GPS2meterRatio = GPS_TO_METER_RATIO
        self.altitude_precision = ALTITUDE_PRECISION
        self.drone_speed = DRONE_SPEED
        self.navRange = DRONE_NAV_RANGE
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.test_thread)
        self.assignedState = DroneStateMachine(FState.STANDBY)
        self.battery = 60 + self.ID
        filename = DATA_DIR + "testDrone.pickle"
        if os.path.isfile(filename):
            self.drone = readPickle(filename)
        else:
            self.drone = Bybop_Device.create_and_connect(
                    device,
                    d2c_port,
                    controller_type,
                    controller_name)
            writePickle(filename, "")
        self.state = self.get_state()
        self.home_position = self.get_location()
        self.destination = self.home_position
        self.thread.start()

    def getInfo(self):
        """ Get basic information of the drone. """
        return (self.ID, self.name, self.drone_type,
                self.assignedState.getState(),
                self.assignedState.getHistory())

    def getAssignedState(self):
        """ Get FSM state of the drone."""
        return self.assignedState.getState()

    def setVerbose(self):
        """ Set drone to verbose, printing more info for debugging. """
        return True
        self.drone.set_verbose(True)

    def checkShutdown(self):
        """ Check if drone shut down. """
        return (self.assignedState.getState() == FState.SHUTDOWN)

    def setDisconnected(self):
        """ Turn to disconnected state and

        Returns:
            last_state: last state, like "HEADING",
                        for resuming state. """
        last_state = self.assignedState.getState()
        try:
            self.assignedState.toDisconnected()
        except DroneStateTransitionError as exception:
            return exception.message
        return last_state

    def resumeState(self, last_state):
        """ Used after reconnection. """
        print (":::::::::::::::" +
               str(self.ID) +
               "resumimg state:" +
               str(last_state))
        self.assignedState.resume(last_state)

    def assign(self):
        """ Assign a drone to the user. """
        try:
            self.assignedState.toAssigned()
        except DroneStateTransitionError:
            return False
        else:
            return True

    def checkIfNetworkRunning(self):
        """ Check if the network with the drone is OK. """
        return self.running
        return self.drone._network._netal._running

    def shut_down(self):
        """ Shut down the drone. """
        self.running = False
        try:
            self.assignedState.toShutdown()
        except DroneStateTransitionError as exception:
            return exception.message
        return True
        self.drone.stop()

    def test_thread(self):
        testdrone_logger.info("Start Testdrone %d" % (self.ID))
        while self.running:
            time.sleep(TESTDRONE_UPDATE_PERIOD)
            message = self.update_testdata()
            testdrone_logger.info(message)
        testdrone_logger.info("Exist Testdrone %d" % (self.ID))

    def update_testdata(self):
        """ Update test data. Testdrone only.

        Update battery whenever this function called.
        Also heading to destination.
        """
        # Checki if available.
        if (self.assignedState.getState() == FState.SHUTDOWN or
                self.assignedState.getState() == FState.DISCONNECTED):
            return ("DroneID %d failed to update testdata" % self.ID)

        # Check if moving.
        if self.assignedState.getState() == FState.HEADING or \
                self.assignedState.getState() == FState.RETURNING:
            if not self.destination:
                raise ValueError("No destination")
            desti_la, desti_lo, desti_al = self.destination
            la, lo, al = self.get_location()

            delta_la = desti_la - la
            delta_lo = desti_lo - lo
            delta_al = desti_al - al

            # Not arrived, update location
            if not self.checkArrived():
                start_la, start_lo, start_al = self.start_position
                delta_la = (desti_la - start_la) / 10
                delta_lo = (desti_lo - start_lo) / 10
                delta_al = (desti_al - start_al) / 10
                self.set_location((la + delta_la,
                                   lo + delta_lo,
                                   al + delta_al))

        # Check and update battery.
        if self.battery > 0:
            if self.getAssignedState() == FState.STANDBY or \
                    self.getAssignedState() == FState.ASSIGNED:
                if random.random() < 0.9:
                    return ("DroneID %d update testdata" % self.ID)
            if random.random() < 0.3:
                return ("DroneID %d update testdata" % self.ID)
            self.battery -= 1
            (self.state['common']['CommonState']
                       ['BatteryStateChanged']['percent']) -= 1

        return ("DroneID %d update testdata" % self.ID)

    def update_state(self):
        """ Update drone FSM.

        Chekc if arrived and other state change.
        """
        # Checki if available.
        if (self.assignedState.getState() == FState.SHUTDOWN or
                self.assignedState.getState() == FState.DISCONNECTED):
            return ("DroneID %d failed to update state" % self.ID)

        # Check if moving.
        if self.assignedState.getState() == FState.HEADING or \
                self.assignedState.getState() == FState.RETURNING:
            if not self.destination:
                raise ValueError("No destination")

            if self.assignedState.getState() == FState.RETURNING:
                print ("Returning: ", self.destination, self.get_location())
            # Arrvied, turn dronestate.
            if self.checkArrived():
                try:
                    if self.destination == self.home_position:
                        print ("Drone", self.ID, "Recharging")
                        self.battery = 100
                        (self.state['common']['CommonState']
                         ['BatteryStateChanged']['percent']) = 100
                        try:
                            self.assignedState.toRecharging()
                        except DroneStateTransitionError as exception:
                            print (exception.message)

                        try:
                            self.assignedState.toStandby()
                        except DroneStateTransitionError as exception:
                            print (exception.message)
                    else:
                        self.assignedState.toOccupied()
                except DroneStateTransitionError as exception:
                    print (exception.message)

        return ("DroneID %d update dronestate" % self.ID)

    def checkArrived(self):
        """ Check if drone arrive destination.

        Returns:
            True if arrived, else False. """
        desti_la, desti_lo, desti_al = self.destination
        la, lo, al = self.get_location()
        delta_la = desti_la - la
        delta_lo = desti_lo - lo
        delta_al = desti_al - al
        if (abs(delta_la) < self.altitude_precision and
                abs(delta_lo) < self.GPS_precision and
                abs(delta_al) < self.GPS_precision):
            return True
        else:
            return False

    def get_return_home_delay(self):
        """ Get return home delay time setting. """
        return (self.state['ardrone3']['GPSSettingsState']
                          ['ReturnHomeDelayChanged']['delay'])

    def get_battery(self):
        """ Get battery percentage. """
        if (self.assignedState.getState() == FState.SHUTDOWN or
                self.assignedState.getState() == FState.DISCONNECTED):
            return False
        return self.battery
        return self.drone.get_battery()

    def get_state(self):
        """ Get inner state of the drone. """
        if (self.state):
            return self.state
        filename = DATA_DIR + "state.py"
        if os.path.isfile(filename):
            self.state = dict(readPickle(filename))
        else:
            self.state = dict(self.drone.get_state())
            writePickle(filename, self.state)
        self.set_location((22.735780 + 0.000001 * self.battery,
                           120.286353 + 0.000001 * self.battery,
                           400))
        (self.state['common']['CommonState']
                   ['BatteryStateChanged']['percent']) = self.battery
        return dict(self.state)

    def get_location(self):
        """ Get GPS location of the drone. 500 is unavailable.  """

        altitude = (self.state['ardrone3']['PilotingState']
                              ['GpsLocationChanged']['altitude'])
        latitude = (self.state['ardrone3']['PilotingState']
                    ['GpsLocationChanged']['latitude'])
        longitude = (self.state['ardrone3']['PilotingState']
                               ['GpsLocationChanged']['longitude'])
        return (latitude, longitude, altitude)

    def estimate_nav_time(self,
                          destination=None,
                          currentLoc=None):
        """ Estimation time of navigation. """
        if not destination:
            destination = self.destination
        if not currentLoc:
            currentLoc = self.get_location()
        des_la, des_lo, des_al = destination
        la, lo, al = currentLoc
        tmp = ((des_la - la) * self.GPS2meterRatio) ** 2 + \
              ((des_lo - lo) * self.GPS2meterRatio) ** 2 + \
              (des_al - al) ** 2
        distance = tmp ** 0.5
        navigation_time = distance / self.drone_speed
        return navigation_time

    def set_location(self, destination):
        """ Set self location. Only used for testdrone. """
        la, lo, al = destination
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['altitude']) = al
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['latitude']) = la
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['longitude']) = lo

    def take_picture(self):
        """ Ask drone to take a picture. """
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        return True
        return self.drone.take_picture()

    def get_picture(self):
        """ Get the last taken picture of the drone. """
        # NOTE: May not get the latest one.
        with open(DATA_DIR + "i.jpg", 'rb') as img_file:
            img = StringIO(img_file.read())
        return img

    def start_video(self):
        """ Start video recording. """
        # NOTE: Not yet tested.
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 0
        return True
        return self.drone.record_video(1)

    def stop_video(self):
        """ Stop video recording. """
        # NOTE: Not yet tested.
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 1
        return True
        return self.drone.record_video(0)

    def take_off(self):
        """ Take off. """
        # NOTE: Not yet tested.
        assert(self.assignedState.getState() == FState.STANDBY)
        return True
        return self.drone.take_off()

    def land(self):
        """ Landing. """
        # NOTE: Not yet tested.
        assert(self.assignedState.getState() == FState.RETURNING)
        return True
        return self.drone.land()

    def emergency(self):
        """ Emergenct stop. """
        # NOTE: Not yet tested.
        try:
            self.assignedState.toDisconnected()
        except DroneStateTransitionError as exception:
            return exception.message
        return True
        return self.drone.emergency()

    def navigate(self, destination):
        """ Navigate to given GPS position with specific mode. """
        latitude, longitude, altitude, orientation_mode, heading = destination
        h_la, h_lo, h_al = self.home_position
        del_la = (latitude - h_la) * self.GPS2meterRatio
        del_lo = (longitude - h_lo) * self.GPS2meterRatio
        distance = (del_la ** 2 + del_lo ** 2) ** 0.5
        if (distance > self.navRange or
                altitude > self.navRange or
                altitude < 1):
            return ("Error: navigation out of range, " +
                    "destination - home = (%f, %f) M" %
                    ((latitude - h_la) * self.GPS2meterRatio,
                     (longitude - h_lo) * self.GPS2meterRatio))
        try:
            self.assignedState.toHeading()
        except DroneStateTransitionError as exception:
            return exception.message
        self.start_position = self.get_location()
        self.destination = (latitude, longitude, altitude)
        return ("Navigating")
        return self.drone.move_to(latitude, longitude,
                                  altitude, orientation_mode, heading)

    def navigate_home(self):
        """ Navigate to home position.

        Should turn to recharging state and to standby.
        In Testdrone the procedure is simplified.
        """
        try:
            self.assignedState.toReturning()
        except DroneStateTransitionError as exception:
            return exception.message
        self.start_position = self.get_location()
        self.destination = self.home_position
        self.set_location(self.destination)
        # print (self.update_state())
        return True


if __name__ == '__main__':
    print (__doc__)
