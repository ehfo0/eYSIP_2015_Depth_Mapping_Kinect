__author__ = 'aniket'
import serial
import numpy as np
from matplotlib import pyplot as plt
import time
import math

#ser = serial.Serial('/dev/ttyUSB0')
plt.ion()
plt.figure()
a = []
b = []
for i in xrange(20):
    a.append(i)
    b.append(math.sin(i*(math.pi/10)))
    plt.plot(a,b)
    plt.draw()
time.sleep(10)