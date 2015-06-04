__author__ = 'aniket'

import freenect
import cv2
import numpy as np

kernel = np.ones((5,5),np.uint8)


def grayscale():
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    median = cv2.medianBlur(a,5)
    ret,thresh = cv2.threshold(median,254,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #ab = freenect.sync_get_video()[0]
    img = cv2.drawContours(median, contours, -1, (0,255,0), 3)
    return median

while(True):
    cv2.imshow('gray',grayscale())
    if cv2.waitKey(10) == 'a':
        break

cv2.destroyAllWindows()
