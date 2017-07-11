#!/usr/bin/env python
"""
Derived class for Parrot devices.
"""
import bybop.Bybop_Discovery as Bybop_Discovery
import bybop.Bybop_Device as Bybop_Device
from Drone import Drone, Discovery

from ftplib import FTP
from StringIO import StringIO


class ParrotDiscovery(Discovery):

    def __init__(self):
        self.d2c_port = 54321
        self.controller_type = "PC"
        self.controller_name = "bybop shell"
        self.discovery = None
        self.all_devices = None
        self.all_devices_itv = None

    def searchAllDevices(self):
        print ('Searching for devices')
        self.discovery = Bybop_Discovery.Discovery(
                Bybop_Discovery.DeviceID.ALL)
        self.discovery.wait_for_change()
        self.all_devices = self.discovery.get_devices()
        self.all_devices_itv = self.all_devices.itervalues()
        print (self.all_devices)
        self.discovery.stop()
        if not self.all_devices:
            print ("Error: No device found.")
            return False
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

    def __init__(self, ID, name, device, d2c_port,
                 controller_type, controller_name):
        self.ID = ID
        self.name = name
        self.state = None
        self.assigned = False
        self.drone = Bybop_Device.create_and_connect(
                device,
                d2c_port,
                controller_type,
                controller_name)

    def getInfo(self):
        return self.ID, self.name, self.assigned

    def setVerbose(self):
        self.drone.set_verbose(True)

    def assign(self):
        if self.assigned:
            return False
        self.assigned = True
        return True

    def checkIfNetworkRunning(self):
        return self.drone._network._netal._running

    def stop(self):
        self.drone.stop()

    def get_battery(self):
        return self.drone.get_battery()

    def get_state(self):
        self.state = self.drone.get_state()
        return self.state

    def take_picture(self):
        return self.drone.take_picture()

    def get_picture(self):
        # return self.drone.get_picture()
        # state = self.drone._state.get_value(
        # 'ardrone3.MediaRecordState.PictureStateChangedV2')
        ftp = FTP("192.168.42.1")
        ftp.login()
        ftp.cwd("internal_000/Bebop_Drone/media")
        ls = []
        ftp.retrlines('LIST', ls.append)

        for entry in reversed(ls):
            # entry = ls[i]
            if entry.split('.')[-1] == 'jpg':
                filename = entry.split(' ')[-1]
                print (filename)
                if (filename.split('_')[2][0:4] == '2017'):
                    r = StringIO()
                    ftp.retrbinary('RETR ' + filename, r.write)
                    return r
        return False

    def start_video(self):
        return self.drone.record_video(1)

    def stop_video(self):
        return self.drone.record_video(0)

    def take_off(self):
        return self.drone.take_off()

    def land(self):
        return self.drone.land()

    def emergency(self):
        return self.drone.emergency()

    def navigate(self, destination):
        print ("Going to ", destination)
        latitude, longitude, altitude, orientation_mode, heading = destination
        return self.drone.move_to(latitude, longitude,
                                  altitude, orientation_mode, heading)


if __name__ == '__main__':
    print (__doc__)
