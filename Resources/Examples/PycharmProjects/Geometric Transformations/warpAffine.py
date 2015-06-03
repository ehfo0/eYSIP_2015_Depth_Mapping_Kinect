__author__ = 'aniket'

import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread('paka.jpg', 0)
rows, cols = img.shape

pts1 = np.float32([[50,50],[200,50],[50,200]])
pts2 = np.float32([[10,100],[200,50],[100,250]])

M = cv2.getAffineTransform(pts1,pts2)

dst = cv2.warpAffine(img,M,(rows,cols))

plt.subplot(121), plt.imshow(img), plt.title('Input')
plt.subplot(122), plt.imshow(dst), plt.title('Output')
plt.show()

"""Warping an image"""


