__author__ = 'aniket'

import cv2
import numpy as np

img = cv2.imread('paka.jpg')

res = cv2.resize(img,None,fx=0.5,fy=0.5,interpolation = cv2.INTER_CUBIC)

cv2.imshow('yo',res)
height, width = img.shape[:2]
res = cv2.resize(img,(2*width, 1*height), interpolation=cv2.INTER_LINEAR)

cv2.imshow('po',res)
cv2.waitKey(0)

"""This code is for resizing any image"""