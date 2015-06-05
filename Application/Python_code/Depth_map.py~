__author__ = 'aniket'

import freenect
import cv2
import numpy as np
import serial
import time
ser = serial.Serial('/dev/ttyUSB0')


def get_depth():
    a = freenect.sync_get_depth()[0]
    np.clip(a, 0, 2**10 - 1, a)
    a >>= 2
    a = a.astype(np.uint8)
    return a

def return_mean(a):
    median = cv2.medianBlur(a,5)
    mediane = cv2.medianBlur(a,5)
    rect = mediane[0:479, 0:639]
    mean = rect.mean()
    return mean

ctx = freenect.init()
dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

freenect.set_tilt_degs(dev, 30)
time.sleep(1)

freenect.set_tilt_degs(dev, 0)
time.sleep(1)

freenect.close_device(dev)
while(True):
    a = get_depth()


    mean = return_mean(a)

    print mean
    if mean > 240:
            ser.write("\x38")

    else:
        while(return_mean(get_depth())<242):
            ser.write("\x36")

    th3 = cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,3,2)
    contours, hierarchy = cv2.findContours(th3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #ab = freenect.sync_get_video()[0]
    img = cv2.drawContours(a, contours, -1, (0,255,0), 3)
    cv2.imshow('gray',a)
    if cv2.waitKey(1)!=-1:
        ser.write('\x35')
        ser.close()
        break



cv2.destroyAllWindows()