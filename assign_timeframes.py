#!/usr/bin/env python

##############################################################################
# Reads the files to assign the timestamp of every frame of a recorded video #
##############################################################################

import cv2
import numpy as np
import datetime
import argparse
from tqdm import tqdm

# Initialize parser
parser = argparse.ArgumentParser(description='Extracts frames from the specified video.')
parser.add_argument('vidname', type=str, help='Name of video (mp4 format).')
parser.add_argument('-wr', '--write', action='store_true', default=False, help='Enables saving frames with its corresponding timeframes (times 1000).')

def main():
    args = parser.parse_args()
    # Get data from txts. e.g: 'C0013'
    gpstime = np.genfromtxt('./gpstimetext/gpstime' + args.vidname + '.txt', dtype='str', delimiter='  ')  # Time data from GPS/RaspberryPi
    frame_blink_list = np.genfromtxt('./frametimetext/framelist' + args.vidname + '.txt')                  # Frame data from video

    # Calculate the slope between frames and time # gpstime[0] is skipped since it doesn't appear on video 
    first_blink_time = datetime.datetime.strptime(gpstime[1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000
    last_blink_time = datetime.datetime.strptime(gpstime[-1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000

    first_blink_frame = frame_blink_list[0]
    last_blink_frame = frame_blink_list[-1]

    slope = (last_blink_time - first_blink_time)/(last_blink_frame - first_blink_frame)

    # Extract every frame of the video and assign its timestamp
    vidcap = cv2.VideoCapture('./videos/' + args.vidname + '.mp4')
    total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    pbar = tqdm(desc='ASSIGNING FRAMES', total=total_frame_count, unit=' frames')
    frame_no = 0
    while(vidcap.isOpened()):
        frame_exists, curr_frame = vidcap.read()
        if frame_exists:
            dateframe = first_blink_time + slope * (frame_no - first_blink_frame)
            if args.write:
                cv2.imwrite("timeframes/%d.jpg" % dateframe, curr_frame)
        else:
            pbar.close()
            break
        frame_no += 1
        pbar.update(1)
        
    # Make xlsx or csv file with frames and timestamp for each (float)
        
if __name__=='__main__': main()
