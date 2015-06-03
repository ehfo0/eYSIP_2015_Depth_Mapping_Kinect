__author__ = 'aniket'

import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('paka.jpg')

blur = cv2.bilateralFilter(img, 9, 75, 75)
median = cv2.medianBlur(img,5)

plt.subplot(221), plt.imshow(img), plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(222), plt.imshow(blur), plt.title('Blurred')
plt.xticks([]), plt.yticks([])
plt.subplot(223), plt.imshow(median), plt.title('Median')
plt.xticks([]), plt.yticks([])
plt.show()
