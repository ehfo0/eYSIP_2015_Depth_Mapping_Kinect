__author__ = 'aniket'
"""
*
*                  ================================
*
*  Author List:         Aniket Patel
*  Filename: 		    Kinect.py
*  Date:                June 20, 2015
*  Functions:           get_depth()
		                filter_smooth()
		                filter_noise()
                        contours_return()
		                potential_rightedge()
                        potential_leftedge()
                        doorway_movement()
                        left_right_lines()
*  Global Variables:
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
import math
import matplotlib.mlab as mlab

ser = serial.Serial('/dev/ttyUSB0')	#initialization of serial communication

def filter_noise(a,mask,ad,row,col):
    """
    * Function Name:	filter_noise
    * Input:		Original frame, noise mask, Original frame with noise pixels being made to 255 value, no. of row tiles, No. of column 				tiles                
    * Output:		Filters the noise from the original depth frame.
    * Logic:		The function divides rows and cols of the frame in some number of pixels. It then finds the mean of the tile and 				assigns the value to the noise pixels in that tile.
    * Example Call:	filter_noise(a,mask,ad,3,4)
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
    a = a/30.0
    a = a.astype(np.uint8)
    a = filter_smooth(a)
    a[0:479,635:639] = a[0:479,630:634]
    return a

def contours_return(a,num):
    """
    * Function Name:	contours_return
    * Input:		Depth Frame and a number for shifting left or right the matrix                        
    * Output:		Returns the left or right edges contours
    * Logic:		It does noise removal process on the frame and shifts the frame matrix by num places so that change in values are 	     		highlighted in the image by Binary Thresholding it.
    * Example Call:	contours_return(a,5)
    """
    b = np.roll(a,num)
    res = np.subtract(b,a)
    res = cv2.medianBlur(res,11)
    mask = res > 200
    res[mask] = 0
    mask = res < 100
    res[mask] = 0
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
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                pts1 = np.float32([[topmost[0]-w,y1],[topmost[0],y1],[bottommost[0]-w,y2],[bottommost[0],y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                if meandst > 50:
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
            if (y2 - y1 > ys) and (abs(x2 - x1) < xs):
                pts1 = np.float32([[topmost[0],y1],[topmost[0]+w,y1],[bottommost[0],y2],[bottommost[0]+w,y2]])
                pts2 = np.float32([[0,0],[w,0],[0,y2-y1],[w,y2-y1]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dst = cv2.warpPerspective(z,M,(w,y2-y1))
                meandst = dst.mean()
                if meandst > 50:
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
    diffl = lb[1]-lt[1]
    diffr = rb[1]-rt[1]
    if abs(diffl - diffr) < 150 and ((cxr - cxl) > 50 and (cxr - cxl ) < 400):
        #ser.write("\x37")
        time.sleep(0.05)
        #ser.write("\x39")
        cv2.line(z,lt,lb,(128,255,0),10)
        cv2.line(z,rt,rb,(128,255,0),10)
        #cv2.waitKey(0)
        return 1
    return 0


def left_right_lines(contoursright,contoursleft):
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
    return ltl, lbl, cxll, rtl, rbl, cxrl, templ, tempr

def horizontal_lines():
    contour = contours_return(z,6400)
    temph = 0
    hll = []
    hrl = []
    cxhl = []
    for c in contour:
        hl, hr, cxh = horizontal_edge(c)
        if cxh != 0:
            hll.append(hl)
            hrl.append(hr)
            cxhl.append(cxh)
            temph += 1
    return hll, hrl, cxhl, temph

def actual_width_in_mm(lb,lt,rb,rt,cxr,cxl):
    a = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    a = a/30.0
    a = a.astype(np.uint8)
    ret, mask = cv2.threshold(a,1,255,cv2.THRESH_BINARY_INV)
    ad = a + mask
    pts1 = np.float32([[lt[0]-30,lt[1]],[lt[0],lt[1]],[lb[0]-30,lb[1]],[lb[0],lb[1]]])
    pts2 = np.float32([[0,0],[30,0],[0,lb[1]-lt[1]],[30,lb[1]-lt[1]]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(ad,M,(30,lb[1]-lt[1]))
    left_depth = np.amin(dst)*30
    pts1 = np.float32([[rt[0],rt[1]],[rt[0]+30,rt[1]],[rb[0],rb[1]],[rb[0]+30,rb[1]]])
    pts2 = np.float32([[0,0],[30,0],[0,rb[1]-rt[1]],[30,rb[1]-rt[1]]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(ad,M,(30,rb[1]-rt[1]))
    right_depth = np.amin(dst)*30
    pixel_width = cxr-cxl
    angle = (pixel_width/640.0)*(57/180.0)*(math.pi)
    width = (left_depth*left_depth) + (right_depth*right_depth) - (2*left_depth*right_depth*math.cos(angle))
    width = math.sqrt(width)
    return width

def actual_height_in_mm(lb,lt,rb,rt):
    a = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    a = a/30.0
    a = a.astype(np.uint8)
    ret, mask = cv2.threshold(a,1,255,cv2.THRESH_BINARY_INV)
    ad = a + mask
    lefttop = ad[lt[1]:lt[1]+10,lt[0]-30:lt[0]]
    lefttop_depth = np.amin(lefttop)*30
    leftbottom = ad[lb[1]-10:lb[1],lb[0]-30:lb[0]]
    leftbottom_depth = np.amin(leftbottom)*30
    righttop = ad[rt[1]:rt[1]+10,rt[0]:rt[0]+30]
    righttop_depth = np.amin(righttop)*30
    rightbottom = ad[rb[1]-10:rb[1],rb[0]:rb[0]+30]
    rightbottom_depth = np.amin(rightbottom)*30
    left_pixel_height = lb[1] - lt[1]
    right_pixel_height = rb[1] - rt[1]
    left_angle = (left_pixel_height/480.0)*(47/180.0)*(math.pi)
    right_angle = (right_pixel_height/480.0)*(47/180.0)*(math.pi)
    left_height = lefttop_depth * lefttop_depth + leftbottom_depth * leftbottom_depth - 2 * leftbottom_depth * lefttop_depth * math.cos(left_angle)
    right_height = righttop_depth * righttop_depth + rightbottom_depth * rightbottom_depth - 2 * rightbottom_depth * righttop_depth * math.cos(right_angle)
    left_height = math.sqrt(left_height)
    right_height = math.sqrt(right_height)
    return left_height, right_height

def return_height_in_mm(lb,lt,rb,rt):
    a = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    left_bottom_x, left_bottom_y = lb[0], lb[1]
    left_top_x, left_top_y = lt[0], lt[1]
    right_bottom_x, right_bottom_y = rb[0], rb[1]
    right_top_x, right_top_y = rt[0], rt[1]
    left_top_area = a[left_top_y:left_top_y+10,left_top_x-10:left_top_x]
    mask = left_top_area == 0
    left_top_area[mask] = 8000
    top = np.amin(left_top_area)
    bound_rect = a[left_top_y:left_bottom_y, left_top_x - 20:left_top_x]
    mask = bound_rect == 0
    bound_rect[mask] = 8000
    bottom = np.amin(bound_rect)
    left_height = math.sqrt(top**2 - bottom **2)
    right_top_area = a[right_top_y:right_top_y+10,right_top_x:right_top_x+10]
    mask = right_top_area == 0
    right_top_area[mask] = 8000
    top = np.amin(right_top_area)
    bound_rect_right = a[right_top_y:right_bottom_y, right_top_x:right_top_x + 20]
    mask = bound_rect_right == 0
    bound_rect_right[mask] = 8000
    bottom = np.amin(bound_rect_right)
    right_height = math.sqrt(top**2 - bottom **2)
    cv2.line(z,lt,lb,(128,255,0),10)
    cv2.line(z,rt,rb,(128,255,0),10)
    return left_height, right_height

def horizontal_edge_test(lb,lt,rb,rt,cxl,cxr,hl,hr,cxh):
    asd = 1

def Probability(std_value,sigma,data):
    p = int(round(data))
    x = np.linspace(std_value-sigma,std_value+sigma,2*sigma)
    a = mlab.normpdf(x,std_value,sigma)
    a = a/(a[len(a)/2])*100
    NewValue = []
    for i in xrange(2*sigma):
        NewValue.append(((a[i] - 60) * 100) / 40)
    if p >= std_value-sigma and p <= std_value+sigma:
        return NewValue[p - (std_value - sigma)]
    else:return 0

def actual_width_test(width):
    prob = Probability(1000,1000,width)
    return prob

def actual_height_test(left_height,right_height):
    left_prob = Probability(1500,1500,left_height)
    right_prob = Probability(1500,1500,right_height)
    return left_prob, right_prob

def door_detection(contoursright,contoursleft):
    ltl, lbl, cxll, rtl, rbl, cxrl, templ, tempr = left_right_lines(contoursright,contoursleft)
    hll, hrl, cxhl, temph = horizontal_lines()
    for i in xrange(templ):
        for j in xrange(tempr):
            for k in xrange(temph):
                if doorway_movement(lbl[i],ltl[i],rbl[j],rtl[j],cxrl[j],cxll[i]):
                    left_height, right_height = actual_height_in_mm(lbl[i],ltl[i],rbl[j],rtl[j])
                    width = actual_width_in_mm(lbl[i],ltl[i],rbl[j],rtl[j],cxrl[j],cxll[i])
                    actual_height_test(left_height, right_height)
                    #actual_width_test(width)

    #horizontal_edge_test(lbl[i],ltl[i],rbl[j],rtl[j],cxll[i],cxrl[i],hll,hrl,cxhl)

def take_right():
    """
    * Function Name:	take_right
    * Input:		None             
    * Output:		Takes Right turn
    * Logic:		This function takes a right turn until the mean of the middlearea crosses the threshold value 
    * Example Call:	take_right()
    """
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        middleval = middlearea.mean()
        ser.write("\x44")
        if middleval > 30:
            return

def take_left():
    """
    * Function Name:	take_left
    * Input:		None             
    * Output:		Takes Left turn
    * Logic:		This function takes a left turn until the mean of the middlearea crosses the threshold value 
    * Example Call:	take_left()
    """
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        middleval = middlearea.mean()
        ser.write("\x45")
        if middleval > 30:
            return

def take_right_near():
    """
    * Function Name:	take_right_near
    * Input:		None             
    * Output:		Takes Right turn
    * Logic:		This function takes a Right turn until the obstacle is not detected i.e. If the obstacle is in range it will turn 				until it is out of its sight 
    * Example Call:	take_right_near()
    """
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        ser.write("\x44")
        if Count_near_pixels(middlearea,900) < 1000:
            return

def take_left_near():
    """
    * Function Name:	take_left_near
    * Input:		None             
    * Output:		Takes Left turn
    * Logic:		This function takes a Left turn until the obstacle is not detected i.e. If the obstacle is in range it will turn 				until it is out of its sight 
    * Example Call:	take_left_near()
    """
    while(1):
        z = get_depth()
        middlearea = z[200:479,200:439]
        ser.write("\x45")
        if Count_near_pixels(middlearea,900) < 1000:
            return

def stuck_pos_movement():
    """
    * Function Name:	stuck_pos_movement
    * Input:		None             
    * Output:		Removes robot from a stuck position
    * Logic:		When both the middle left and middle right detect an obstacle it takes the mean of the left and right area and the 				area with lesser mean is the preferable area to go 
    * Example Call:	stuck_pos_movement()
    """
    z = get_depth()
    leftarea = z[0:479,0:100]
    rightarea = z[0:479,539:639]
    leftvals = leftarea.mean()
    rightvals = rightarea.mean()
    if leftvals > rightvals:
        print "left"
        take_left()
    else:
        print "right"
        take_right();

def data_send(x,y):
    """
    * Function Name:	data_send
    * Input:		left and right speed mode         
    * Output:		Sends speed mode of the robot wheels to the Fire bird V for further analysis
    * Logic:		Total 25 different possibilities of speed modes are their according to the vertical frame in which the obstacle is 				detected and using if else statements proper speed mode is sent
    * Example Call:	data_send(speed_left,speed_right)
    """
    if x == 0:
        if y==0:
            ser.write('\x00')
        elif y == 1:
            ser.write('\x01')
        elif y == 2:
            ser.write('\x02')
        elif y == 3:
            ser.write('\x03')
        elif y == 4:
            ser.write('\x04')
    elif x == 1:
        if y==0:
            ser.write('\x10')
        elif y == 1:
            ser.write('\x11')
        elif y == 2:
            ser.write('\x12')
        elif y == 3:
            ser.write('\x13')
        elif y == 4:
            ser.write('\x14')
    elif x == 2:
        if y==0:
            ser.write('\x20')
        elif y == 1:
            ser.write('\x21')
        elif y == 2:
            ser.write('\x22')
        elif y == 3:
            ser.write('\x23')
        elif y == 4:
            ser.write('\x24')
    elif x == 3:
        if y==0:
            ser.write('\x30')
        elif y == 1:
            ser.write('\x31')
        elif y == 2:
            ser.write('\x32')
        elif y == 3:
            ser.write('\x33')
        elif y == 4:
            ser.write('\x34')
    elif x == 4:
        if y==0:
            ser.write('\x40')
        elif y == 1:
            ser.write('\x41')
        elif y == 2:
            ser.write('\x42')
        elif y == 3:
            ser.write('\x43')
        elif y == 4:
            stuck_pos_movement()

def Count_near_pixels(area,dist):
    """
    * Function Name:	Count_near_pixels
    * Input:		area and the distance upto which the obstacle should be detected        
    * Output:		Returns the number of obstacle pixels that are in the distance range.
    * Logic:		The depth data is Binary thresholded according to the obstacle detected in its range. Than the NonZeros are counted as 				they are the obstacle
    * Example Call:	Count_near_pixels(area,900)
    """
    ret, th3 = cv2.threshold(area,dist/30,255,cv2.THRESH_BINARY_INV)
    Count = cv2.countNonZero(th3)
    return Count

def search_wall(dir):
    """
    * Function Name:	search_wall
    * Input:		left/right wall      
    * Output:		follows left or right wall
    * Logic:		If left wall is selected for instance then the robot moves along the wall. The robot keeps track of the objects on the 				left side of frame for left wall and if the frame does not have any object in the range than the robot moves left 				until it is detected 
    * Example Call:	search_wall(0)
    """
    if dir == 0:
        while(True):
            z = get_depth()
            area = z[0:479,0:319]
            ser.write("\x03")
            if Count_near_pixels(area,1800) > 1000:
                break
    elif dir == 1:
        while(True):
            z = get_depth()
            area = z[0:479,320:639]
            ser.write("\x30")
            if Count_near_pixels(area,1800) > 1000:
                break

def regular_movement(z):
    """
    * Function Name:	regular_movement
    * Input:		Original depth frame     
    * Output:		robot moves without bumping into any obstacle
    * Logic:		The frame is divided in 8 vertical sections. Speed mode is selected from the speed_right and speed_left. There are 4 				left frames and 4 right frames. The frame loop starts from middle and if any frame detects any obstacle break the loop 				and the corresponding data is saved in the speed_left or speed_right variable
    * Example Call:	regular_movement(original)
    """
    x = 320
    speed = 4
    for i in xrange(4):
        area = z[0:479,x:x+79]
        if Count_near_pixels(area,900) > 1000:
            break
        speed = speed - 1
        x = x + 80
    speed_right = speed
    x = 319
    speed = 4
    for i in xrange(4):
        area = z[0:479,x-79:x]
        if Count_near_pixels(area,900) > 1000:
            break
        speed = speed - 1
        x = x - 80
    speed_left = speed
    if speed_left!=0 or speed_right!=0:
        data_send(speed_left,speed_right)
    else:
        search_wall(0)
        ser.write("\x00")

def horizontal_edge(c):
    Area = 500
    ys = 50
    xs = 100
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
            if (y2 - y1 < ys) and (abs(x2 - x1) > xs):
                    cv2.line(z,leftmost,rightmost,(0,255,0),5)
                    hl = leftmost
                    hr = rightmost
                    M = cv2.moments(c)
                    cxh = int(M['m10']/M['m00'])
                    return hl, hr, cxh
    return 0, 0, 0

ctx = freenect.init()
dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

freenect.set_tilt_degs(dev, 20)
freenect.close_device(dev)

while(True):
    z = get_depth()	#returns the depth frame
    contoursright = contours_return(z,-10)
    contoursleft = contours_return(z,10)
    door_detection(contoursright,contoursleft)
    #regular_movement(original)
    cv2.imshow('depth',z)
    if cv2.waitKey(1)!=-1:
        ser.write('\x35')
        ser.close()
        freenect.Kill
        break

cv2.destroyAllWindows()
