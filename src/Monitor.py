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

    def handleDisconnection(self, threadID):
        self.manager.regainDrone(threadID)
        del self.threads[threadID]
        print ("Delete thread", threadID, ", regain the drone")


class DroneThread(threading.Thread):

    def __init__(self, threadID, drone, monitor):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.threadID = threadID
        self.drone = drone
        self.battery = 0
        self.state = dict()
        self.monitor = monitor

    def run(self):
        print ("Starting droneThread", self.threadID)
        alive = True
        while alive and not self.stopped.wait(DRONE_MONITOR_PERIOD):
            print ("Time: ", time.strftime("%Y-%m-%d %H:%M:%S"),
                   "Drone: ", self.threadID)
            try:
                battery = self.drone.get_battery()
                if battery != self.battery:
                    print ("Thread", self.threadID, "alive, battery:", battery)
                    self.battery = battery
            except:
                print (self.threadID, "could not get battery")
                alive = False
                break

            try:
                s = self.drone.get_state()
                if s != self.state:
                    print ("Thread", self.threadID, "alive, state:", s)
                    self.state = s
            except:
                print (self.threadID, "could not get state")
                alive = False
                break
            alive = self.drone.checkIfNetworkRunning()
        print ("Exist droneThread", self.threadID)
        self.monitor.handleDisconnection(self.threadID)
