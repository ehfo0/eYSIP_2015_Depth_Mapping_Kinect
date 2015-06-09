import freenect, cv2, numpy as np
from scipy.ndimage.interpolation import shift
def convert_depth(depth):
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth
np.set_printoptions(threshold=np.nan)
depth = cv2.imread('feed.jpg',0)
d2 = cv2.bilateralFilter(depth, 10,50,100)
a = d2
b = np.roll(a,2)
res = np.subtract(b,a)
res = np.multiply(res,255)
res = cv2.medianBlur(res,5)
cv2.imshow('result.jpg',res)
cv2.waitKey(0)
temp = res

_,res = cv2.threshold(res,50,255,cv2.THRESH_BINARY)

contours, hier = cv2.findContours(res,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(temp, contours, 2, (0,255,0), 3)
cv2.imshow('result.jpg',res)
cv2.waitKey(0)



