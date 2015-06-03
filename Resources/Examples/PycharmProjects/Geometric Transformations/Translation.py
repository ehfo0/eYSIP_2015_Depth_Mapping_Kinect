__author__ = 'aniket'

import cv2
import numpy as np

img = cv2.imread('paka.jpg',0)
rows,cols = img.shape

M = np.float32([[1,0,1000],[0,1,50]])
dst = cv2.warpAffine(img, M, (cols,rows))

cv2.imshow('img',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

"""This code translates the image to a new position"""
