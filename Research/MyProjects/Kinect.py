__author__ = 'aniket'

import freenect
import cv2
import numpy as np

def filter_noise(a,mask,ad,row,col):
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
    ret, mask = cv2.threshold(a,1,255,cv2.THRESH_BINARY_INV)
    mask_1 = mask/255
    ad = a + mask
    blur = filter_noise(a,mask_1,ad,2,2)
    blur = cv2.bilateralFilter(blur, 5, 50, 100)
    return blur

def get_depth():
    a = freenect.sync_get_depth(format = freenect.DEPTH_MM)[0]
    a = a/30
    a = a.astype(np.uint8)
    a = filter_smooth(a)
    return a

while(True):
    frame = get_depth()
    cv2.imshow('depth',frame)
    if cv2.waitKey(1)!=-1:
        freenect.Kill
        break

cv2.destroyAllWindows()
