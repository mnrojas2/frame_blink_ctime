#!/usr/bin/env python

"""
# Reads the files to assign the timestamp of every frame of a recorded video #
# Author: mnrojas2
"""

import os
import argparse
import cv2 as cv
import numpy as np
import datetime as dt
from tqdm import tqdm


def main():
    # Get name of the file only
    vidfile = os.path.basename(args.vidname)[:-4]
    
    # Get data from txts. e.g: 'C0013'
    gpstime = np.genfromtxt('./gpstimetext/gpstime' + vidfile + '.txt', dtype='str', delimiter='  ')  # Time data from GPS/RaspberryPi
    frame_blink_list = np.genfromtxt('./frametimetext/framelist' + args.vidname + '.txt')             # Frame data from video

    # Calculate the slope between frames and time # gpstime[0] is skipped since it doesn't appear on video 
    first_blink_time = dt.datetime.strptime(gpstime[1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000
    last_blink_time = dt.datetime.strptime(gpstime[-1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000

    first_blink_frame = frame_blink_list[0]
    last_blink_frame = frame_blink_list[-1]

    slope = (last_blink_time - first_blink_time)/(last_blink_frame - first_blink_frame)

    # Extract every frame of the video and assign its timestamp
    vidcap = cv.VideoCapture('./videos/' + args.vidname + '.mp4')
    
    # Get total frame count and frames per second
    total_frame_count = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv.CAP_PROP_FPS)

    # Make a list with the timestamp of all frames
    vidtimes = np.arange(total_frame_count)/fps
    
    ################################
    vidtime_blinks = [0, 4]
    gpstime_blinks = [0, 4]
    ################################
    
    gps_timeframes = np.interp(vidtimes, vidtime_blinks, gpstime_blinks)

    pbar = tqdm(desc='ASSIGNING FRAMES', total=total_frame_count, unit=' frames')
    frame_no = 0
    while(vidcap.isOpened()):
        frame_exists, curr_frame = vidcap.read()
        if not frame_exists:
            pbar.close()
            break
        
        dateframe = first_blink_time + slope * (frame_no - first_blink_frame)
        if args.write:
            cv.imwrite("timeframes/%d.jpg" % dateframe, curr_frame)
            
        frame_no += 1
        pbar.update(1)
        
    # Make xlsx or csv file with frames and timestamp for each (float)
    

if __name__=='__main__': 
    # Initialize parser
    parser = argparse.ArgumentParser(description='Extracts frames from the specified video.')
    parser.add_argument('vidname', type=str, help='Directory of video (mp4 format).')
    parser.add_argument('-wr', '--write', action='store_true', default=False, help='Enables saving frames with its corresponding timeframes (times 1000).')

    # Get parser arguments
    args = parser.parse_args()
    
    # Main    
    main()
