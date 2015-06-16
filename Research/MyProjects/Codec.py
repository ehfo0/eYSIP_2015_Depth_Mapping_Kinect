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
    ret,mask = cv2.threshold(median,254,255,cv2.THRESH_BINARY_INV)
    mask = mask/255
    ab = freenect.sync_get_video()[0]
    ab = cv2.cvtColor(ab, cv2.COLOR_BGR2RGB)
    for i in range(3):
        maske[:,:,i] = mask[:,:]
    maske = maske/255
    abc = np.multiply(ab,maske)
    #print abc
    return abc

def colored():
    a = freenect.sync_get_video()[0]
    return a

while(True):
    cv2.imshow('gray',grayscale())
    #cv2.imshow('color',colored())
    if cv2.waitKey(0) == 'q':
        break

cv2.destroyAllWindows()
