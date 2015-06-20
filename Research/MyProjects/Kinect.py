__author__ = 'aniket'
"""
*
*                  ================================
*
*  Author List: Aniket P
*  Filename: 		Kinect.py
*  Date:                June 20, 2015
*  Functions:   get_depth()
		filter_smooth()
		filter_noise()
                contours_return()
		potential_rightedge()
		potential_leftedge()
                doorway_movement()
                left_right_lines()
*  Global Variables:    mode
			flag
*  Dependent library files:     numpy, freenect, cv2, serial, time
*
*  e-Yantra - An MHRD project under National Mission on Education using
*  ICT(NMEICT)
*
**************************************************************************
"""

import freenect
import cv2
import numpy as np
import time
import serial

ser = serial.Serial('/dev/ttyUSB0')	#initialization of serial communication

global mode	#variable to provide the mode of movement
mode = 0
global flag	#flag is 0 if door is not yet detected. It is 1 when the door is detected even once.
flag = 0

def filter_noise(a,mask,ad,row,col):
    """
    * Function Name:	filter_noise
    * Input:		Original frame, noise mask, Original frame with noise pixels being made to 255 value, no. of row tiles, No. of column 				tiles                
    * Output:		Filters the noise from the original depth frame.
    * Logic:		The function divides rows and cols of the frame in some number of pixels. It then finds the mean of the tile and 				assigns the value to the noise pixels in that tile.
    * Example Call:	filter_noise(a,mask,ad,row,col)
    """
    rp = 480/row
    cp = 640/col
    y = 0
    for i in xrange(col):
        x = 0
        for j in xrange(row):
            area = ad[x:x+rp-1,y:y+cp-1]
            mask[x:x+rp-1,y:y+cp-1]*=area.mean()
            a[x:x+rp-1,y:y+cp-1]+=mask[x:x+rp-1,y:y+cp-1]
            x = x + rp
        y = y + cp
    return a

def filter_smooth(a):
    """
    * Function Name:	filter_smooth
    * Input:		Original Depth frame in mm        
    * Output:		Filters the noise from the depth frame
    * Logic:		It creates a mask for the noise. It makes all the noise pixels to 255 to send to filter noise. The output from filter 				noise is smoothened using bilateral filter
    * Example Call:	filter_smooth(a)
    """
    ret, mask = cv2.threshold(a,1,255,cv2.THRESH_BINARY_INV)
    mask_1 = mask/255
    ad = a + mask
    blur = filter_noise(a,mask_1,ad,3,4)
    blur = cv2.bilateralFilter(blur, 5, 50, 100)
    return blur

def get_depth():
    """
    * Function Name:	get_depth
    * Input:		None                        
    * Output:		Returns the depth information from pixel values of 0 to 255
    * Logic:		It recieves the depth information from the Kinect sensor in mm. The depth range is 40cm to 800cm. The values are 				brought down from 0 to 255. It then changes the data type to 1 bytes. It then smoothens the frame and returns it.
    * Example Call:	get_depth()
    """
    a = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    a = a/30
    a = a.astype(np.uint8)
    a = filter_smooth(a)
    return a

