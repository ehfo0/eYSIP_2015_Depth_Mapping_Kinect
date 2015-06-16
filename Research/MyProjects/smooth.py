__author__ = 'aniket'

import freenect
import cv2
import numpy as np

kernel = np.ones((5,5),np.uint8)

def grayscale():
    maske = np.zeros((480,640,3))
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    median = cv2.medianBlur(a,5)
    return median

while(True):
    cv2.imshow('gray',grayscale())

cv2.destroyAllWindows()
