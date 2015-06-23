__author__ = 'aniket'

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import math
import cv2
mean = 1000

sigma = 1000
x = np.linspace(0,2000,2000)
a = mlab.normpdf(x,mean,sigma)
a = a/(a[1000])*100
NewValue = []
for i in xrange(2000):
    NewValue.append(((a[i] - 60) * 100) / 40)
print NewValue[450]

plt.show()