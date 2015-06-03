__author__ = 'aniket'

import cv2
img = cv2.imread('paka.jpg',0)
rows, cols = img.shape

M = cv2.getRotationMatrix2D((cols/2,rows/2),90,0.5)
dst = cv2.warpAffine(img, M, (cols,rows))

cv2.imshow('yo',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

"""This code rotates the image by specified degrees"""
