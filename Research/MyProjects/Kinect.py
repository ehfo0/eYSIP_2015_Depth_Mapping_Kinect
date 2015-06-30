__author__ = 'aniket'
"""
*
*                  ================================
*
*  Author List:
*  Filename:
*  Date:
*  Functions:
*  Global Variables:
*  Dependent library files:
*
*  e-Yantra - An MHRD project under National Mission on Education using
*  ICT(NMEICT)
*
**************************************************************************
"""

import depth
import freenect
import cv2

ctx = freenect.init()
dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)
freenect.set_tilt_degs(dev, 20)
freenect.close_device(dev)
test_cases = [True, True, True]

while True:
    z = depth.get_depth()	 # returns the depth frame
    contours_right = depth.contours_return(z, -10)
    contours_left = depth.contours_return(z, 10)
    depth.door_detection(contours_right, contours_left, test_cases)
    if depth.flag:
        depth.door_movement()
    else:
        depth.regular_movement()
    cv2.imshow('final', z)
    if cv2.waitKey(1) != -1:
        depth.ser.write('\x35')
        depth.ser.close()
        break

cv2.destroyAllWindows()
