""" Class for monitoring connection and status of drones. """
import threading
import time
from drones.Drone import FState

# Period for monitor to check state of each drone, in second
DRONE_MONITOR_PERIOD = 1
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
        state = self.manager.reconnectDrone(threadID, last_state)
        print ("Resumed state: " + str(state))

    def handleLowBattery(self, threadID):
        """ Tell manager to bring a drone back when battery is low. """
        print ("Handling low battery")
        state = self.manager.navigateHome(threadID)
        print (state)

    def getThreadMessage(self, threadID):
        return self.threads[threadID].getMessage()


class DroneThread(threading.Thread):
    """ Thread to periodically check connection and status of a drone. """

    def __init__(self, threadID, drone, monitor):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.threadID = threadID
        self.drone = drone
        self.battery = 0
        self.disconnectedTime = 0
        self.message = ""
        self.returnHomeDelay = self.drone.get_return_home_delay()
        self.state = dict()
        self.monitor = monitor
        self.lock = monitor.lock

    def getMessage(self):
        """ Get thread message like warning. """
        return self.message

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
            print ("Time: " + time.strftime("%Y-%m-%d %H:%M:%S") +
                   "\tDrone: " + str(self.threadID) +
                   "\tAState: " + self.drone.getAssignedState() +
                   "\t Battery: " + str(self.drone.get_battery()))

            """ Check shut down (should not happen). """
            if self.drone.checkShutdown():
                raise IOError("Drone shut down wihout releasing thread.")
                self.lock.release()
                break

            """ Check connection.
            After disconnected for returnHomeDelay second,
            the drone should return by itself. """
            if ((not self.drone.checkIfNetworkRunning()) or
                    self.drone.getAssignedState == FState.DISCONNECTED):
                self.disconnectedTime += DRONE_MONITOR_PERIOD
                self.message = ("*** Warning: Thread", self.threadID,
                                "Disconnected",
                                self.disconnectedTime, "s ***")
                print (self.message)
                if self.disconnectedTime > self.returnHomeDelay:
                    nav_time = self.drone.estimate_nav_time(
                        destination=self.drone.home_position)
                    # Substract the time drone should have started flying back
                    nav_time -= (self.disconnectedTime - self.returnHomeDelay)
                    if nav_time > 0:
                        self.message = ("*** Warning: Disconnected thread "
                                        "%d should return home automatically "
                                        "within %f second. ***"
                                        % (self.threadID, nav_time))
                    else:
                        self.message = ("*** Warning: Disconnected thread "
                                        "%d should have returned home "
                                        "automatically %f seconds ago."
                                        "Please check if it is crashed. ***"
                                        % (self.threadID, -nav_time))
                    print (self.message)

                assert(self.drone.checkShutdown is not False)
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue
            else:
                self.disconnectedTime = 0

            """ Update status of the drone. """
            self.message = self.drone.update_state()

            """ Check battery. """
            try:
                battery = self.drone.get_battery()
                if abs(battery - self.battery) > 10 and self.battery > 0:
                    print ("Thread " + str(self.threadID)
                           + " get_battery problem," +
                           "battery (%d/%d): " %
                           (battery, self.battery))
                    time.sleep(1)
                    self.lock.release()
                    continue

                if not battery:
                    raise IOError("Battery False")
                if battery != self.battery:
                    print ("Thread " + str(self.threadID)
                           + " alive, battery: " + str(battery))
                    self.battery = battery
                if battery <= self.monitor.battery_min:
                    self.message = ("*** Warning: Thread " +
                                    str(self.threadID) +
                                    " Low battery: " +
                                    str(battery) + " ***")
                    print (self.message)
                    self.monitor.handleLowBattery(self.threadID)
                    self.lock.release()
                    continue
            except IOError:
                self.message = (str(self.threadID) + "could not get battery")
                print (self.message)

                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue

            """ Check State. """
            try:
                s = self.drone.get_state()
                if s != self.state:
                    print ("Thread " + str(self.threadID) +
                           " alive, state changed")
                    self.state = s
            except:
                self.message = ("DroneID " +
                                self.threadID +
                                str(" could not get state"))
                print (self.message)
                self.drone.setDisconnected()
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue
            self.lock.release()
        self.lock.acquire()
        print ("Exist droneThread", self.threadID)
        self.lock.release()
