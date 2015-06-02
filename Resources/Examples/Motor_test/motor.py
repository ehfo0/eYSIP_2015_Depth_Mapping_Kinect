import freenect
import time
import cv2

TILT_MAX = 30
TILT_STEP = 10
TILT_START = 0

freenect.error_open_device()

ctx = freenect.init()
dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)

if not dev:
    freenect.error_open_device()

print "Starting TILT Cycle"
for tilt in xrange(TILT_START, TILT_MAX+TILT_STEP, TILT_STEP):
    print "Setting TILT: ", tilt
    freenect.set_tilt_degs(dev, tilt)
    time.sleep(3)

    cv2.set

freenect.set_tilt_degs(dev, 0)
