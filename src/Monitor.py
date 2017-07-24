""" Class for monitoring connection and status of drones. """
import threading
import time
from drones.Drone import FState

# Period for monitor to check state of each drone, in second
DRONE_MONITOR_PERIOD = 2
# Battery minimum for drones to return home.
DRONE_LOW_BATTERY_TH = 20


class Monitor:
    """ Monitor to monitor threads of drones. """

    def __init__(self, manager):
        self.all_drones = dict()
        self.threads = dict()
        self.manager = manager
        self.battery_min = DRONE_LOW_BATTERY_TH
        self.lock = threading.Lock()

    def addDrone(self, assignedID, drone):
        """ Add a new thread to monitor the drone. """
        self.lock.acquire()
        self.all_drones[assignedID] = drone
        droneThread = DroneThread(assignedID, drone, self)
        self.threads[assignedID] = droneThread
        droneThread.start()
        self.lock.release()

    def releaseDrone(self, assignedID):
        """ Release a drone from monitoring. """
        if assignedID in self.threads:
            self.threads[assignedID].stop()
            del self.threads[assignedID]
            self.lock.acquire()
            print ("Released thread", assignedID)
            self.lock.release()
        if assignedID in self.all_drones:
            del self.all_drones[assignedID]

    def handleDisconnection(self, threadID, last_state):
        """ Tell manager to reconnect a disconnected drone. """
        print ("Handling disconnection")
        self.manager.reconnectDrone(threadID, last_state)

    def handleLowBattery(self, threadID):
        """ Tell manager to bring a drone back when battery is low. """
        print ("Handling low battery")
        self.manager.navigateHome(threadID)


class DroneThread(threading.Thread):
    """ Thread to periodically check connection and status of a drone. """

    def __init__(self, threadID, drone, monitor):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.threadID = threadID
        self.drone = drone
        self.battery = 0
        self.state = dict()
        self.monitor = monitor
        self.lock = monitor.lock

    def stop(self):
        """ Stop the thread. """
        self.stopped.set()

    def ifStopped(self):
        """ Check if the thread is stopped. """
        return self.stopped.isSet()

    def run(self):
        """ Start the thread.
        Check the connection, battery and status periodically with
        every DRONE_MONITOR_PERIOD second."""
        self.lock.acquire()
        print ("Starting droneThread", self.threadID)
        self.lock.release()
        while not self.ifStopped() and \
                not self.stopped.wait(DRONE_MONITOR_PERIOD):
            self.lock.acquire()
            print ("Time: ", time.strftime("%Y-%m-%d %H:%M:%S"),
                   "Drone: ", self.threadID)

            """ Check shut down (should not happen). """
            if self.drone.checkShutdown():
                raise IOError("Drone shut down wihout releasing thread.")
                self.lock.release()
                break

            """ Check connection. """
            if not self.drone.checkIfNetworkRunning():
                print ("Warning: Thread", self.threadID, "Disconnected")
                assert(self.drone.checkShutdown != False)
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue

            """ Update status of the drone. """
            self.drone.update_state()

            """ Check battery. """
            try:
                battery = self.drone.get_battery()
                if not battery:
                    raise IOError("Battery False")
                if battery != self.battery:
                    print ("Thread", self.threadID, "alive, battery:", battery)
                    self.battery = battery
                if battery <= self.monitor.battery_min:
                    print ("Warning: Thread", self.threadID, "Low battery:", battery)
                    self.monitor.handleLowBattery(self.threadID)
                    self.lock.release()
                    continue
            except:
                print (self.threadID, "could not get battery")
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue

            """ Check State. """
            try:
                s = self.drone.get_state()
                if s != self.state:
                    print ("Thread", self.threadID, "alive, state changed")
                    self.state = s
            except:
                print (self.threadID, "could not get state")
                self.drone.setDisconnected()
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue
            self.lock.release()
        self.lock.acquire()
        print ("Exist droneThread", self.threadID)
        self.lock.release()
