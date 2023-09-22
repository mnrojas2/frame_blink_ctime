#!/usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

vidname = 'C0014'
vidcap = cv2.VideoCapture('./videos/' + vidname + '.mp4')
total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

pbar = tqdm(desc='READING FRAMES', total=total_frame_count, unit=' frames')
frame_no = 0
last_frame_print = -2

av_crop_frame_list = []
first_frame = False

while(vidcap.isOpened()):
    frame_exists, curr_frame = vidcap.read()
    if frame_exists:
        if first_frame:
            cv2.imwrite("frame"+vidname+".jpg", curr_frame)
            break
        else:
            # Crop the image to the place the LED is. It's hardcoded. Update when position of the LED is set.
            #crop_frame = curr_frame[1507:1507+507,1882:1882+277,:]  # C01 @ 30ms (super original)
            #crop_frame = curr_frame[1507:1507+519,3341:3341+280,:]  # C07 & C08 @ 31ms plus new offset (6 instead of 5)
            #crop_frame = curr_frame[1430:1430+498,3199:3199+270,:]  # C09 @ 31ms plus new offset (6 instead of 5)
            crop_frame = curr_frame[1512:1512+586,3486:3486+354,:]  # C13, C14 @ 33ms plus offset 11,14 respectively
            
            #crop_frame = cv2.GaussianBlur(crop_frame,(201,201),0)
            cv2.imwrite("testframes/frame%d.jpg" % frame_no, crop_frame)
            crop_frame = cv2.GaussianBlur(crop_frame,(251,251),0)
            crop_frame_hsv = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2HSV)
            
            if frame_no == 0:
                new_frame_hsv = 0*crop_frame
            else:
                new_frame_hsv = cv2.subtract(crop_frame_hsv, last_frame_hsv)
            
            av_crop_frame = np.average(new_frame_hsv, axis = (0,1)) #crop_frame_hsv
            av_crop_frame_list.append(av_crop_frame)
            last_frame_hsv = crop_frame_hsv
            last_av_crop = av_crop_frame
    else:
        pbar.close()
        break
    frame_no += 1
    pbar.update(1)

if not first_frame:
    data = np.array(av_crop_frame_list)

    fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)

    # We can set the number of bins with the *bins* keyword argument.
    axs[0].hist(data[:,0], color='red', ec='black', bins=15)
    axs[1].hist(data[:,1], color='green', ec='black', bins=15)
    axs[2].hist(data[:,2], color='blue', ec='black', bins=15)
    # axs[0].axvline(data[-119], color='k', linestyle='dashed', linewidth=1)

    plt.show()
vidcap.release()





