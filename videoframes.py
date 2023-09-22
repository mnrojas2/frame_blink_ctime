##################################################################
# Checks every frame of a video to find out if a LED is blinking #
##################################################################

import cv2
import numpy as np
from matplotlib import pyplot as plt

vidname = 'C0034'
vidcap = cv2.VideoCapture('videos/' + vidname + '.mp4')

frame_no = 0
last_frame_print = -2
tot_interpol = 0

frame_blink_list = []
av_frames = []

while(vidcap.isOpened()):
    frame_exists, curr_frame = vidcap.read()
    if frame_exists:
        # Crop the image to the place the LED is. It's hardcoded. Update when position of the LED is set.
        #crop_frame = curr_frame[1309:1309+316,1573:1573+170,:]  # C25 @ 30ms (original)
        #crop_frame = curr_frame[1424:1424+471,2033:2033+240,:]  # C27 @ 30ms
        #crop_frame = curr_frame[1432:1432+395,2153:2153+214,:]  # C30 @ 31ms
        #crop_frame = curr_frame[1424:1424+414,1768:1768+235,:]  # C31 @ 31ms
        #crop_frame = curr_frame[1417:1417+414,1697:1697+235,:]  # C32 @ 31ms
        crop_frame = curr_frame[1477:1477+459,2054:2054+252,:]  # C33 @ 31ms plus new offset (6 before 5)
        
        # Calculate the average tone (r,g,b) of the cropped image.
        crop_frame = cv2.GaussianBlur(crop_frame,(251,251),0)
        crop_frame2 = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2HSV)
        av_crop_frame = np.average(crop_frame2, axis = (0,1))
        # 
        if av_crop_frame[2] > 220: #av_crop_frame[1] > 208 and      # Hardcoded. Update when more videos can be made in different environments.
            #C25: r<31, g>45, b>120 
            #C27: r<23, g>25, b>71
            #C30: r<23, g>22, b>80
            #C31: r<34, g>48, b>233
            #C32: b>234
            #C33: r<18.5, g>70, b>226, hsv: ?,208,220
            #C34: 
            if last_frame_print == frame_no - 1:
                print("NEED INTERPOLATION at frames", last_frame_print, "and", frame_no)
                tot_interpol += 1
            else:
                frame_blink_list.append(frame_no)
            cv2.imwrite("frames/frame%d.jpg" % frame_no, crop_frame)
            #cv2.imwrite("frames/frame%dv.jpg" % frame_no, crop_frame[:,:,2])
            last_frame_print = frame_no
            av_frames.append(av_crop_frame)
    else:
        break
    frame_no += 1

# Save the list of frames that have the LED turned on.
np.savetxt('frametimetext/framelist'+ vidname +'.txt', frame_blink_list)
print("Total de interpolaciones", tot_interpol)

data = np.array(av_frames)
fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)

# We can set the number of bins with the *bins* keyword argument.
axs[0].hist(data[:,0], color='red', ec='black', bins=15)
axs[1].hist(data[:,1], color='green', ec='black', bins=15)
axs[2].hist(data[:,2], color='blue', ec='black', bins=15)
# axs[0].axvline(data[-119], color='k', linestyle='dashed', linewidth=1)

plt.show()
vidcap.release()





