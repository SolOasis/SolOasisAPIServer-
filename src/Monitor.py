import threading


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
        self.threadID = threadID
        self.drone = drone
        self.battery = 0
        self.monitor = monitor

    def run(self):
        print ("Starting droneThread", self.threadID)
        alive = True
        while alive:
            try:
                battery = self.drone.get_battery()
                if battery != self.battery:
                    print ("Thread", self.threadID, "alive, battery:", battery)
                    self.battery = battery
            except:
                print (self.threadID, "could not get battery")
                alive = False
            else:
                alive = self.drone.checkIfNetworkRunning()
        print ("Exist droneThread", self.threadID)
        self.monitor.handleDisconnection(self.threadID)
