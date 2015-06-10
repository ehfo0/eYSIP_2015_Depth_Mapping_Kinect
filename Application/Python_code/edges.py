__author__ = 'aniket'

import freenect
import cv2
import numpy as np
import serial
import time
from matplotlib import pyplot as plt

kernel = np.ones((5,5),np.uint8)
#ser = serial.Serial('/dev/ttyUSB1')

def get_depth():
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    return a

def return_mean(a):
    mediane = cv2.medianBlur(a,5)
    rect = mediane[0:479, 0:639]
    mean = rect.mean()
    return mean


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
    np.set_printoptions(threshold=np.nan)
    a = get_depth()
    a = cv2.bilateralFilter(a, 10, 50, 100)
    original = a
    mean = return_mean(a)
    b = np.roll(a,2)
    c = np.roll(a,-2)
    res = np.subtract(b,a)
    resc = np.subtract(c,a)
    res = np.multiply(res,255)
    resc = np.multiply(resc, 255)
    res = cv2.medianBlur(res,5)
    resc = cv2.medianBlur(resc, 5)
    if mean > 230:
        t=1
 #          ser.write("\x38")
    else:
        #frame.append(a)
        i=i+1
        #while(return_mean(get_depth())<232):
        #    t=1
            # ser.write("\x36")
    ret,th3 = cv2.threshold(res,50,255,cv2.THRESH_BINARY)
    ret,th2 = cv2.threshold(resc,50,255,cv2.THRESH_BINARY)
    count = 0
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contoursc, hierarchy = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    Area = 1000
    ys = 250
    xs = 60
    for c in contours:
        if(cv2.contourArea(c)>Area):
            #cv2.drawContours(original, contours, count, (128,255,0), 3)
            leftmost = tuple(c[c[:,:,0].argmin()][0])
            rightmost = tuple(c[c[:,:,0].argmax()][0])
            topmost = tuple(c[c[:,:,1].argmin()][0])
            bottommost = tuple(c[c[:,:,1].argmax()][0])
            x1 = leftmost[0]
            x2 = rightmost[0]
            y1 = topmost[1]
            y2 = bottommost[1]
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                cv2.line(original,topmost,bottommost,(0,255,0),5)
        count+=1
    count = 0
    for c in contoursc:
        if(cv2.contourArea(c)>Area):
            #cv2.drawContours(original, contoursc, count, (128,255,0), 3)
            leftmost = tuple(c[c[:,:,0].argmin()][0])
            rightmost = tuple(c[c[:,:,0].argmax()][0])
            topmost = tuple(c[c[:,:,1].argmin()][0])
            bottommost = tuple(c[c[:,:,1].argmax()][0])
            x1 = leftmost[0]
            x2 = rightmost[0]
            y1 = topmost[1]
            y2 = bottommost[1]
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                cv2.line(original,topmost,bottommost,(0,255,0),5)
        count+=1

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
    time.sleep(1)

cv2.destroyAllWindows()