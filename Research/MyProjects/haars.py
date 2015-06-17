"""
*
*                  ================================
*
*  Author List: Mukesh P, Aniket Patel
*  Filename: 		obstacle_right_edge_detection.py
*  Date:                June 10, 2015
*  Functions:
*  Global Variables:
*  Dependent library files:     numpy, freenect, cv2
*
*  e-Yantra - An MHRD project under National Mission on Education using
*  ICT(NMEICT)
*
**************************************************************************
*
*
*
"""

import numpy as np
import cv2
import freenect
door_cascade = cv2.CascadeClassifier('cascade.xml') #Classifier in which all the nodes and hidden layers are defined

def door_detect(gray):
    """
    * Function Name:	door_detect
    * Input:		grayscale image
    * Output:		grayscale image with doors detected
    * Logic:		This function gives a grayscale output by drawing rectangles over the image where doors are detected
    * Example Call:	door_detect(gray)
    """
    doors = door_cascade.detectMultiScale(gray, 2, 5) #Scale can be varied and it detects the doors
    for (x,y,w,h) in doors:
        cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2) #draws rectangles around the doors
while(1):

    img = freenect.sync_get_video()[0] # gets the frame
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # converts to grayscale image
    door_detect(gray)   # detects doors
    cv2.imshow('img',gray)  #displays output
    if cv2.waitKey(1)!=-1:  #to finish the task
        freenect.Kill
        break

cv2.destroyAllWindows()