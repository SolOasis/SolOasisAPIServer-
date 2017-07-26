import unittest
import time


class TestManagerFunctions(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()

    def test_searchAllDevices(self):
        self.manager.searchAllDevices()
        self.assertEqual(len(self.manager.all_drones),
                         len(self.manager.all_devices))
        self.test_releaseAllDevices()

    def test_releaseAllDevices(self):
        self.manager.releaseAllDevices()
        self.assertEqual(len(self.manager.all_drones), 0)
        self.assertEqual(len(self.manager.all_devices), 0)

    def test_assignDrone(self):
        self.manager.searchAllDevices()
        droneID = self.manager.assignDrone()
        self.assertEqual(droneID, 0)
        droneID = self.manager.assignDrone()
        self.assertEqual(droneID, 1)
        droneID = self.manager.assignDrone()
        self.assertEqual(droneID, 2)
        droneID = self.manager.assignDrone()
        self.assertFalse(droneID)
        self.manager.releaseAllDevices()

    def test_regainDrone(self):
        self.test_releaseAllDevices()
        droneID = 0
        regained = self.manager.regainDrone(droneID)
        self.assertFalse(regained)
        self.manager.searchAllDevices()
        regained = self.manager.regainDrone(droneID)
        self.assertTrue(regained)
        droneID = self.manager.assignDrone()
        self.assertEqual(droneID, 0)
        regained = self.manager.regainDrone(droneID)
        self.assertTrue(regained)
        self.manager.releaseAllDevices()

    def test_getDroneBattery(self):
        droneID = 0
        battery = self.manager.getDroneBattery(droneID)
        self.assertFalse(battery)
        self.assertIsInstance(battery, bool)
        self.manager.searchAllDevices()
        battery = self.manager.getDroneBattery(droneID)
        self.assertIsInstance(battery, int)
        self.assertGreaterEqual(battery, 0)
        droneID = self.manager.assignDrone()
        self.assertEqual(droneID, 0)
        battery = self.manager.getDroneBattery(droneID)
        self.assertIsInstance(battery, int)
        self.assertGreaterEqual(battery, 0)
        self.manager.releaseAllDevices()

    def test_lowBattery(self):
        self.manager.searchAllDevices()
        droneID = self.manager.assignDrone()
        battery = self.manager.getDroneBattery(droneID)
        self.assertIsInstance(battery, int)
        self.assertGreaterEqual(battery, 0)
        for i in range(100):
            self.manager.getDrone(droneID).update_state()
            battery = self.manager.getDroneBattery(droneID)
            self.assertIsInstance(battery, int)
            self.assertGreaterEqual(battery, 0)
            # Need to wait since the monitor only check
            # battery in period of 2 second
            time.sleep(0.02)
        time.sleep(2)

        self.manager.releaseAllDevices()

    def test_disconnection(self):
        self.manager.searchAllDevices()
        droneID = self.manager.assignDrone()
        self.manager.getDrone(droneID).setDisconnected()
        self.manager.getDrone(droneID).running = False
        battery = self.manager.getDroneBattery(droneID)
        self.assertFalse(battery)
        self.assertIsInstance(battery, bool)
        time.sleep(2)
        battery = self.manager.getDroneBattery(droneID)
        self.assertIsInstance(battery, int)
        self.assertGreaterEqual(battery, 0)
        self.manager.releaseAllDevices()

    def test_navigation(self):
        self.manager.searchAllDevices()
        droneID = self.manager.assignDrone()
        destination = (100, 100, 100, 1, 1)
        self.manager.navigate(droneID, destination)
        for i in range(100):
            self.manager.getDrone(droneID).update_state()
            time.sleep(0.02)
        time.sleep(2)
        self.manager.releaseAllDevices()


if __name__ == "__main__":
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from src.Manager import Manager
    unittest.main()
    # from drones.ParrotDrones import ParrotDiscovery as Discovery
