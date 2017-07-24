#!/usr/bin/env python
"""
Derived class for Test devices.
"""
import bybop.Bybop_Discovery as Bybop_Discovery
import bybop.Bybop_Device as Bybop_Device
from Drone import Drone, Discovery, DroneStateMachine, FState
import pickle
import os
import copy
from StringIO import StringIO

print (os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + '/../data/'


def readPickle(filename):
    """ Read from the testing data. """
    with open(filename, 'rb') as read_file:
        fileContent = pickle.load(read_file)
    print ("Read pickle from %s" % filename)
    return fileContent


def writePickle(filename, content):
    """ Write the testing data. """
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
        #Record connected devices,
        #(device_name: connected ID or "disconnected")
        self.all_devices_connection = dict()

    def searchAllDevices(self):
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

    def reconnectToDevice(self, assignedID):
        """ Reconnect to given divice.
        Used by mananger when disconnected. """
        for key, value in self.all_devices_connection.items():
            if value == assignedID:
                deviceName = key
                drone = self.connectToDevice(assignedID, deviceName)
                return drone
        return False


class BebopDrone(Drone):
    """ Derived class for testing Bebop drones manipulation.
    May have some difference with original Bebop drones"""

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        self.ID = ID
        self.name = name
        self.drone_type = 'Bebop'
        self.state = dict()
        self.destination = None
        self.running = True
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

    def getInfo(self):
        return self.ID, self.name, self.drone_type, self.assignedState

    def setVerbose(self):
        return True
        self.drone.set_verbose(True)

    def checkShutdown(self):
        return (self.assignedState.getState() == FState.SHUTDOWN)

    def setDisconnected(self):
        """ Turn to disconnected state and
        return last_state for reconnection. """
        last_state = self.assignedState.getState()
        self.assignedState.toDisconnected()
        return last_state

    def resumeState(self, last_state):
        """ Used after reconnection. """
        print (":::::::::::::::resumimg state:", last_state)
        self.assignedState.resume(last_state)

    def assign(self):
        try:
            self.assignedState.toAssigned()
        except:
            return False
        else:
            return True

    def checkIfNetworkRunning(self):
        return self.running
        return self.drone._network._netal._running

    def shut_down(self):
        self.running = False
        self.assignedState.toShutdown()
        return True
        self.drone.stop()

    def update_state(self):
        """ Update inner state.
        Testdrones update battery whenever this function called.
        Also heading to destination.
        """
        if (self.assignedState.getState() == FState.SHUTDOWN or \
                self.assignedState.getState() == FState.DISCONNECTED):
            return False
        if self.battery > 0:
            self.battery -= 1
            (self.state['common']['CommonState']
                       ['BatteryStateChanged']['percent']) -= 1

        if len(self.state):
            if self.assignedState.getState() == FState.HEADING:
                if self.destination != self.get_location():
                    if not self.destination:
                        return
                    dla, dlo, dal = self.destination
                    la, lo, al = self.get_location()
                    self.set_location(la + (dla - la) / 100,
                                      lo + (dlo - lo) / 100,
                                      al + (dal - al) / 100)
                else:
                    self.assignedState.toOccupied()

    def get_battery(self):
        if (self.assignedState.getState() == FState.SHUTDOWN or \
                self.assignedState.getState() == FState.DISCONNECTED):
            return False
        return self.battery
        return self.drone.get_battery()

    def get_state(self):
        if (self.state):
            return self.state
        filename = DATA_DIR + "state.py"
        if os.path.isfile(filename):
            self.state = dict(readPickle(filename))
        else:
            self.state = dict(self.drone.get_state())
            writePickle(filename, self.state)
        self.set_location(22.6, 120.2, 400)
        (self.state['common']['CommonState']
                   ['BatteryStateChanged']['percent']) = self.battery
        return dict(self.state)

    def get_location(self):

        altitude = (self.state['ardrone3']['PilotingState']
                              ['GpsLocationChanged']['altitude'])
        latitude = (self.state['ardrone3']['PilotingState']
                             ['GpsLocationChanged']['latitude'])
        longitude = (self.state['ardrone3']['PilotingState']
                               ['GpsLocationChanged']['longitude'])
        return (latitude, longitude, altitude)

    def set_location(self, la, lo, al):
        """ Set self location. Only used for testdrone. """
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['altitude']) = al
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['latitude']) = la
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['longitude']) = lo

    def take_picture(self):
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        return True
        return self.drone.take_picture()

    def get_picture(self):
        with open(DATA_DIR + "i.jpg", 'rb') as img_file:
            img = StringIO(img_file.read())
        return img

    def start_video(self):
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 0
        return True
        return self.drone.record_video(1)

    def stop_video(self):
        assert(self.assignedState.getState() == FState.OCCUPIED)
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 1
        return True
        return self.drone.record_video(0)

    def take_off(self):
        assert(self.assignedState.getState() == FState.STANDBY)
        self.assignedState.toHeading()
        return True
        return self.drone.take_off()

    def land(self):
        assert(self.assignedState.getState() == FState.RETURNING)
        self.assignedState.toRecharging()
        return True
        return self.drone.land()

    def emergency(self):
        self.assignedState.toDisconnected()
        return True
        return self.drone.emergency()

    def navigate(self, destination):
        print ("Going to ", destination)
        self.assignedState.toHeading()
        latitude, longitude, altitude, orientation_mode, heading = destination
        self.destination = (latitude, longitude, altitude)
        return True
        return self.drone.move_to(latitude, longitude,
                                  altitude, orientation_mode, heading)

    def navigate_home(self):
        """ Navigate to home position.
        Should turn to recharging state and to standby.
        In Testdrone the procedure is simplified.
        """
        self.assignedState.toReturning()
        print ("Returning Home .. ")
        self.battery = 100
        if len(self.state):
            (self.state['common']['CommonState']
                       ['BatteryStateChanged']['percent']) = 100
        self.assignedState.toRecharging()
        self.assignedState.toStandby()
        return True


if __name__ == '__main__':
    print (__doc__)
