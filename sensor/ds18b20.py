import glob
import time


class DS18B20:
    """
    Manages reading the temperature sensor

    Based on https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
    """

    current = None
    device_file = None

    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        """
        raw results from the sensor
        :return:
        """
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        """
        Reads the current temperature from the sensor, retrying on errors
        :return:
        """
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            print "retry"
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            self.current = float(temp_string) / 1000.0
            return self.current

    def get_current(self):
        """
        :return: float the last temperature reading
        """
        return self.current