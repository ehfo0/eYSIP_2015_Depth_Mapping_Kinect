"""
This module contains code for detection of doors.
"""
import freenect
import cv2
import numpy as np
import time
import serial
import math
import matplotlib.mlab as mlab
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')

DOOR_FLAG = False
global global_depth_map
DOOR_COUNT = 0
global ser

def filter_noise(depth_array, mask, masked_array, row, col):
    """
    * Function Name:filter_noise
    * Input:		Original frame, noise mask, Original
                    frame with noise pixels being made to 255 value,
                    no. of row tiles, No. of column tiles.
    * Output:		Filters the noise from the original depth frame.
    * Logic:		The function divides rows and cols of the frame in
                    some number of pixels. It then finds the mean of the
                    tile and assigns the value to the noise pixels in that
                    tile.
    * Example Call:	filter_noise(depth_array, mask, ad, 3, 4)
    """
    row_ratio = 480/row
    column_ratio = 640/col
    temp_y = 0
    for i in xrange(col):
        temp_x = 0
        for j in xrange(row):
            area = masked_array[temp_x:temp_x+row_ratio-1, \
                   temp_y:temp_y+column_ratio-1]
            mask[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1] \
                *= area.mean()
            depth_array[temp_x:temp_x+row_ratio-1, \
            temp_y:temp_y+column_ratio-1] += \
                mask[temp_x:temp_x+row_ratio-1, temp_y:temp_y+column_ratio-1]
            temp_x = temp_x + row_ratio
        temp_y = temp_y + column_ratio
    return depth_array

def filter_smooth(depth_array):
    """
    * Function Name:	filter_smooth
    * Input:		Original Depth frame in mm.
    * Output:		Filters the noise from the depth frame
    * Logic:		It creates a mask for the noise. It makes
                    all the noise pixels to 255 to send to filter noise.
                    The output from filter noise is smoothened using
                    bilateral filter
    * Example Call:	filter_smooth(a)
    """
    ret, mask = cv2.threshold(depth_array, 10, 255, cv2.THRESH_BINARY_INV)
    mask_1 = mask/255
    masked_array = depth_array + mask
    blur = filter_noise(depth_array, mask_1, masked_array, 3, 4)
    blur = cv2.bilateralFilter(blur, 5, 50, 100)
    return blur

def get_depth():
    """
    * Function Name:	get_depth
    * Input:		None
    * Output:		Returns the depth information from pixel values of 0 to 255
    * Logic:		It recieves the depth information from the Kinect sensor in mm.
                    The depth range is 40cm to 800cm. The values are brought
                    down from 0 to 255. It then changes the data type
                    to 1 bytes. It then smoothens the frame and returns it.
    * Example Call:	get_depth()
    """
    depth_array = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    depth_array = depth_array/30.0
    depth_array = depth_array.astype(np.uint8)
    depth_array = filter_smooth(depth_array)
    depth_array[0:479, 630:639] = depth_array[0:479, 620:629]
    return depth_array

