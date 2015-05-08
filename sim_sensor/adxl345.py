# simulator for ADXL345 Python library for Raspberry Pi 
#

import numpy
import time
import os

class ADXL345:
    # ADXL345 constants
    EARTH_GRAVITY_MS2 = 9.80665
    SCALE_MULTIPLIER = 0.004
    SIMULATION_FILENAME = 'simulator_data/example_night.csv'

    def __init__(self, address=0x53):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               self.SIMULATION_FILENAME),'r') as sim_file:
            (self.t,self.x,self.y,self.z)=numpy.loadtxt(sim_file,
                delimiter=',',unpack=True)
        self.time_offset=self.t[0]-time.time()

    def enableMeasurement(self):
        pass

    def setBandwidthRate(self, rate_flag):
        pass

    # set the measurement range for 10-bit readings
    def setRange(self, range_flag):
        pass

    # returns the current reading from the sensor for each axis
    #
    # parameter gforce:
    #    False (default): result is returned in m/s^2
    #    True           : result is returned in gs
    def getAxes(self, gforce=False):

        cur_epoch_time=time.time()
        t_search=cur_epoch_time+self.time_offset
        index=numpy.searchsorted(self.t,t_search)
        x=self.x[index]
        y=self.y[index]
        z=self.z[index]

        if gforce == False:
            x = x * self.EARTH_GRAVITY_MS2
            y = y * self.EARTH_GRAVITY_MS2
            z = z * self.EARTH_GRAVITY_MS2

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        return {"x": x, "y": y, "z": z}


if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output 
    # the current readings
    adxl345 = sim_ADXL345()

    axes = adxl345.getAxes(True)
    print "ADXL345 on address 0x%x:" % (adxl345.address)
    print "   x = %.3fG" % (axes['x'])
    print "   y = %.3fG" % (axes['y'])
    print "   z = %.3fG" % (axes['z'])
