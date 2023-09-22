#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt

data = np.loadtxt('./info/infoC0014.txt', delimiter=',')

frame_no = data[:,0]
average_min = data[:,1]
average_max = data[:,2]
average_diff = data[:,3] # max-min
average_std = data[:,4]

fig, axs = plt.subplots(1, 4, sharey=True, tight_layout=True, figsize=(15, 5))
axs[0].hist(average_min, color='magenta', ec='black', bins=9)
axs[1].hist(average_max, color='yellow', ec='black', bins=9)
axs[2].hist(average_diff, color='cyan', ec='black', bins=9)
axs[3].hist(average_std, color='lightgreen', ec='black', bins=9)
plt.show()