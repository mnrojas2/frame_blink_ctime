import numpy as np
from datetime import datetime
import time

gpstime = np.genfromtxt('blinkgpstime.txt', dtype='str', delimiter='  ')

for t in gpstime:
    print(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())