#!/usr/bin/env python

##################################################################
# Checks every frame of a video to find out if a LED is blinking #
##################################################################

import cv2
import numpy as np
import argparse
from matplotlib import pyplot as plt
from tqdm import tqdm

# Initialize parser
parser = argparse.ArgumentParser(description='Extracts frames from the specified video.')
parser.add_argument('vidname', type=str, help='Name of video (mp4 format).')
parser.add_argument('-wr', '--write', action='store_true', default=False, help='Enables saving frames when LED is ON.')

def main():
    args = parser.parse_args()
    
    # Load the video e.g: 'C0014'
    vidcap = cv2.VideoCapture('videos/' + args.vidname + '.mp4')
    total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Set counters for all frames and for last frame with a peak (LED turned on)
    pbar = tqdm(desc='READING FRAMES', total=total_frame_count, unit=' frames')
    frame_no = -1

    # Set lists to save data
    frame_blink_list = []
    frame_stats_list = []

    # Whileloop
    while(vidcap.isOpened()):
        # Read if there's a frame to continue
        frame_exists, curr_frame = vidcap.read()
        if frame_exists: # and frame_no < 150
            # Crop the whole image to focus only on the LED part
            #ncrop_frame = curr_frame[1507:1507+507,1882:1882+277,:]  # C01 @ 30ms (super original)
            #ncrop_frame = curr_frame[1507:1507+519,3341:3341+280,:]  # C07 & C08 @ 31ms plus new offset (6 instead of 5)
            #ncrop_frame = curr_frame[1430:1430+498,3199:3199+270,:]  # C09 @ 31ms plus new offset (6 instead of 5)
            ncrop_frame = curr_frame[1512:1512+586,3486:3486+354,:]  # C13, C14 @ 33ms plus offset 11,14 respectively
            
            # Apply a Gaussian blur and convert the matrix from RGB to HSV
            ncrop_frame = cv2.GaussianBlur(ncrop_frame,(251,251),0)
            ncrop_frame_hsv = cv2.cvtColor(ncrop_frame, cv2.COLOR_BGR2HSV)
            
            # If the whileloop is starting, just update the frames but don't do anything
            if frame_no < 0:
                ocrop_frame = ncrop_frame
                ccrop_frame = ncrop_frame
                
                ocrop_frame_hsv = ncrop_frame_hsv
                ccrop_frame_hsv = ncrop_frame_hsv
                
            elif frame_no >= 0:
                # Get 2nd to last frame, last frame and current frame and name them as "old, current, new" and calculate their average values.
                av_crop_frame_o = np.average(ocrop_frame_hsv, axis = (0,1))
                av_crop_frame_c = np.average(ccrop_frame_hsv, axis = (0,1))
                av_crop_frame_n = np.average(ncrop_frame_hsv, axis = (0,1))
                
                # Find the minimum and maximum values for ([2]: HS"V") and substract it from all frame samples.
                av_crop_min = np.min([av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]])
                av_crop_max = np.max([av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]])
                av_crop_frame_o[2] -= av_crop_min
                av_crop_frame_c[2] -= av_crop_min
                av_crop_frame_n[2] -= av_crop_min
                
                # Save data to analysis if necessary.
                led_frame_stats = np.hstack((frame_no, np.round(av_crop_min,3), np.round(av_crop_max,3), np.round(av_crop_max-av_crop_min,3), np.std((av_crop_frame_n[2], av_crop_frame_c[2], av_crop_frame_o[2]))))
                frame_stats_list.append(led_frame_stats)

                # Get the standard deviation between the 3 frame samples. 
                if np.std((av_crop_frame_o[2], av_crop_frame_c[2], av_crop_frame_n[2])) > 1.1: # Arbitrary value after experimentation. If something is failing, it could be this.
                    if av_crop_frame_o[2] < av_crop_frame_c[2] and av_crop_frame_n[2] < av_crop_frame_c[2]:
                        if args.write:
                            cv2.imwrite("frames/frame%d.jpg" % (frame_no), ccrop_frame)
                        frame_blink_list.append(frame_no)
                    
                # Update old frames for next loop.
                ocrop_frame_hsv = ccrop_frame_hsv
                ccrop_frame_hsv = ncrop_frame_hsv
                ocrop_frame = ccrop_frame
                ccrop_frame = ncrop_frame
            
        else:
            pbar.close()
            break
        frame_no += 1
        pbar.update(1)
    vidcap.release()

    # Save the list of frames that have the LED turned on.
    np.savetxt('./frametimetext/framelist'+ args.vidname +'.txt', frame_blink_list, fmt='%1.0f')
    np.savetxt('./info/info'+ args.vidname +'.txt', frame_stats_list, fmt='%1.4f', delimiter=',')

    plt.show()
    
if __name__=='__main__': main()
    