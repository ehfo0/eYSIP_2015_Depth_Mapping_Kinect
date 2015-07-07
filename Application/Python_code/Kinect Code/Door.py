__author__ = 'aniket'
import Kinect
import cv2
while True:
    z = Kinect.get_depth()
    cr = Kinect.contours_return(z,10)
    cl = Kinect.contours_return(z,-10)
    for c in cr:
        Kinect.potential_leftedge(c)
    for c in cl:
        Kinect.potential_rightedge(c)
    Kinect.search_wall()
    cv2.imshow('final', z)
    if cv2.waitKey(1) != -1:
        break