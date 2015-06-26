__author__ = 'aniket'


import numpy as np
import matplotlib.mlab as mlab
import math
import cv2
import Kinect
mean = 1000
def haha():
    sigma = 1000
    x = np.linspace(0,2000,2000)
    a = mlab.normpdf(x,mean,sigma)
    a = a/(a[1000])*100
    NewValue = []
    for i in xrange(2000):
        NewValue.append(((a[i] - 60) * 100) / 40)


