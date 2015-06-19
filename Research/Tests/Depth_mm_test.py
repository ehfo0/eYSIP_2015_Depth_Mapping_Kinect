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
    depth >>= 4
    np.clip(depth, 0, 255, depth)
    mask = depth == 0
    depth[mask] = 255
    depth = depth.astype(np.uint8)
    return depth

np.set_printoptions(threshold=np.nan)
while(True):

    map = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    vid = freenect.sync_get_video()[0]
    mask = (map >= 1100)
    vid[mask,:] = 0

    cv2.imshow('image',vid)
    if(cv2.waitKey(10) != -1): break