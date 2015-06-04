__author__ = 'aniket'

import serial
import time

ser = serial.Serial('/dev/ttyUSB0')
ser.write("\x36")   #robot moves forward
time.sleep(2)
ser.write("\x35")   #robot stops
ser.close()
