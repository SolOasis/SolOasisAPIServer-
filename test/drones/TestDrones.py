#!/usr/bin/env python
"""
Derived class for Test devices.
"""
import bybop.Bybop_Discovery as Bybop_Discovery
import bybop.Bybop_Device as Bybop_Device
from Drone import Drone, Discovery
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
        self.all_devices_itv = None

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
            self.all_devices_itv = self.all_devices.itervalues()
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
        return self.all_devices

    def connectToDevice(self, assignedID, deviceName=None, deviceType='Bebop'):
        if not len(self.all_devices):
            return False
        if (deviceName):
            device = self.all_devices[deviceName]
        else:
            try:
                device = self.all_devices_itv.next()
                deviceName = Bybop_Discovery.get_name(device)
            except:
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


class BebopDrone(Drone):
    """ Derived class for testing Bebop drones manipulation.
    May have some difference with original Bebop drones"""

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        self.ID = ID
        self.name = name
        self.drone_type = 'Bebop'
        self.state = dict()
        self.running = True
        self.assigned = False
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

    def getInfo(self):
        return self.ID, self.name, self.drone_type, self.assigned

    def setVerbose(self):
        return True
        self.drone.set_verbose(True)

    def assign(self):
        if self.assigned:
            return False
        self.assigned = True
        return True

    def checkIfNetworkRunning(self):
        return self.running
        return self.drone._network._netal._running

    def stop(self):
        self.running = False
        self.assigned = False
        return True
        self.drone.stop()

    def get_battery(self):
        if self.battery > 0:
            self.battery -= 1
            (self.state['common']['CommonState']
                       ['BatteryStateChanged']['percent']) -= 1

        if len(self.state):
            if (self.state['ardrone3']['PilotingState']
                    ['GpsLocationChanged']['latitude']) < 50:
                (self.state['ardrone3']['PilotingState']
                           ['GpsLocationChanged']['latitude']) += 0.005
            if (self.state['ardrone3']['PilotingState']
                    ['GpsLocationChanged']['longitude']) < 150:
                (self.state['ardrone3']['PilotingState']
                           ['GpsLocationChanged']['longitude']) += 0.005
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
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['altitude']) = 400
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['latitude']) = 22.6
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['longitude']) = 120.2
        (self.state['common']['CommonState']
                   ['BatteryStateChanged']['percent']) = self.battery
        return dict(self.state)

    def take_picture(self):
        self.battery -= 1
        return True
        return self.drone.take_picture()

    def get_picture(self):
        with open(DATA_DIR + "i.jpg", 'rb') as img_file:
            img = StringIO(img_file.read())
        return img

    def start_video(self):
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 0
        return True
        return self.drone.record_video(1)

    def stop_video(self):
        self.battery -= 1
        (self.state['ardrone3']['MediaStreamingState']
                   ['VideoEnableChanged']['enabled']) = 1
        return True
        return self.drone.record_video(0)

    def take_off(self):
        return True
        return self.drone.take_off()

    def land(self):
        return True
        return self.drone.land()

    def emergency(self):
        return True
        return self.drone.emergency()

    def navigate(self, destination):
        print ("Going to ", destination)
        latitude, longitude, altitude, orientation_mode, heading = destination
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['altitude']) = altitude
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['latitude']) = latitude
        (self.state['ardrone3']['PilotingState']
                   ['GpsLocationChanged']['longitude']) = longitude
        return True
        return self.drone.move_to(latitude, longitude,
                                  altitude, orientation_mode, heading)

    def navigate_home(self):
        print ("Returning Home .. ")
        self.battery = 100
        (self.state['common']['CommonState']
                   ['BatteryStateChanged']['percent']) = 100
        self.assigned = False
        return True


if __name__ == '__main__':
    print (__doc__)
