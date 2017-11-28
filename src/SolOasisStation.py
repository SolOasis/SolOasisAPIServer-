""" Station Class """

class Station:

    def __init__(self):
        self.battery = 100
        self.longitude = -79
        self.latitude = 44

    def get_battery(self):
        return self.battery

    def get_GPS_location(self):
        return (self.longitude, self.latitude)

    def update(self, data):
        print (data)
        if ('percentage' in data):
            self.battery = data['percentage']
        if ('longitude' in data):
            self.longitude = data['longitude']
        if ('latitude' in data):
            self.latitude =  data['latitude']
        return True



if __name__ == "__main__":
    print (__doc__)
