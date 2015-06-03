__author__ = 'aniket'

import cv2
import numpy as np

img = cv2.imread('paka.png',0)
kernel = np.ones((5,5),np.uint8)
erosion = cv2.erode(img,kernel,iterations = 1)
dilation = cv2.dilate(img,kernel,iterations = 1)
supera = cv2.dilate(erosion,kernel,iterations=1)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)
#cv2.imshow('soft',erosion)
#cv2.imshow('hard',img)
#cv2.imshow('med',dilation)
#cv2.imshow('super',supera)
#cv2.imshow('opening',opening)
#cv2.imshow('gradient',gradient)
#cv2.imshow('tophat',tophat)
cv2.imshow('blackhat',blackhat)
cv2.waitKey(0)


"""This is an erosion code"""