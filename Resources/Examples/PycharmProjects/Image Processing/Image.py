
import cv2
import numpy as np
cap = cv2.VideoCapture(0)

def nothing(x):
    pass

cv2.namedWindow('image')

cv2.createTrackbar('H1','image',0,255,nothing)
cv2.createTrackbar('S1','image',0,255,nothing)
cv2.createTrackbar('V1','image',0,255,nothing)
cv2.createTrackbar('H2','image',0,255,nothing)
cv2.createTrackbar('S2','image',0,255,nothing)
cv2.createTrackbar('V2','image',0,255,nothing)

while(1):

    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h1 = cv2.getTrackbarPos('H1','image')
    s1 = cv2.getTrackbarPos('S1','image')
    v1 = cv2.getTrackbarPos('V1','image')
    h2 = cv2.getTrackbarPos('H2','image')
    s2 = cv2.getTrackbarPos('S2','image')
    v2 = cv2.getTrackbarPos('V2','image')
    lower_blue = np.array([h1,s1,v1])
    upper_blue = np.array([h2,s2,v2])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    res = cv2.bitwise_and(frame,frame,mask = mask)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    k = cv2.waitKey(5) & 0xFF
    if  k == 27:
        break

cv2.destroyAllWindows()


"""This code filters colors as per our choice"""