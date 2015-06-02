import numpy as np
import time
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import freenect

ctx=freenect.init()
time.sleep(5)
z=freenect.sync_get_depth()[0]
print z
x=[]
y=[]
zi=[]

for i in range(0,479,5):
    for j in range(0,639,5):
        x.append(i)
        y.append(j)
        zi.append(z[i][j])

#print z[480][640]

#x, y, z = zip(*z)
print len(x)
print len(y)
print len(zi)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x,y,zi)
plt.show()

