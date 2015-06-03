__author__ = 'aniket'

import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('paka.jpg')
kernel = np.append([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [2, 2, 2, 2, 2], [-1, -1, -1, -1, -1]],[[-1, -1, -1, -1, -1]], axis = 0)
print kernel
dst = cv2.filter2D(img,-1,kernel)

plt.subplot(121), plt.imshow(img), plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122), plt.imshow(dst), plt.title('Averaging')
plt.xticks([]), plt.yticks([])
plt.show()

"""This code blurs the image using kernels"""
