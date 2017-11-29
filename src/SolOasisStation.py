""" Station Class """

class Station:

    def __init__(self):

        self.Hour = None
        self.Minutes = None
        self.Seconds = None
        self.Day  = None
        self.Month  = None
        self.Year  = None
        self.Latitude  = None
        self.Longitude  = None
        self.Altitude  = None
        self.PanelAvgVoltage  = None
        self.PanelAvgCurrent  = None
        self.PanelCurrPower  = None
        self.PanelEnergy  = None
        self.BatteryAvgVoltage  = None
        self.BatteryAvgCurrent  = None
        self.BatteryCurrPower  = None
        self.BatteryEnergy  = None
        self.BatteryPercentage  = None
        self.ConverterAvgVoltage  = None
        self.ConverterAvgCurrent  = None
        self.ConverterCurrPower  = None
        self.ConverterEnergy  = None
        self.Azimuth  = None
        self.Elevation  = None
        self.Zenith  = None
        self.Sunrise  = None
        self.Sunset  = None
        self.JulianDay  = None
        self.CompassDegrees  = None

    def get_battery(self):
        return self.battery

    def get_GPS_location(self):
        return (self.longitude, self.latitude)

    def get_all_info(self):
        info = dict()
        info['Hour'] = self.Hour
        info['Minutes'] = self.Minutes
        info['Seconds'] = self.Seconds
        info['Day'] = self.Day
        info['Month'] = self.Month
        info['Year'] = self.Year
        info['Latitude'] = self.Latitude
        info['Longitude'] = self.Longitude
        info['Altitude'] = self.Altitude
        info['PanelAvgVoltage'] = self.PanelAvgVoltage
        info['PanelAvgCurrent'] = self.PanelAvgCurrent
        info['PanelCurrPower'] = self.PanelCurrPower
        info['PanelEnergy'] = self.PanelEnergy
        info['BatteryAvgVoltage'] = self.BatteryAvgVoltage
        info['BatteryAvgCurrent'] = self.BatteryAvgCurrent
        info['BatteryCurrPower'] = self.BatteryCurrPower
        info['BatteryEnergy'] = self.BatteryEnergy
        info['BatteryPercentage'] = self.BatteryPercentage
        info['ConverterAvgVoltage'] = self.ConverterAvgVoltage
        info['ConverterAvgCurrent'] = self.ConverterAvgCurrent
        info['ConverterCurrPower'] = self.ConverterCurrPower
        info['ConverterEnergy'] = self.ConverterEnergy
        info['Azimuth'] = self.Azimuth
        info['Elevation'] = self.Elevation
        info['Zenith'] = self.Zenith
        info['Sunrise'] = self.Sunrise
        info['Sunset'] = self.Sunset
        info['JulianDay'] = self.JulianDay
        info['CompassDegrees'] = self.CompassDegrees
        return info

    def update(self, data):
        if ('BatteryPercentage' in data):
            self.BatteryPercentage = data['BatteryPercentage']
        if ('Longitude' in data):
            self.Longitude = data['Longitude']
        if ('Latitude' in data):
            self.Latitude =  data['Latitude']
        if ('Hour' in data):
            self.Hour = data['Hour']
        if ('Minutes' in data):
            self.Minutes = data['Minutes']
        if ('Seconds' in data):
            self.Seconds = data['Seconds']
        if ('Day ' in data):
            self.Day  = data['Day ']
        if ('Month ' in data):
            self.Month  = data['Month ']
        if ('Year ' in data):
            self.Year  = data['Year ']
        if ('Latitude ' in data):
            self.Latitude  = data['Latitude ']
        if ('Longitude ' in data):
            self.Longitude  = data['Longitude ']
        if ('Altitude ' in data):
            self.Altitude  = data['Altitude ']
        if ('PanelAvgVoltage ' in data):
            self.PanelAvgVoltage  = data['PanelAvgVoltage ']
        if ('PanelAvgCurrent ' in data):
            self.PanelAvgCurrent  = data['PanelAvgCurrent ']
        if ('PanelCurrPower ' in data):
            self.PanelCurrPower  = data['PanelCurrPower ']
        if ('PanelEnergy ' in data):
            self.PanelEnergy  = data['PanelEnergy ']
        if ('BatteryAvgVoltage ' in data):
            self.BatteryAvgVoltage  = data['BatteryAvgVoltage ']
        if ('BatteryAvgCurrent ' in data):
            self.BatteryAvgCurrent  = data['BatteryAvgCurrent ']
        if ('BatteryCurrPower ' in data):
            self.BatteryCurrPower  = data['BatteryCurrPower ']
        if ('BatteryEnergy ' in data):
            self.BatteryEnergy  = data['BatteryEnergy ']
        if ('BatteryPercentage ' in data):
            self.BatteryPercentage  = data['BatteryPercentage ']
        if ('ConverterAvgVoltage ' in data):
            self.ConverterAvgVoltage  = data['ConverterAvgVoltage ']
        if ('ConverterAvgCurrent ' in data):
            self.ConverterAvgCurrent  = data['ConverterAvgCurrent ']
        if ('ConverterCurrPower ' in data):
            self.ConverterCurrPower  = data['ConverterCurrPower ']
        if ('ConverterEnergy ' in data):
            self.ConverterEnergy  = data['ConverterEnergy ']
        if ('Azimuth ' in data):
            self.Azimuth  = data['Azimuth ']
        if ('Elevation ' in data):
            self.Elevation  = data['Elevation ']
        if ('Zenith ' in data):
            self.Zenith  = data['Zenith ']
        if ('Sunrise ' in data):
            self.Sunrise  = data['Sunrise ']
        if ('Sunset ' in data):
            self.Sunset  = data['Sunset ']
        if ('JulianDay ' in data):
            self.JulianDay  = data['JulianDay ']
        if ('CompassDegrees ' in data):
            self.CompassDegrees  = data['CompassDegrees ']
        return True



if __name__ == "__main__":
    print (__doc__)
