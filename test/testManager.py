import unittest


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
        self.test_releaseAllDevices()


if __name__ == "__main__":
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from src.Manager import Manager
    unittest.main()
    # from drones.ParrotDrones import ParrotDiscovery as Discovery
