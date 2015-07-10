__author__ = 'aniket'

import freenect
import cv2
import numpy as np

kernel = nfrp.ones((5,5),np.uint8)
freenect.C
def grayscale():
    maske = np.zeros((480,640,3))
    a = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    mask = a == 0
    a[mask] = 8000

    mask1 = a > 1000
    b = freenect.sync_get_video()[0]
    ab = cv2.cvtColor(b, cv2.COLOR_BGR2RGB)
    ab[mask1,:] = 0

    return ab

while(True):
    cv2.imshow('gray',grayscale())
    #cv2.imshow('color',colored())
    if cv2.waitKey(1) != -1:
        break
cv2.destroyAllWindows()
