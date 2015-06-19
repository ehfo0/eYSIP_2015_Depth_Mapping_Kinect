import cv2
import cv2.cv as cv
import numpy as np
import freenect
import time

def convert_depth(depth1):
    ##np.clip(depth1, 0, 2**12 - 1, depth1)
   ## depth1 >>= 2
    depth1/=10
    np.clip(depth1, 0, 2**10- 1, depth1)
    depth1 = depth1.astype(np.uint8)
    return depth1

#np.set_printoptions(threshold=np.nan)
#depth = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
#print depth
count = 0

while(1):
    #depth1 = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    depth = freenect.sync_get_depth()[0]
    cv2.imshow('depth_11bit',convert_depth(depth))
    #cv2.imshow('depth_mm',convert_depth(depth1))
    count += 1
    if(count == 100):
        freenect.sync_stop()
        break
    if(cv2.waitKey(10)!=-1): break

depth1 = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
cv2.imshow('depth_mm',convert_depth(depth1))
cv2.waitKey(0)

