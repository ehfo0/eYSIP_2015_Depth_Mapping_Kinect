"""
*                       
*                  ================================
*  
*  Author List: Mukesh P, Aniket Patel
*  Filename: 		Depth_map.py
*  Date:                June 18, 2015
*  Functions: 		get_depth, return_mean
*  Global Variables:	
*  Dependent library files:     numpy, freenect, cv2, serial, time
*  This software is made available on an AS IS WHERE IS BASIS. 
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*  
*  e-Yantra - An MHRD project under National Mission on Education using 
*  ICT(NMEICT)
*
**************************************************************************
*     
*
*
"""

import freenect
import cv2
import numpy as np
import serial
import time
ser = serial.Serial('/dev/ttyUSB0')	#serial communication initialization


def get_depth():
    """
    * Function Name:	get_depth
    * Input:		None                        
    * Output:		Returns the depth information from pixel values of 0 to 255
    * Logic:		It gets the depth from kinect whose values lie in range of 0 to above 2000. It clips and left shifts the data to get 				all the values between 0 and 255.
    * Example Call:	get_depth()
    """
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    return a

def return_mean(a):
    """
    * Function Name:	return_mean
    * Input:		Depth Frame or any other matrix.                        
    * Output:		Returns mean of the frame
    * Logic:		It reduces the noise and calculates the mean of the pixel values in the frame using mean() function
    * Example Call:	return_mean(a)
    """
    median = cv2.medianBlur(a,5)
    mediane = cv2.medianBlur(a,5)
    rect = mediane[0:479, 0:639]
    mean = rect.mean()
    return mean

ctx = freenect.init()	#initialize freenect
dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)	#open Kinect Device

freenect.set_tilt_degs(dev, 30)	#Tilts kinect to 30 degrees
time.sleep(1)	

freenect.set_tilt_degs(dev, 0)	#Tilts kinect to 0 degree
time.sleep(1)

freenect.close_device(dev)	#closes Kinect
while(True):
    a = get_depth()	#gets the depth data from Kinect
    mean = return_mean(a)	#returns the mean of the depth data
    if mean > 240:	
            ser.write("\x38")	#if the front area has more depth than the threshold than the robot will move forward
    else:
        while(return_mean(get_depth())<242):
            ser.write("\x36")	#rotate till the threshold is crossed

    th3 = cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,3,2)	#Binary threshold
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)	#find contours
    img = cv2.drawContours(a, contours, -1, (0,255,0), 3)	#draw contours in the frame
    cv2.imshow('gray',a)	#displays the image with contours
    if cv2.waitKey(1)!=-1:	#if key is pressed terminate the program
        ser.write('\x35')
        ser.close()
        break



cv2.destroyAllWindows()	#closes all windows
