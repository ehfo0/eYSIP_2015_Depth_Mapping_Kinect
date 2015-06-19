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
ser = serial.Serial('/dev/ttyUSB0')
global eli
eli = 0
global flag
flag = 0
global wall
wall = 2


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
    res = np.multiply(res,255)
    res = cv2.medianBlur(res,5)
    ret,th3 = cv2.threshold(res,50,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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

def go_forward():
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        middleval = middlearea.mean()
        ser.write("\x38")
        if middleval > 220:
            return

def CountZeros(area,th1,th2):
    ret, mask = cv2.threshold(area,th1,th2,cv2.THRESH_BINARY_INV)
    Zeros = cv2.countNonZero(mask)
    return Zeros

def regular_movement(z):
    global tp
    global eli
    global wall
    middlearea = z[200:479,200:439]
    leftarea = z[0:479,0:100]
    rightarea = z[0:479,539:639]
    leftvals = CountZeros(leftarea,170,255)
    rightvals = CountZeros(rightarea,170,255)
    middleob = CountZeros(middlearea,150,255)
    if wall == 2:
        if rightvals > leftvals:
            wall = 0
        else: wall = 1
    else :
        print "forward"
        #ser.write("\x38")
    if eli == 0:
        if wall == 0:
            if leftvals < 1000:
                while(1):
                    z = get_depth()
                    leftarea = z[0:479,0:100]
                    leftvals = CountZeros(leftarea,150,255)
                    if leftvals > 1000:
                        break
                    else:
                        print "left"
                        #ser.write("\x34")
            if middleob < 1000:
                print "forward"
                #ser.write("\x38")
                time.sleep(0.1)
            else:
                print "right"
                take_right()
        else :
            if rightvals < 1000:
                while(1):
                    z = get_depth()
                    rightarea = z[0:479,0:100]
                    rightvals = CountZeros(rightarea,150,255)
                    if rightvals > 1000:
                        break
                    else:
                        print "right"
                        #ser.write("\x36")
            if middleob < 1000:
                print "forward"
                #ser.write("\x38")
                time.sleep(0.1)
            else:
                print "left"
                take_left()

    if eli == 2:
        if middleob < 1000:
            print "forward"
            #ser.write("\x38")
            time.sleep(0.1)
        else:
            if leftvals > rightvals:
                print "right"
                take_right()
            else:
                print "left"
                take_left()

def doorway_movement(lb,lt,rb,rt,cxr,cxl):
    global eli
    global flag
    diffl = lb[1]-lt[1]
    diffr = rb[1]-rt[1]
    if abs(diffl - diffr) < 150 and ((cxr - cxl) > 50 and (cxr - cxl ) < 400):
        #ser.write("\x37")
        time.sleep(0.05)
        #ser.write("\x39")
        eli = 2
        flag = 1
        mid = (cxr + cxl)/2
        cv2.line(z,lt,lb,(128,255,0),10)
        cv2.line(z,rt,rb,(128,255,0),10)
        if mid < 439 and mid > 200:
            print "forward"
            #ser.write("\x38")
        elif mid < 200:
            print "left"
            #ser.write("\x34")
        else:
            print "right"
            #ser.write("\x36")
    else :
        if flag == 0:
            eli = 0
        else: eli = 2

def potential_rightedge(c):
    Area = 1000
    ys = 250
    xs = 60
    if(cv2.contourArea(c)>Area):
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
                if meandst > 240:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    rt = topmost
                    rb = bottommost
                    M = cv2.moments(c)
                    cxr = int(M['m10']/M['m00'])
                    return rt, rb, cxr
    return 0, 0, 0

def potential_leftedge(c):
    Area = 1000
    ys = 250
    xs = 60
    if(cv2.contourArea(c)>Area):
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
                if meandst > 240:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    lt = topmost
                    lb = bottommost
                    M = cv2.moments(c)
                    cxl = int(M['m10']/M['m00'])
                    return lt, lb, cxl
    return 0, 0, 0


def left_right_lines(contoursright,contoursleft,z):
    templ = 0
    tempr = 0
    ltl = []
    lbl = []
    cxll = []
    rtl = []
    rbl = []
    cxrl = []
    for c in contoursleft:
        lt, lb, cxl = potential_leftedge(c)
        if cxl != 0:
            ltl.append(lt)
            lbl.append(lb)
            cxll.append(cxl)
            templ+=1
    for c in contoursright:
        rt, rb, cxr = potential_rightedge(c)
        if cxr != 0:
            rtl.append(rt)
            rbl.append(rb)
            cxrl.append(cxr)
            tempr+=1
    eli = 0
    for i in xrange(templ):
        for j in xrange(tempr):
            doorway_movement(lbl[i],ltl[i],rbl[j],rtl[j],cxrl[j],cxll[i])
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
