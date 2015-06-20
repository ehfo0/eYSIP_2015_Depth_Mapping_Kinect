'''
*
*                  ================================
*
*  Author List: Aniket P, Mukesh P
*  Filename: 		edges.py
*  Date:                June 11, 2015
*  Functions:   get_depth()
                return_mean(a)
                contours_return(a,num)
                regular_movement(z)
                doorway_movement(lb,lt,rb,rt,cxr,cxl)
                left_right_lines(contoursright,contoursleft,z)
*  Global Variables:    tp
                        eli
*  Dependent library files:     numpy, freenect, cv2, serial, time
*
*  e-Yantra - An MHRD project under National Mission on Education using
*  ICT(NMEICT)
*
**************************************************************************
*
*
*
'''

import freenect
import cv2
import numpy as np
import serial
import time

kernel = np.ones((5,5),np.uint8)
#ser = serial.Serial('/dev/ttyUSB0')
global tp
tp = 51
global eli
eli = 0


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
#freenect.close_device(dev)
def contours_return(a,num):
    b = np.roll(a,num)
    res = np.subtract(b,a)
    res = cv2.medianBlur(res,5)
    mask = res > 200
    res[mask] = 0
    contours, hierarchy = cv2.findContours(res,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def take_left():
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        middleval = middlearea.mean()
        #ser.write("\x34")
        if middleval > 220:
            return

def take_right():
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        middleval = middlearea.mean()
        #ser.write("\x36")
        if middleval > 220:
            return

def CountZeros(area,th1,th2):
    ret, mask = cv2.threshold(area,th1,th2,cv2.THRESH_BINARY_INV)
    Zeros = cv2.countNonZero(mask)
    return Zeros

def regular_movement(z):
    global tp
    global eli
    middlearea = z[200:479,200:439]
    middleval = middlearea.mean()
    leftarea = z[0:479,0:100]
    rightarea = z[0:479,539:639]
    leftval = leftarea.mean()
    rightval = rightarea.mean()
    leftvals = CountZeros(leftarea,150,255)
    rightvals = CountZeros(rightarea,150,255)
    middleob = CountZeros(middlearea,150,255)
    if eli == 0:
        if middleval > 220 and middleob < 1000:
            print "forward"
            #ser.write("\x38")
            time.sleep(0.1)
        else:
            if leftval > rightval:
                print "left"
                take_left()
            else:
                print "right"
                take_right()
    if leftvals > 1000 or rightvals > 1000:
        if leftvals > rightvals:
                #print "left"
                take_right()
        else:
                #print "right"
                take_left()



def doorway_movement(lb,lt,rb,rt,cxr,cxl):
    global eli
    diffl = lb[1]-lt[1]
    diffr = rb[1]-rt[1]
    if abs(diffl - diffr) < 50 and (cxr - cxl) > 50:
        eli = 1
        mid = (cxr + cxl)/2
        print "haha"
        if mid < 500 and mid > 200:
            print "forward"
            #ser.write("\x38")
        elif mid < 200:
            print "left"
            #ser.write("\x34")
        else:
            print "right"
            #ser.write("\x36")
    else : eli = 0

def left_right_lines(contoursright,contoursleft,z):
    count = 0
    Area = 1000
    ys = 250
    xs = 60
    tempr = 0
    templ = 0
    for c in contoursright:
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
            w = 50
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                pts1 = np.float32([[topmost[0]-w,y1],[topmost[0],y1],[bottommost[0]-w,y2],[bottommost[0],y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                #print meandst
                if meandst > 240:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    tempr+=1
                    rt = topmost
                    rb = bottommost
                    M = cv2.moments(c)
                    cxr = int(M['m10']/M['m00'])
        count+=1
    count = 0
    for c in contoursleft:
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
            w = 50
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                pts1 = np.float32([[topmost[0],y1],[topmost[0]+w,y1],[bottommost[0],y2],[bottommost[0]+w,y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                #print meandst
                if meandst > 240:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    templ+=1
                    lt = topmost
                    lb = bottommost
                    M = cv2.moments(c)
                    cxl = int(M['m10']/M['m00'])
        count+=1
    if templ == 1 and tempr == 1:
        doorway_movement(lb,lt,rb,rt,cxr,cxl)
    return z


while(True):
    np.set_printoptions(threshold=np.nan)
    a = get_depth()
    z = a
    a = cv2.bilateralFilter(a, 10, 50, 100)
    contoursright = contours_return(a,2)
    contoursleft = contours_return(a,-2)
    regular_movement(z)
    linesz = left_right_lines(contoursright,contoursleft,z)
    cv2.imshow('gray',linesz)
    if cv2.waitKey(1)!=-1:
        #ser.write('\x35')
        #ser.close()
        freenect.Kill
        break

cv2.destroyAllWindows()