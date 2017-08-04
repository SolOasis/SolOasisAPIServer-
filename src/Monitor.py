""" Class for monitoring connection and status of drones.

May have some bugs for threading control,
especially on Heroku. """
import threading
import time
from loggingConfig import setup_logger, LOG_DIR_TODAY, log_debug
from drones.Drone import FState

# Period for monitor to check state of each drone, in second
DRONE_MONITOR_PERIOD = 1
# Battery minimum for drones to return home.
DRONE_LOW_BATTERY_TH = 20
monitor_log_file = (LOG_DIR_TODAY + '/monitor_' +
                    time.strftime("%Y-%m-%d_%H:%M") + '.log')
"""
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format=('%(asctime)s %(name)-12s ' +
                            '%(levelname)-8s %(message)s'),
                    datefmt='%Y-%m-%d %H:%M',
                    filename=LOG_FILE,
                    filemode='w')
"""
monitor_logger = setup_logger('Monitor', monitor_log_file,
                              shownInConsole=log_debug)


class Monitor:
    """ Monitor to monitor threads of drones. """

    def __init__(self, manager):
        self.all_drones = dict()
        self.threads = dict()
        self.manager = manager
        self.battery_min = DRONE_LOW_BATTERY_TH
        self.lock = threading.RLock()

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
            self.lock.acquire()
            monitor_logger.info("Stopping thread %d" % assignedID)
            self.threads[assignedID].stop()
            self.lock.release()
            self.lock.acquire()
            del self.threads[assignedID]
            monitor_logger.info("Released thread %d" % assignedID)
            self.lock.release()
        if assignedID in self.all_drones:
            del self.all_drones[assignedID]

    def handleDisconnection(self, threadID, last_state):
        """ Tell manager to reconnect a disconnected drone. """
        monitor_logger.info("Handling drone %d disconnection" % threadID)
        state = self.manager.reconnectDrone(threadID, last_state)
        monitor_logger.info("Drone %d Resumed state: %s" % (threadID, state))

    def handleLowBattery(self, threadID):
        """ Tell manager to bring a drone back when battery is low. """
        monitor_logger.info("Handling drone %d low battery" % threadID)
        state = self.manager.navigateHome(threadID)
        monitor_logger.info("..Drone %d low battery to navigateHome state %s" %
                            (threadID, state))

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
        self.logger = monitor_logger

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
        self.logger.info("Starting droneThread %d" % self.threadID)
        self.lock.release()
        battery_false_count = 0
        while not self.stopped.wait(DRONE_MONITOR_PERIOD):
            if self.ifStopped():
                break
            self.lock.acquire()
            self.logger.info("Drone: " + str(self.threadID) +
                             "\tAState: " + self.drone.getAssignedState() +
                             "\t Battery: " + str(self.drone.get_battery()))

            """ Check shut down (should not happen). """
            if self.drone.checkShutdown():
                self.logger.error("Drone shut down wihout releasing thread.")
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
                self.logger.warning("*** Drone %d disconnected %d sec ***" %
                                    (self.threadID, self.disconnectedTime))

                if self.disconnectedTime > self.returnHomeDelay:
                    nav_time = self.drone.estimate_nav_time(
                        destination=self.drone.home_position)
                    # Substract the time drone should have started flying back
                    nav_time -= (self.disconnectedTime - self.returnHomeDelay)
                    if nav_time > 0.1:
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
                    self.logger.warning(self.message)

                assert(self.drone.checkShutdown is not False)
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue
            else:
                self.disconnectedTime = 0

            # """ Update status of the drone. """
            # Done by testdrone thread
            self.message = self.drone.update_state()

            """ Check battery. """
            try:
                battery = self.drone.get_battery()
                if not battery:
                    self.logger.error("Drone %d battery False" % self.threadID)
                    raise IOError("Battery False")
                if battery != self.battery:
                    self.logger.debug("Thread %d alive, battery: %d " %
                                      (self.threadID, battery))
                    self.battery = battery
                if battery <= self.monitor.battery_min:
                    self.message = ("*** Warning: Thread " +
                                    str(self.threadID) +
                                    " Low battery: " +
                                    str(battery) + " ***")
                    self.logger.warning(self.message)
                    self.monitor.handleLowBattery(self.threadID)
                    self.lock.release()
                    continue
            except IOError:
                self.message = (str(self.threadID) + "could not get battery")
                self.logger.error(self.message)
                battery_false_count += 1
                if battery_false_count > 5:
                    battery_false_count = 0
                    last_state = self.drone.setDisconnected()
                    self.monitor.handleDisconnection(self.threadID, last_state)
                    self.lock.release()
                    continue

            """ Check State. """
            try:
                s = self.drone.get_state()
                if s != self.state:
                    self.logger.debug("Thread " + str(self.threadID) +
                                      " alive, state changed")
                    self.state = s
            except:
                self.message = ("DroneID " +
                                self.threadID +
                                str(" could not get state"))
                self.logger.warning(self.message)
                self.drone.setDisconnected()
                last_state = self.drone.setDisconnected()
                self.monitor.handleDisconnection(self.threadID, last_state)
                self.lock.release()
                continue
            self.lock.release()
        self.lock.acquire()
        self.logger.info("Exist droneThread %d" % self.threadID)
        self.lock.release()


if __name__ == '__main__':
    print (__doc__)
