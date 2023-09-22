##################################################################
# Checks every frame of a video to find out if a LED is blinking #
##################################################################

import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the video
vidname = 'C0035'
vidcap = cv2.VideoCapture('videos/' + vidname + '.mp4')

# Set counters for all frames and for last frame with a peak (LED turned on)
frame_no = -1
last_frame_print = frame_no-2

# Set lists to save data
frame_blink_list = []
another_list = []

# Whileloop
while(vidcap.isOpened()):
    # Read if there's a frame to continue
    frame_exists, curr_frame = vidcap.read()
    if frame_exists: # and frame_no < 150
        # Crop the whole image to focus only on the LED part
        #ncrop_frame = curr_frame[1477:1477+459,2054:2054+252,:]  # C33 & C34 @ 31ms plus new offset (6 instead of 5)
        ncrop_frame = curr_frame[1489:1489+510,3347:3347+290,:]  # C35 & C36 @ 31ms plus new offset (6 instead of 5)
        
        # Apply a Gaussian blur and convert the matrix from RGB to HSV
        ncrop_frame = cv2.GaussianBlur(ncrop_frame,(251,251),0)
        ncrop_frame_hsv = cv2.cvtColor(ncrop_frame, cv2.COLOR_BGR2HSV)
        
        # If the whileloop is starting OR a frame is being skipped, just update the frames but don't do anything
        if frame_no < 0 or skip_next == True:
            ocrop_frame = ncrop_frame
            ccrop_frame = ncrop_frame
            
            ocrop_frame_hsv = ncrop_frame_hsv
            ccrop_frame_hsv = ncrop_frame_hsv
            
            skip_next = False
        
        # If the 
        elif frame_no >= 0 and skip_next == False:
            # Get 2nd to last frame, last frame and current frame and name them as "old, current, new" and calculate their average values.
            av_crop_frame_o = np.average(ocrop_frame_hsv, axis = (0,1))
            av_crop_frame_c = np.average(ccrop_frame_hsv, axis = (0,1))
            av_crop_frame_n = np.average(ncrop_frame_hsv, axis = (0,1))
            
            # Find the minimum and maximum values for ([2]: HS"V") and substract it from all
            av_crop_min = np.min([av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]])
            av_crop_max = np.max([av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]])
            av_crop_frame_o[2] -= av_crop_min
            av_crop_frame_c[2] -= av_crop_min
            av_crop_frame_n[2] -= av_crop_min
            
            # Save data to analysis if necessary
            list_txt = np.hstack((frame_no, np.round(av_crop_min,3), np.round(av_crop_max,3), np.round(av_crop_max-av_crop_min,3), np.std((av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]))))
            #print((frame_no, av_crop_min, av_crop_max, av_crop_max-av_crop_min))
            another_list.append(list_txt)
            print(frame_no, np.std((av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2])))
            
            # Define threshold as an adaptative thing
            av_threshold = 115
            
            # Compare old and current averages to a set threshold
            if av_crop_frame_o[2] < av_threshold < av_crop_frame_c[2]: #C33/34: 115, #C35: 115, #C36: 85
                if av_crop_frame_c[2] >= av_crop_frame_n[2]:
                    cv2.imwrite("frames/frame%d.jpg" % (frame_no), ccrop_frame) # ccrop_frame
                    frame_blink_list.append(frame_no)
                elif av_crop_frame_c[2] < av_crop_frame_n[2]:
                    cv2.imwrite("frames/frame%d.jpg" % (frame_no+1), ncrop_frame)
                    frame_blink_list.append(frame_no+1)
                    skip_next = True
                
            # Update old frames for next loop
            ocrop_frame_hsv = ccrop_frame_hsv
            ccrop_frame_hsv = ncrop_frame_hsv
            ocrop_frame = ccrop_frame
            ccrop_frame = ncrop_frame
        
    else:
        break
    frame_no += 1

# Save the list of frames that have the LED turned on.
np.savetxt('frametimetext/framelist'+ vidname +'.txt', frame_blink_list)
np.savetxt(vidname+'list.txt', another_list, fmt='%1.4f', delimiter=',')

plt.show()
vidcap.release()





