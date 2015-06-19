import cv
from openni import *
import numpy as np

def array2cv(a):
  dtype2depth = {
        'uint8':   cv.IPL_DEPTH_8U,
        'int8':    cv.IPL_DEPTH_8S,
        'uint16':  cv.IPL_DEPTH_16U,
        'int16':   cv.IPL_DEPTH_16S,
        'int32':   cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }

  try:
    nChannels = a.shape[2]
  except:
    nChannels = 1
  cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
          dtype2depth[str(a.dtype)],
          nChannels)
  cv.SetData(cv_im, a.tostring(),
             a.dtype.itemsize*nChannels*a.shape[1])
  return cv_im

cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow("w2", cv.CV_WINDOW_AUTOSIZE)

ctx = Context()
ctx.init()

# Create a depth generator
depth = DepthGenerator()
rgb   = ImageGenerator()

depth.create(ctx)
rgb.create(ctx)

# Set it to VGA maps at 30 FPS
depth.set_resolution_preset(RES_VGA)
depth.fps = 30
rgb.set_resolution_preset(RES_VGA)
rgb.fps = 30

# Start generating
ctx.start_generating_all()

def repeat():

    rgbMap   = np.fromstring(rgb.get_synced_image_map_bgr(),dtype=np.uint8).reshape(480,640,3)
    depthMap2 = np.fromstring(depth.get_raw_depth_map(),dtype=np.uint16).reshape(480,640)
    foo = array2cv(rgbMap)
    cv.ShowImage("w1",cv.fromarray(depthMap2))
    cv.ShowImage("w2",foo)
    nRetVal2 = ctx.wait_one_update_all(rgb)
    cv.WaitKey(100)


while True:
    repeat()
