import threading
import time

# Period for monitor to check state of each drone, in second
DRONE_MONITOR_PERIOD = 2
# Battery minimum for drones to return home.
DRONE_LOW_BATTERY_TH = 20


class Monitor:

    def __init__(self, manager):
        self.all_drones = dict()
        self.threads = dict()
        self.manager = manager
        self.battery_min = DRONE_LOW_BATTERY_TH
        self.lock = threading.Lock()

    def addDrone(self, assignedID, drone):
        self.all_drones[assignedID] = drone
        droneThread = DroneThread(assignedID, drone, self)
        self.threads[assignedID] = droneThread
        droneThread.start()

    def releaseDrone(self, assignedID):
        if assignedID in self.threads:
            self.threads[assignedID].stop()
            del self.threads[assignedID]
            print ("Releasing thread", assignedID)
        if assignedID in self.all_drones:
            del self.all_drones[assignedID]

    def handleDisconnection(self, threadID):
        self.manager.reconnectDrone(threadID)

    def handleLowBattery(self, threadID):
        self.manager.navigateHome(threadID)


class DroneThread(threading.Thread):

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
        self.stopped.set()

    def ifStopped(self):
        return self.stopped.isSet()

    def run(self):
        print ("Starting droneThread", self.threadID)
        while not self.ifStopped() and \
                not self.stopped.wait(DRONE_MONITOR_PERIOD):
            self.lock.acquire()
            print ("Time: ", time.strftime("%Y-%m-%d %H:%M:%S"),
                   "Drone: ", self.threadID)
            if not self.drone.checkIfNetworkRunning():
                if self.drone.assigned:
                    self.monitor.handleDisconnection(self.threadID)

                    print ("Warning: Thread", self.threadID, "Disconnected")
                    continue
                else:
                    break
            try:
                battery = self.drone.get_battery()
                if battery != self.battery:
                    print ("Thread", self.threadID, "alive, battery:", battery)
                    self.battery = battery
                if battery <= self.monitor.battery_min:
                    print ("Warning: Thread", self.threadID, "Low battery")
                    self.monitor.handleLowBattery(self.threadID)
            except:
                print (self.threadID, "could not get battery")
                self.stop()
                break

            try:
                s = self.drone.get_state()
                if s != self.state:
                    print ("Thread", self.threadID, "alive, state changed")
                    self.state = s
            except:
                print (self.threadID, "could not get state")
                self.stop()
                break
            self.lock.release()
        print ("Exist droneThread", self.threadID)
