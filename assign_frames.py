##############################################################################
# Reads the files to assign the timestamp of every frame of a recorded video #
##############################################################################

import cv2
import numpy as np
import datetime

# Get data from txts.
vidname = 'C0013'
gpstime = np.genfromtxt('gpstimetext/gpstime' + vidname + '.txt', dtype='str', delimiter='  ')  # Time data from GPS/RaspberryPi
frame_blink_list = np.genfromtxt('frametimetext/framelist' + vidname + '.txt')                  # Frame data from video

# Calculate the slope between frames and time # gpstime[0] is skipped since it doesn't appear on video 
first_blink_time = datetime.datetime.strptime(gpstime[1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000
last_blink_time = datetime.datetime.strptime(gpstime[-1], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000

first_blink_frame = frame_blink_list[0]
last_blink_frame = frame_blink_list[-1]

slope = (last_blink_time - first_blink_time)/(last_blink_frame - first_blink_frame)

# Extract every frame of the video and assign its timestamp
vidcap = cv2.VideoCapture('videos/' + vidname + '.mp4')

frame_no = 0
while(vidcap.isOpened()):
    frame_exists, curr_frame = vidcap.read()
    if frame_exists:
        dateframe = first_blink_time + slope * (frame_no - first_blink_frame)
        cv2.imwrite("timeframes/%d.jpg" % dateframe, curr_frame)
    else:
        break
    frame_no += 1