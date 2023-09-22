import numpy as np
from datetime import datetime

gpstime = np.genfromtxt('./gpstimetext/gpstimeC0014.txt', dtype='str', delimiter='  ')

for t in gpstime:
    print(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())