def contours_return(a,num):
    """
    * Function Name:	contours_return
    * Input:		Depth Frame and a number for shifting left or right the matrix                        
    * Output:		Returns the left or right edges contours
    * Logic:		It does noise removal process on the frame and shifts the frame matrix by num places so that change in values are 	     		highlighted in the image by Binary Thresholding it.
    * Example Call:	contours_return(a,num)
    """
    b = np.roll(a,num)
    res = np.subtract(b,a)
    res = np.multiply(res,255)
    res = cv2.medianBlur(res,5)
    ret,th3 = cv2.threshold(res,50,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def potential_rightedge(c):
    """
    * Function Name:	potential_rightedge
    * Input:		A contour                        
    * Output:		Returns a potential rightedge which fulfills all the conditions
			returns topmost, bottommost and centroid of the contour.
    * Logic:		If area of the contour crosses a threshoold than the extreme points are calculated of the contour. If the difference 				in opposite extreme points lies in the given threshold and the width and height of the bounding rectangle lies in the 				threshold than the contour is a potential contour and a line is drawn as an edge. The centroid is calculated for 				further use 
    * Example Call:	potential_rightedge(c)
    """
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
            xr,yr,wr,hr = cv2.boundingRect(c)
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs) and hr > 240 and wr < 50:
                pts1 = np.float32([[topmost[0]-w,y1],[topmost[0],y1],[bottommost[0]-w,y2],[bottommost[0],y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                if meandst > 150:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    rt = topmost
                    rb = bottommost
                    M = cv2.moments(c)
                    cxr = int(M['m10']/M['m00'])
                    return rt, rb, cxr
    return 0, 0, 0

def potential_leftedge(c):
    """
    * Function Name:	potential_leftedge
    * Input:		A contour                        
    * Output:		Returns a potential leftedge which fulfills all the conditions
			returns topmost, bottommost and centroid of the contour.
    * Logic:		If area of the contour crosses a threshoold than the extreme points are calculated of the contour. If the difference 				in opposite extreme points lies in the given threshold and the width and height of the bounding rectangle lies in the 				threshold than the contour is a potential contour and a line is drawn as an edge. The centroid is calculated for 				further use 
    * Example Call:	potential_leftedge(c)
    """
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
            xr,yr,wr,hr = cv2.boundingRect(c)
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs) and hr > 240 and wr < 50:
                pts1 = np.float32([[topmost[0],y1],[topmost[0]+w,y1],[bottommost[0],y2],[bottommost[0]+w,y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                if meandst > 150:
                    cv2.line(z,topmost,bottommost,(0,255,0),5)
                    lt = topmost
                    lb = bottommost
                    M = cv2.moments(c)
                    cxl = int(M['m10']/M['m00'])
                    return lt, lb, cxl
    return 0, 0, 0

def doorway_movement(lb,lt,rb,rt,cxr,cxl):
    """
    * Function Name:	doorway_movement
    * Input:		left_bottom, left_top, right_bottom, right_top, right_edge_centroid, left_edge_centroid                       
    * Output:		Movement of the robot on door detection
    * Logic:		Pixel Heights of the edges are calculated. If the pixel height difference and centroid of left and right edge 				difference crosses a threshold than the edges are door edges. The midpoint is calculated. If midpoint lies in middle 				frame than robot moves forward and if it lies on the left or right part than the robot takes a turn. When mode is 1 				the door is detected and in mode 0 mode regular movement is followed.
    * Example Call:	doorway_movement(lb,lt,rb,rt,cxr,cxl)
    """
    global mode
    global flag
    diffl = lb[1]-lt[1]
    diffr = rb[1]-rt[1]
    if abs(diffl - diffr) < 150 and ((cxr - cxl) > 50 and (cxr - cxl ) < 400):
        #ser.write("\x37")
        time.sleep(0.05)
        #ser.write("\x39")
        mode = 2
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
            mode = 0
        else: mode = 2

def left_right_lines(contoursright,contoursleft,z):
    """
    * Function Name:	left_right_lines
    * Input:		right contours, left contours, original depth frame                    
    * Output:		detects left and right edges and accordingly calls the door movement function.
    * Logic:		creates an array of all the required parameters of all the potential left and right edges and sends them two at a time 				to doorway_movement function.
    * Example Call:	left_right_lines(contoursright,contoursleft,z)
    """
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

    mode = 0
    for i in xrange(templ):
        for j in xrange(tempr):
            doorway_movement(lbl[i],ltl[i],rbl[j],rtl[j],cxrl[j],cxll[i])
    return z

while(True):
    z = get_depth()	#returns the depth frame 
    contoursright = contours_return(z,2)
    contoursleft = contours_return(z,-2)
    linesz = left_right_lines(contoursright,contoursleft,z)
    cv2.imshow('depth',linesz)
    if cv2.waitKey(1)!=-1:
        freenect.Kill
        break

cv2.destroyAllWindows()