'''
*                       
*                  ================================
*  
*  Author List: Mukesh P
*  Filename: 		obstacle_right_edge_detection.py
*  Date:                June 10, 2015
*  Functions: 		
*  Global Variables:	
*  Dependent library files:     numpy, freenect, cv2
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
'''

import freenect, cv2, numpy as np

'''
* Function Name:	convert_depth
* Input:		depth-> A freenect object                        
* Output:		A freenect object in a different format.
* Logic:		This function accepts a freenect object and 
			converts it into a format which can be 
			displayed on screen.
*                       
* Example Call:	convert_depth(depth)
*
'''

def convert_depth(depth):
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth

'''
* Function Name:	return_left_edges
* Input:		depth-> A freenect object                        
* Output:		A freenect object which contains information about left edges of the obstacles.
* Logic:		This function accepts a freenect object and 
			subtracts consecutive pixels. This will give the edges of obstacle.
*                       
* Example Call:	return_left_edges(depth)
*
'''

def return_left_edges(depth):
	a = depth
	b = np.roll(a,2)
	res = np.subtract(a,b)
	res = np.multiply(res,255)
	return res

'''
* Function Name:	return_right_edges
* Input:		depth-> A freenect object                        
* Output:		A freenect object which contains information about right edges of the obstacles.
* Logic:		This function accepts a freenect object and 
			subtracts consecutive pixels. This will give the edges of obstacle.
*                       
* Example Call:	return_right_edges(depth)
*
'''

def return_right_edges(depth):
	a = depth
	b = np.roll(a,2)
	res = np.subtract(b,a)
	res = np.multiply(res,255)
	return res

'''
* Function Name:	return_contours
* Input:		img-> An image                        
* Output:		A list containing contours of the given image
* Logic:		This function accepts a image and return the contours formed in the image
*                       
* Example Call:	return_contours(img)
*
'''

def return_contours(img):
	_,res = cv2.threshold(img,50,255,cv2.THRESH_BINARY)
	count = 0
	contours, hier = cv2.findContours(res,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	return contours

'''
* Function Name:	return_big_obstacles
* Input:		contours -> A list containing information about all contours in the image                       
* Output:		A list containing information about large obstacles
* Logic:		This function detects a door by calculating the height of the object. Height of the object is detected by calculating the highest and lowest points of a contour. The square root of sum of the squares of this value and the distance of the obstacle will give the height of the object. If the height is above a particular value, it is further processed for checking whether it's a door or not.
*                       
* Example Call:	return_big_obstacles(contours)
*
'''

def return_big_obstacles(contours):
	L = []
	for i in contours:
    		if(cv2.contourArea(i)>500):
        	x,y,w,h = cv2.boundingRect(i)
        		if(h>250):
           			 L.append(i)
    		count+=1
	return L
	

depth = cv2.imread('feed.jpg',0)	#took a feed from Kinect, which is a sample image here

d2 = cv2.bilateralFilter(depth, 10,50,100)	#bilateral filter is applied to remove noise.

res = return_right_edges(d2)
res = cv2.medianBlur(res,5)	#median blur to remove salt and pepper noise

contours = return_contours(res)

door1 = return_big_obstacles(contours)	#to draw the contours

for i in door1:			#to draw a rectangle around the door
	x,y,w,h = cv2.boundingRect(i)
	cv2.rectangle(depth,(x,y),(x+w,y+h),(0,255,0),2)

cv2.imshow('result.jpg',depth) #to show the image till a key is pressed
cv2.waitKey(0)



