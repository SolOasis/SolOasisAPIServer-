#!/usr/bin/env python
"""
Manager class to access SolOasis sun tracker.
"""

from loggingConfig import setup_logger, LOG_DIR, log_debug
manager_log_file = LOG_DIR + '/manager.log'
manager_logger = setup_logger('Manager', manager_log_file,
                              shownInConsole=log_debug)

from SolOasisStation import Station

class Manager:
    """ Manager for SolOasis. """

    def __init__(self):
        stat = Station()
        self.all_stations = dict()
        self.all_stations[0] = stat

    def getStation(self, ID):
        try:
            ID = int(ID)
        except:
            return False
        if not (ID in self.all_stations):
            manager_logger.warning('Unable to get station %d' % ID)
            return False
        return self.all_stations[ID]


    def getStationBattery(self, ID):
        """ Get battery percentage. """
        stat = self.getStation(ID)
        if not stat:
            return False
        return stat.get_battery()

    def getStationGPSLoacton(self, ID):
        """ Get GPS location. """
        stat = self.getStation(ID)
        if not stat:
            return False
        return stat.get_GPS_location()

    def getAllInfo(self):
        return "all"

if __name__ == "__main__":
    print (__doc__)

