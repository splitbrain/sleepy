import sim_sensor as sensor
import time

adxl345 = sensor.ADXL345()
    

while True:
    try:
        axes = adxl345.getAxes(True)
        print "%.2f,%.3f,%.3f,%.3f" % (
            time.time(),
            axes['x'],
            axes['y'],
            axes['z']
        )
    except:
        pass
    time.sleep(0.5)
