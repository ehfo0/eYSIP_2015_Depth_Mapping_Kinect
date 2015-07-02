import cv2, os, sys
import numpy as np
from PIL import Image


filelist = os.listdir('.')

#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')



for filename in filelist:
	if "neg" in filename:  # only process pictures
		input_image = cv2.imread(filename)
		input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
		#facesInInputImage = face_cascade.detectMultiScale(input_image, 1.02, 10)
		newname = filename
		#for (x, y, w, h) in facesInInputImage:
			#input_image = input_image[y:y+h, x:x+w]
		input_image = cv2.resize(input_image, (200, 200), interpolation = cv2.INTER_CUBIC)
			#cv2.rectangle(input_image, (x, y), (x+w, y+h), (0,255,0), 3)
		cv2.imwrite(newname,input_image)


cv2.waitKey(0)

cv2.destroyAllWindows()





    