def contours_return(depth_array, num):
    """
    * Function Name:	contours_return
    * Input:		Depth Frame and a number for shifting left or right the matrix.
    * Output:		Returns the left or right edges contours
    * Logic:		It does noise removal process on the frame and
                    shifts the frame matrix by num places so that
                    change in values are highlighted in the
                    image by Binary Thresholding it.
    * Example Call:	contours_return(a,5)
    """
    temp_b = np.roll(depth_array, num)
    res = np.subtract(temp_b, depth_array)
    result = cv2.medianBlur(res, 11)
    mask = result > 200
    result[mask] = 0
    mask = result < 100
    result[mask] = 0
    ret, th3 = cv2.threshold(result, 50, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(th3, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    return contours

def potential_rightedge(contours):
    """
    * Function Name:	potential_rightedge
    * Input:		A contour
    * Output:		Returns a potential rightedge which fulfills all the conditions
                    returns topmost, bottommost and centroid of the contour.
    * Logic:		If area of the contour crosses a threshoold than the
                    extreme points are calculated of the contour. If
                    the difference 	in opposite extreme points lies
                    in the given threshold and the width and height
                    of the bounding rectangle lies in the threshold
                    than the contour is a potential contour and a line
                    is drawn as an edge. The centroid is calculated for
                    further use
    * Example Call:	potential_rightedge(c)
    """
    temp_area = 1000
    thresh_y = 250
    thresh_x = 60
    if cv2.contourArea(contours) > temp_area:
        leftmost = tuple(contours[contours[:, :, 0].argmin()][0])
        rightmost = tuple(contours[contours[:, :, 0].argmax()][0])
        topmost = tuple(contours[contours[:, :, 1].argmin()][0])
        bottommost = tuple(contours[contours[:, :, 1].argmax()][0])
        x_1 = leftmost[0]
        x_2 = rightmost[0]
        x_3 = topmost[0]
        x_4 = bottommost[0]
        y_1 = topmost[1]
        y_2 = bottommost[1]
        width = 50
        if (y_2 - y_1 > thresh_y) and (abs(x_2 - x_1) < thresh_x) \
                and x_3 < 620 and x_4 < 620:
            pts1 = np.float32([[topmost[0]-width, y_1],
                               [topmost[0], y_1], [bottommost[0]-width, y_2],
                               [bottommost[0], y_2]])
            pts2 = np.float32([[0, 0], [width, 0],
                               [0, y_2-y_1], [width, y_2-y_1]])
            flat = cv2.getPerspectiveTransform(pts1, pts2)
            dst = cv2.warpPerspective(global_depth_map, flat, (width, y_2-y_1))
            meandst = dst.mean()
            if meandst > 50:
                cv2.line(global_depth_map, topmost, bottommost, (0, 255, 0), 5)
                right_top = topmost
                right_bottom = bottommost
                flat = cv2.moments(contours)
                cxr = int(flat['m10'] / flat['m00'])
                return right_top, right_bottom, cxr
    return 0, 0, 0

def potential_leftedge(contours):
    """
    * Function Name:	potential_leftedge
    * Input:		A contour
    * Output:		Returns a potential leftedge which fulfills all the conditions
                    returns topmost, bottommost and centroid of the contour.
    * Logic:		If area of the contour crosses a threshoold than the
                    extreme points are calculated of the contour. If
                    the difference in opposite extreme points lies
                    in the given threshold and the width and height
                    of the bounding rectangle lies in the threshold
                    than the contour is a potential contour and a
                    line is drawn as an edge. The centroid is
                    calculated for further use
    * Example Call:	potential_leftedge(c)
    """
    temp_area = 1000
    thresh_y = 250
    thresh_x = 60
    if cv2.contourArea(contours) > temp_area:
        leftmost = tuple(contours[contours[:, :, 0].argmin()][0])
        rightmost = tuple(contours[contours[:, :, 0].argmax()][0])
        topmost = tuple(contours[contours[:, :, 1].argmin()][0])
        bottommost = tuple(contours[contours[:, :, 1].argmax()][0])
        x_1 = leftmost[0]
        x_2 = rightmost[0]
        x_3 = topmost[0]
        x_4 = bottommost[0]
        y_1 = topmost[1]
        y_2 = bottommost[1]
        width = 50
        if (y_2 - y_1 > thresh_y) and (abs(x_2 - x_1) < thresh_x) \
                and x_3 > 20 and x_4 > 20:
            pts1 = np.float32([[topmost[0], y_1],
                               [topmost[0] + width, y_1], [bottommost[0], y_2],
                               [bottommost[0] + width, y_2]])
            pts2 = np.float32([[0, 0], [width, 0], [0, y_2-y_1],
                               [width, y_2-y_1]])
            flat = cv2.getPerspectiveTransform(pts1, pts2)
            dst = cv2.warpPerspective(global_depth_map, flat, (width, y_2-y_1))
            meandst = dst.mean()
            if meandst > 50:
                cv2.line(global_depth_map, topmost, bottommost, (0, 255, 0), 5)
                left_top = topmost
                left_bottom = bottommost
                flat = cv2.moments(contours)
                cxl = int(flat['m10'] / flat['m00'])
                return left_top, left_bottom, cxl
    return 0, 0, 0

def is_door(left_bottom, left_top, right_bottom, right_top, cxr, cxl):
    """
    * Function Name:	doorway_movement
    * Input:		left_bottom, left_top, right_bottom,
                    right_top, right_edge_centroid,
                    left_edge_centroid
    * Output:		Movement of the robot on door detection
    * Logic:		Pixel Heights of the edges are calculated.
                    If the pixel height difference and centroid
                    of left and right edge difference crosses a
                    threshold than the edges are door edges.
                    The midpoint is calculated. If midpoint lies
                    in middle frame than robot moves forward and
                    if it lies on the left or right part than the
                    robot takes a turn. When mode is 1 the door is
                    detected and in mode 0 mode regular movement is
                    followed.
    * Example Call:	doorway_movement(lb,lt,rb,rt,cxr,cxl)
    """
    diffl = left_bottom[1]-left_top[1]
    diffr = right_bottom[1]-right_top[1]
    if abs(diffl - diffr) < 150 and((cxr - cxl) > 50 and(cxr - cxl) < 400):
        cv2.line(global_depth_map, left_top, left_bottom, (128, 255, 0), 10)
        cv2.line(global_depth_map, right_top, right_bottom, (128, 255, 0), 10)
        return 1
    return 0

def left_right_lines(contours_right, contours_left):
    """
    * Function Name:	left_right_lines
    * Input:		right contours, left contours, original depth frame
    * Output:		detects left and right edges and accordingly calls
                    the door movement function.
    * Logic:		creates an array of all the required parameters
                    of all the potential left and right edges and
                    sends them two at a time to doorway_movement function.
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
    for contours in contours_left:
        left_top, left_bottom, cxl = potential_leftedge(contours)
        if cxl != 0:
            ltl.append(left_top)
            lbl.append(left_bottom)
            cxll.append(cxl)
            templ += 1
    for contours in contours_right:
        right_top, right_bottom, cxr = potential_rightedge(contours)
        if cxr != 0:
            rtl.append(right_top)
            rbl.append(right_bottom)
            cxrl.append(cxr)
            tempr += 1
    return ltl, lbl, cxll, rtl, rbl, cxrl, templ, tempr

def horizontal_lines():
    """
    * Function Name: horizontal_lines()
    * Input:		None
    * Output:		Returns information about the edges.
    * Logic:		Analyzes the depth array for any drastic
                    change in vertical direction. Areas with
                    sudden increase/decrease in depth are marked as edges.
    * Example Call:	horizontal_line()
    """

    contour = contours_return(global_depth_map, 6400)
    temph = 0
    hll = []
    hrl = []
    cxhl = []
    for contours in contour:
        height_left, height_right, cxh = horizontal_edge(contours)
        if cxh != 0:
            hll.append(height_left)
            hrl.append(height_right)
            cxhl.append(cxh)
            temph += 1
    return hll, hrl, cxhl, temph

def actual_width_in_mm(left_bottom, left_top, right_bottom, right_top,
                       cxr, cxl):
    """
    * Function Name:actual_width_in_mm()
    * Input:		left_bottom: bottom most co-ordinate of the left edge.
                    left_top: top most co-ordinate of the right edge.
                    right_bottom: Bottom most co-ordinate of the right edge
                    right_top: Top most co-ordinate of the right edge
                    cxr: Centroid of the right edge.
                    cxl: Centroid of the left edge.
    * Output:		Returns the real width of the obstacle.
    * Logic:		Calculates the real width in mm using
                    basic trigonometric calculations.
    * Example Call:	acutal_width_in_mm(10,10,20,20,15,15)
    """
    depth_map = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    depth_map = depth_map / 30.0
    depth_map = depth_map.astype(np.uint8)
    ret, mask = cv2.threshold(depth_map, 1, 255, cv2.THRESH_BINARY_INV)
    masked = depth_map + mask
    pts1 = np.float32([[left_top[0]-30, left_top[1]],
                       [left_top[0], left_top[1]], [left_bottom[0]-30,
                                                    left_bottom[1]],
                       [left_bottom[0], left_bottom[1]]])
    pts2 = np.float32([[0, 0], [30, 0], [0, left_bottom[1]-left_top[1]],
                       [30, left_bottom[1]-left_top[1]]])
    flat = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(masked, flat, (30, left_bottom[1]-left_top[1]))
    left_depth = np.amin(dst)*30
    pts1 = np.float32([[right_top[0], right_top[1]],
                       [right_top[0]+30, right_top[1]],
                       [right_bottom[0], right_bottom[1]],
                       [right_bottom[0]+30, right_bottom[1]]])
    pts2 = np.float32([[0, 0], [30, 0], [0, right_bottom[1]-right_top[1]],
                       [30, right_bottom[1]-right_top[1]]])
    flat = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(masked, flat, (30, right_bottom[1]-right_top[1]))
    right_depth = np.amin(dst)*30
    pixel_width = cxr-cxl
    angle = (pixel_width/640.0)*(57/180.0)*(math.pi)
    width = (left_depth*left_depth) + (right_depth*right_depth) - \
            (2*left_depth*right_depth*math.cos(angle))
    width = math.sqrt(width)
    return width

def actual_height_in_mm(left_bottom, left_top, right_bottom, right_top):
    """
    * Function Name:actual_height_in_mm()
    * Input:		left_bottom: bottom most co-ordinate of the left edge.
                    left_top: top most co-ordinate of the right edge.
                    right_bottom: Bottom most co-ordinate of the right edge
                    right_top: Top most co-ordinate of the right edge
                    cxr: Centroid of the right edge.
                    cxl: Centroid of the left edge.
    * Output:		Returns the real height of the obstacle.
    * Logic:		Calculates the real height in mm using cosine rule.
    * Example Call:	acutal_hieght_in_mm(10,10,20,20,15,15)
    """

    depth_map = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    depth_map = depth_map / 30.0
    depth_map = depth_map.astype(np.uint8)
    ret, mask = cv2.threshold(depth_map, 1, 255, cv2.THRESH_BINARY_INV)
    masked = depth_map + mask
    lefttop = masked[left_top[1]:left_top[1]+10, left_top[0]-30:left_top[0]]
    lefttop_depth = np.amin(lefttop)*30
    leftbottom = masked[left_bottom[1]-10:left_bottom[1], \
                 left_bottom[0]-30:left_bottom[0]]
    leftbottom_depth = \
        np.amin(leftbottom)*30
    righttop = masked[right_top[1]:right_top[1] + 10, \
               right_top[0]:right_top[0] + 30]
    righttop_depth = np.amin(righttop)*30
    rightbottom = masked[right_bottom[1]-10:right_bottom[1], \
                  right_bottom[0]:right_bottom[0] + 30]
    rightbottom_depth = np.amin(rightbottom)*30
    left_pixel_height = left_bottom[1] - left_top[1]
    right_pixel_height = right_bottom[1] - right_top[1]
    left_angle = (left_pixel_height/480.0)*(47/180.0)*(math.pi)
    right_angle = (right_pixel_height/480.0)*(47/180.0)*(math.pi)
    left_height = lefttop_depth * lefttop_depth + \
                  leftbottom_depth * leftbottom_depth - 2 * leftbottom_depth * \
                lefttop_depth * math.cos(left_angle)
    right_height = righttop_depth * righttop_depth + \
                   rightbottom_depth * rightbottom_depth - \
                   2 * rightbottom_depth * righttop_depth * \
                   math.cos(right_angle)
    left_height = math.sqrt(left_height)
    right_height = math.sqrt(right_height)
    return left_height, right_height

def return_height_in_mm(left_bottom, left_top, right_bottom, right_top):

    """
    * Function Name:return_height_in_mm()
    * Input:		left_bottom: bottom most co-ordinate of the left edge.
                    left_top: top most co-ordinate of the right edge.
                    right_bottom: Bottom most co-ordinate of the right edge
                    right_top: Top most co-ordinate of the right edge
                    cxr: Centroid of the right edge.
                    cxl: Centroid of the left edge.
    * Output:		Returns the real height of the obstacle.
    * Logic:		Calculates the real height in mm using pythagoras theorem.
    * Example Call:	return_height_in_mm(10,10,20,20,15,15)
    """

    depth_map = freenect.sync_get_depth(format=freenect.DEPTH_MM)[0]
    left_bottom_y = left_bottom[1]
    left_top_x, left_top_y = left_top[0], left_top[1]
    right_bottom_y = right_bottom[1]
    right_top_x, right_top_y = right_top[0], right_top[1]
    left_top_area = depth_map[left_top_y:left_top_y+10, \
                    left_top_x-10:left_top_x]
    mask = left_top_area == 0
    left_top_area[mask] = 8000
    top = np.amin(left_top_area)
    bound_rect = depth_map[left_top_y:left_bottom_y, \
                 left_top_x - 20:left_top_x]
    mask = bound_rect == 0
    bound_rect[mask] = 8000
    bottom = np.amin(bound_rect)
    left_height = math.sqrt(top**2 - bottom **2)
    right_top_area = depth_map[right_top_y:right_top_y+10, \
                     right_top_x:right_top_x+10]
    mask = right_top_area == 0
    right_top_area[mask] = 8000
    top = np.amin(right_top_area)
    bound_rect_right = depth_map[right_top_y:right_bottom_y \
        , right_top_x:right_top_x + 20]
    mask = bound_rect_right == 0
    bound_rect_right[mask] = 8000
    bottom = np.amin(bound_rect_right)
    right_height = math.sqrt(top**2 - bottom **2)
    cv2.line(global_depth_map, left_top, left_bottom, (128, 255, 0), 10)
    cv2.line(global_depth_map, right_top, right_bottom, (128, 255, 0), 10)
    return left_height, right_height

def rectangle_door_test(left_bottom, left_top, right_bottom,
                        right_top, cxl, cxr, height_left, height_right, cxh):

    """
    * Function Name:return_height_in_mm()
    * Input:		left_bottom: bottom most co-ordinate of the left edge.
                    left_top: top most co-ordinate of the right edge.
                    right_bottom: Bottom most co-ordinate of the right edge
                    right_top: Top most co-ordinate of the right edge
                    cxr: Centroid of the right edge.
                    cxl: Centroid of the left edge.
                    height_left: height in pixels of left edge
                    height_right: height in pixels of right edge.
    * Output:		Returns a probability value based on whether the obstacle
                    is a door or not.
    * Logic:		Calculates probability using different tests
    * Example Call:	rectangle_door_test(150,150,250,150,200,200,50,50,25)
    """

    if cxh > cxl and cxh < cxr:
        top_edge_pixel_length = height_right[0] - height_left[0]
        top = right_top[0] - left_top[0]
        middle = cxr - cxl
        bottom = right_bottom[0] - left_bottom[0]
        top_error = top - top_edge_pixel_length
        middle_error = middle - top_edge_pixel_length
        bottom_error = bottom - top_edge_pixel_length
        probtop = probability(0, 200, top_error)
        probmiddle = probability(0, 200, middle_error)
        probbottom = probability(0, 200, bottom_error)
        probavg = (probtop + probmiddle + probbottom) / 3
        return probavg

def probability(std_value, sigma, data):
    """
    * Function Name:probability()
    * Input:		std_value: Standard deviation
                    sigma: A parameter for Gaussian curve.
                    data: Information for which probability is calculated
    * Output:		Returns a probability value using Gaussian distribution function.
    * Logic:		Calculates probability using a Gaussian distribution curve
    * Example Call:	probability(1500,500,1750)
    """

    param_x = int(round(data))
    bounds = np.linspace(std_value-sigma, std_value+sigma, 2*sigma)
    temp = mlab.normpdf(bounds, std_value, sigma)
    temp = temp / (temp[len(temp) / 2]) * 100
    newvalue = []
    for i in xrange(2*sigma):
        newvalue.append(((temp[i] - 60) * 100) / 40)
    if param_x >= std_value-sigma and param_x <= std_value+sigma:
        return newvalue[param_x - (std_value - sigma)]
    else: return 0

def actual_width_test(width):
    """
    * Function Name:actual_width_test()
    * Input:		width: Width of door in mm.
    * Output:		Returns a probability value.
    * Logic:		Calculates probability using a Gaussian distribution curve
    * Example Call:	actual_width_test(1500,500,1750)
    """
    prob = probability(1000, 1000, width)
    return prob

def actual_height_test(left_height, right_height):
    """
    * Function Name:actual_height_test()
    * Input:		std_value: Standard deviation
                    sigma: A parameter for Gaussian curve.
                    data: Information for which probability is calculated
    * Output:		Returns a probability value using Gaussian distribution function.
    * Logic:		Calculates probability using a Gaussian distribution curve
    * Example Call:	probability(1500,500,1750)
    """
    left_prob = probability(1500, 1500, left_height)
    right_prob = probability(1000, 1000, right_height)
    return (left_prob+right_prob) / 2.0

def door_detection(contours_right, contours_left, test_cases):
    """
    * Function Name:probability()
    * Input:		std_value: Standard deviation
                    sigma: A parameter for Gaussian curve.
                    data: Information for which probability is calculated
    * Output:		Returns a probability value using Gaussian distribution function.
    * Logic:		Calculates probability using a Gaussian distribution curve
    * Example Call:	probability(1500,500,1750)
    """
    global DOOR_COUNT
    global DOOR_FLAG
    ltl, lbl, cxll, rtl, rbl, cxrl, templ, tempr = \
        left_right_lines(contours_right, contours_left)
    test_1, test_2, test_3 = test_cases
    #hll, hrl, cxhl, temph = horizontal_lines()
    for i in xrange(templ):
        for j in xrange(tempr):
            #for k in xrange(temph):
            if is_door(lbl[i], ltl[i], rbl[j], rtl[j], cxrl[j], cxll[i]):
                left_height, right_height = \
                    actual_height_in_mm(lbl[i], ltl[i], rbl[j], rtl[j])
                width = actual_width_in_mm(lbl[i], ltl[i],
                                           rbl[j], rtl[j], cxrl[j], cxll[i])
                #if test_1:

                if test_2:
                    prob_2 = actual_height_test(left_height, right_height)
                if test_3:
                    prob_3 = actual_width_test(width)
                if prob_2 > 80 and prob_3 > 90:
                    DOOR_COUNT += 1
                    ser.write("\x37")
                    time.sleep(0.05)
                    ser.write("\x39")
    if DOOR_COUNT == 1:
        DOOR_FLAG = True

def take_right():
    """
    * Function Name:	take_right
    * Input:		None
    * Output:		Takes Right turn
    * Logic:		This function takes a right turn until
                    the mean of the middlearea crosses
                    the threshold value
    * Example Call:	take_right()
    """
    while True:
        global_depth_map = get_depth()
        middlearea = global_depth_map[200:479, 200:439]
        middleval = middlearea.mean()
        print middleval
        ser.write("\x44")
        if middleval > 30:
            return

def take_left():
    """
    * Function Name:	take_left
    * Input:		None
    * Output:		Takes Left turn
    * Logic:		This function takes a left turn until
                    the mean of the middlearea crosses the
                    threshold value
    * Example Call:	take_left()
    """
    while True:
        global_depth_map = get_depth()
        middlearea = global_depth_map[200:479, 200:439]
        middleval = middlearea.mean()
        ser.write("\x45")
        if middleval > 30:
            return

def take_right_near():
    """
    * Function Name:	take_right_near
    * Input:		None
    * Output:		Takes Right turn
    * Logic:		This function takes a Right turn until the
                    obstacle is not detected i.e. If the
                    obstacle is in range it will turn
                    until it is out of its sight
    * Example Call:	take_right_near()
    """
    while True:
        global_depth_map = get_depth()
        middlearea = global_depth_map[0:479, 160:479]
        contoursright = contours_return(global_depth_map, -10)
        contoursleft = contours_return(global_depth_map, 10)
        door_detection(contoursright, contoursleft, test_cases)
        ser.write("\x44")
        if count_near_pixels(middlearea, 900) < 1000:
            return

def take_left_near():
    """
    * Function Name:	take_left_near
    * Input:		None
    * Output:		Takes Left turn
    * Logic:		This function takes a Left turn until
                    the obstacle is not detected i.e. If
                    the obstacle is in range it will turn
                    until it is out of its sight
    * Example Call:	take_left_near()
    """
    while True:
        global_depth_map = get_depth()
        middlearea = global_depth_map[0:479, 160:479]
        contoursright = contours_return(global_depth_map, -10)
        contoursleft = contours_return(global_depth_map, 10)
        door_detection(contoursright, contoursleft, test_cases)
        ser.write("\x45")
        if count_near_pixels(middlearea, 900) < 1000:
            return

def stuck_pos_movement():
    """
    * Function Name:	stuck_pos_movement
    * Input:		None
    * Output:		Removes robot from a stuck position
    * Logic:		When both the middle left and middle right
                    detect an obstacle it takes the mean of the
                    left and right area and the area with lesser
                    mean is the preferable area to go.
    * Example Call:	stuck_pos_movement()
    """
    global_depth_map = get_depth()
    leftarea = global_depth_map[0:479, 0:200]
    rightarea = global_depth_map[0:479, 439:639]
    leftvals = leftarea.mean()
    rightvals = rightarea.mean()
    if leftvals > rightvals:
        print "left"
        take_left_near()
    else:
        print "right"
        take_right_near()

def data_send(left_motor_value, right_motor_value):
    """
    * Function Name:	data_send
    * Input:		left and right speed mode
    * Output:		Sends speed mode of the robot wheels to the Fire bird V
                    for further analysis
    * Logic:		Total 25 different possibilities of speed modes are
                    there according to the vertical frame in which
                    the obstacle is detected and using if else
                    statements proper speed mode is sent.
    * Example Call:	data_send(speed_left,speed_right)
    """
    if left_motor_value == 0:
        if right_motor_value == 0:
            ser.write('\x00')
        elif right_motor_value == 1:
            ser.write('\x01')
        elif right_motor_value == 2:
            ser.write('\x02')
        elif right_motor_value == 3:
            ser.write('\x03')
        elif right_motor_value == 4:
            ser.write('\x04')
    elif left_motor_value == 1:
        if right_motor_value == 0:
            ser.write('\x10')
        elif right_motor_value == 1:
            ser.write('\x11')
        elif right_motor_value == 2:
            ser.write('\x12')
        elif right_motor_value == 3:
            ser.write('\x13')
        elif right_motor_value == 4:
            ser.write('\x14')
    elif left_motor_value == 2:
        if right_motor_value == 0:
            ser.write('\x20')
        elif right_motor_value == 1:
            ser.write('\x21')
        elif right_motor_value == 2:
            ser.write('\x22')
        elif right_motor_value == 3:
            ser.write('\x23')
        elif right_motor_value == 4:
            ser.write('\x24')
    elif left_motor_value == 3:
        if right_motor_value == 0:
            ser.write('\x30')
        elif right_motor_value == 1:
            ser.write('\x31')
        elif right_motor_value == 2:
            ser.write('\x32')
        elif right_motor_value == 3:
            ser.write('\x33')
        elif right_motor_value == 4:
            ser.write('\x34')
    elif left_motor_value == 4:
        if right_motor_value == 0:
            ser.write('\x40')
        elif right_motor_value == 1:
            ser.write('\x41')
        elif right_motor_value == 2:
            ser.write('\x42')
        elif right_motor_value == 3:
            ser.write('\x43')
        elif right_motor_value == 4:
            stuck_pos_movement()

def count_near_pixels(area, dist):
    """
    * Function Name:	count_near_pixels()
    * Input:		area and the distance upto which the obstacle should be detected.
    * Output:		Returns the number of obstacle
    pixels that are in the distance range.
    * Logic:		The depth data is Binary thresholded according to the obstacle
                    detected in its range. Than the NonZeros are counted as
                    they are the obstacle.
    * Example Call:	count_near_pixels()(area,900)
    """
    ret, th3 = cv2.threshold(area, dist / 30, 255, cv2.THRESH_BINARY_INV)
    count = cv2.countNonZero(th3)
    return count

def door_movement(global_depth_map):
    """
    * Function Name:door_movement
    * Input:		global_depth_map
    * Output:		Sends serial code to FireBird V to exit the door.
    * Logic:		The robot exits the door by moving in a direction that
                    appears to be free.
    * Example Call: door_movement(global_depth)
    """
    middlearea = global_depth_map[200:479, 200:439]
    middleval = count_near_pixels(middlearea, 900)
    leftarea = global_depth_map[0:479, 0:100]
    rightarea = global_depth_map[0:479, 539:639]
    leftval = leftarea.mean()
    rightval = rightarea.mean()
    if middleval < 1000:
        print "forward"
        ser.write("\x00")
        time.sleep(0.1)
    else:
        if leftval > rightval:
            print "left"
            take_left()
        else:
            print "right"
            take_right()

def search_wall(direction):
    """
    * Function Name:    search_wall
    * Input:		left/right wall
    * Output:		follows left or right wall
    * Logic:		If left wall is selected for instance then the
                    robot moves along the wall. The robot keeps track of
                    the objects on the left side of frame for left wall
                    and if the frame does not have any object in the range
                    than the robot moves left until it is detected
    * Example Call:	search_wall(0)
    """
    if direction == 0:
        while True:
            global_depth_map = get_depth()
            area = global_depth_map[0:479, 0:319]
            contoursright = contours_return(global_depth_map, -10)
            contoursleft = contours_return(global_depth_map, 10)
            door_detection(contoursright, contoursleft, test_cases)
            ser.write("\x03")
            if count_near_pixels(area, 1800) > 1000:
                break
    elif direction == 1:
        while True:
            global_depth_map = get_depth()
            area = global_depth_map[0:479, 320:639]
            contoursright = contours_return(global_depth_map, -10)
            contoursleft = contours_return(global_depth_map, 10)
            door_detection(contoursright, contoursleft, test_cases)
            ser.write("\x30")
            if count_near_pixels(area, 1800) > 1000:
                break

def regular_movement(global_depth_map):
    """
    * Function Name:	regular_movement
    * Input:		Original depth frame
    * Output:		robot moves without bumping into any obstacle
    * Logic:		The frame is divided in 8 vertical sections.
    Speed mode is selected from the speed_right and speed_left. There are 4 l
    left frames and 4 right frames. The frame loop starts from middle
    and if any frame detects any obstacle break the loop and the
    corresponding data is saved in the speed_left or
    speed_right variable
    * Example Call:	regular_movement(original)
    """
    temp_x = 320
    speed = 4
    for i in xrange(4):
        area = global_depth_map[0:479, temp_x:temp_x+79]
        if count_near_pixels(area, 900) > 1000:
            break
        speed = speed - 1
        temp_x = temp_x + 80
    speed_right = speed
    temp_x = 319
    speed = 4
    for i in xrange(4):
        area = global_depth_map[0:479, temp_x-79:temp_x]
        if count_near_pixels(area, 900) > 1000:
            break
        speed = speed - 1
        temp_x = temp_x - 80
    speed_left = speed
    if speed_left != 0 or speed_right != 0:
        data_send(speed_left, speed_right)
    else:
        search_wall(0)
        ser.write("\x00")

def horizontal_edge(contours):
    """
    * Function Name:horizontal_edge
    * Input:		Contours of edges
    * Output:		Detects actual edges of a door from given contours
    * Logic:		The coordinates of the topmost, bottommost and
                    centroid of edges are calculated using moments.
                    These values are compared with a threshold and returned
                    if they lie above a threshold
    * Example Call:	horizontal_edge(contours)
    """
    area = 500
    thresh_y = 50
    thresh_x = 100
    if cv2.contourArea(contours) > area:
        leftmost = tuple(contours[contours[:, :, 0].argmin()][0])
        rightmost = tuple(contours[contours[:, :, 0].argmax()][0])
        topmost = tuple(contours[contours[:, :, 1].argmin()][0])
        bottommost = tuple(contours[contours[:, :, 1].argmax()][0])
        x_1 = leftmost[0]
        x_2 = rightmost[0]
        y_1 = topmost[1]
        y_2 = bottommost[1]
        if (y_2 - y_1 < thresh_y) and (abs(x_2 - x_1) > thresh_x):
            cv2.line(global_depth_map, leftmost, rightmost, (0, 255, 0), 5)
            left_height = leftmost
            right_height = rightmost
            moment = cv2.moments(contours)
            cxh = int(moment['m10']/moment['m00'])
            return left_height, right_height, cxh
    return 0, 0, 0

def start():
    ser = serial.Serial('/dev/ttyUSB0')	#initialization of serial communication

    ctx = freenect.init()
    dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

    freenect.set_tilt_degs(dev, 20)
    freenect.close_device(dev)
    test_cases = [True, True, True]

    while True:
        global_depth_map = get_depth()	#returns the depth frame
        contoursright = contours_return(global_depth_map, -10)
        contoursleft = contours_return(global_depth_map, 10)
        door_detection(contoursright, contoursleft, test_cases)
        if DOOR_FLAG:
            door_movement(global_depth_map)
        else: regular_movement(global_depth_map)
        cv2.imshow('final', global_depth_map)
        if cv2.waitKey(1) != -1:
            ser.write('\x35')
            ser.close()
            break

    cv2.destroyAllWindows()
