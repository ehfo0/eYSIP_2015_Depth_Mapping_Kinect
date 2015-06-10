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

def is_contour_bad(c,num):
    approx = cv2.approxPolyDP(c,1000*cv2.arcLength(c,True),True)
    area = cv2.contourArea(c)
    #print area
    if area > num and area < 10000000:
        return True
    else: return False

#ctx = freenect.init()
#dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

#freenect.set_tilt_degs(dev, 20)
#time.sleep(1)

#freenect.set_tilt_degs(dev, 0)
#time.sleep(1)

#freenect.close_device(dev)
i=0
frame=[]
while(True):
    np.set_printoptions(threshold=np.nan)

a = get_depth()
    for i in xrange(5):
        a = cv2.morphologyEx(a, cv2.MORPH_OPEN, kernel)
    original = a
    mean = return_mean(a)

    #print mean
    if mean > 230:
        t=1
 #          ser.write("\x38")
    else:
        #frame.append(a)
        i=i+1
        #while(return_mean(get_depth())<232):
        #    t=1
            # ser.write("\x36")
    num = 1
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    a = clahe.apply(a)

    #ret,th3 = cv2.threshold(a,254,255,cv2.THRESH_BINARY)
    th3 = cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    #cv2.imshow('tree',th3)
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #ab = freenect.sync_get_video()[0]
    #cv2.drawContours(a, contours, -1, (0,255,0), 1)
    for c in contours:
        if is_contour_bad(c,num):
            cv2.drawContours(a, [c], -1, (0,255,0), 1)
    for i in xrange(2):
        a = cv2.morphologyEx(a, cv2.MORPH_OPEN, kernel)
    num = num * 1000
    th3 = cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if is_contour_bad(c,num):
            cv2.drawContours(a, [c], -1, (0,255,0), 1)
    for i in xrange(2):
        a = cv2.morphologyEx(a, cv2.MORPH_OPEN, kernel)
    x = 0
    for i in xrange(64):
        count = a[:,x:x+9]
        NonZeros = cv2.countNonZero(count)
        Zeros = 4800 - NonZeros
        if Zeros > 2000:
            y = 0
            yippee = 0
            for j in xrange(48):
                dabba = a[y:y+9,x:x+9]
                NonZeros = cv2.countNonZero(dabba)
                Zeros = 100 - NonZeros
                if Zeros > 25:
                    yippee = yippee + 1
                else:
                    yippee = 0
                if yippee > 5:
                    cv2.line(a,(y,y+9),(x,x+9),(0,255,0),3)
                y = y+10
        x = x+10

    #ret,th3 = cv2.threshold(a,0,255,cv2.THRESH_BINARY)
    #cv2.line(th3,(x1,y1),(x2,y2),(0,0,255),2)
    #hist = cv2.calcHist([a],[0],None,[256],[0,256])

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