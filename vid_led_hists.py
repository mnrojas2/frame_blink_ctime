#!/usr/bin/env python

"""
# Read an info file, then plot an histogram with its data.
# Author: mnrojas2
"""

import os
import argparse
import numpy as np
from matplotlib import pyplot as plt


def main():
    # Get data from txt file
    data = np.loadtxt(args.file, delimiter=',')

    # Split data in variables
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

    axs[0].title.set_text('Min')
    axs[1].title.set_text('Max')
    axs[2].title.set_text('Max-Min')
    axs[3].title.set_text('STD')
    plt.show()
    
    
if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(description='Read an info file, then plot an histogram with its data.')
    parser.add_argument('file', type=str, help='Name of the txt file containing timedata to plot.')

    # Get parser arguments
    args = parser.parse_args()
    
    # Main
    main()