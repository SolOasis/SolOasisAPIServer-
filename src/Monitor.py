import threading
import time

# Period for monitor to check state of each drone, in second
DRONE_MONITOR_PERIOD = 2


class Monitor:

    def __init__(self, manager):
        self.all_drones = dict()
        self.threads = dict()
        self.manager = manager

    def addDrone(self, assignedID, drone):
        self.all_drones[assignedID] = drone
        droneThread = DroneThread(assignedID, drone, self)
        self.threads[assignedID] = droneThread
        droneThread.start()

    def releaseDrone(self, assignedID):
        if assignedID in self.threads:
            self.threads[assignedID].stop()
            print ("Releasing thread", assignedID)
        if assignedID in self.all_drones:
            del self.all_drones[assignedID]

    def handleDisconnection(self, threadID):
        self.manager.reconnectDrone(threadID)


class DroneThread(threading.Thread):

    def __init__(self, threadID, drone, monitor):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.threadID = threadID
        self.drone = drone
        self.battery = 0
        self.state = dict()
        self.monitor = monitor

    def stop(self):
        self.stopped.set()

    def stopped(self):
        return self.stopped.isSet()

    def run(self):
        print ("Starting droneThread", self.threadID)
        while not self.stopped and not self.stopped.wait(DRONE_MONITOR_PERIOD):
            print ("Time: ", time.strftime("%Y-%m-%d %H:%M:%S"),
                   "Drone: ", self.threadID)
            if not self.drone.checkIfNetworkRunning():
                self.monitor.handleDisconnection(self.threadID)
                continue
            try:
                battery = self.drone.get_battery()
                if battery != self.battery:
                    print ("Thread", self.threadID, "alive, battery:", battery)
                    self.battery = battery
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
        print ("Exist droneThread", self.threadID)
