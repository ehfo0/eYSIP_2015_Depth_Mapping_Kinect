__author__ = 'aniket'

import freenect
import cv2
import numpy as np
import serial
import time

kernel = np.ones((5,5),np.uint8)
#ser = serial.Serial('/dev/ttyUSB1')

def get_depth():
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    return a

def return_mean(a):
    median = cv2.medianBlur(a,5)
    mediane = cv2.medianBlur(a,5)
    rect = mediane[0:479, 0:639]
    mean = rect.mean()
    return mean

def is_contour_bad(c):
    approx = cv2.approxPolyDP(c,100*cv2.arcLength(c,True),True)
    area = cv2.contourArea(c)
    #print area
    if area > 1 and area < 1000000:
        return True
    else: return False

#ctx = freenect.init()
#dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

#freenect.set_tilt_degs(dev, 15)
#time.sleep(1)

#freenect.set_tilt_degs(dev, 0)
#time.sleep(1)

#freenect.close_device(dev)
i=0
frame=[]
while(True):
    a = get_depth()
    for i in xrange(5):
        a = cv2.morphologyEx(a, cv2.MORPH_OPEN, kernel)

    mean = return_mean(a)

    print mean
    if mean > 230:
        t=1
 #          ser.write("\x38")
    else:
        #frame.append(a)
        i=i+1
        #while(return_mean(get_depth())<232):
        #    t=1
           # ser.write("\x36")

    for i in xrange(2):
        #ret,th3 = cv2.threshold(a,254,255,cv2.THRESH_BINARY)
        th3 = cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,2)
        #cv2.imshow('tree',th3)
        contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #ab = freenect.sync_get_video()[0]
        #cv2.drawContours(a, contours, -1, (0,255,0), 1)

        for c in contours:
            if is_contour_bad(c):
                cv2.drawContours(a, [c], -1, (0,255,0), 1)
        for i in xrange(2):
            a = cv2.morphologyEx(a, cv2.MORPH_OPEN, kernel)






    cv2.imshow('gray',a)
    if cv2.waitKey(1)!=-1:
        #ser.write('\x35')
        #ser.close()
        freenect.Kill
        break

cv2.destroyWindow('gray')
time.sleep(1)
for i in xrange(3):
    #print frame[i]
    time.sleep(3)

cv2.destroyAllWindows()