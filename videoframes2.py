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

while(vidcap.isOpened()):
    frame_exists, curr_frame = vidcap.read()
    if frame_exists:
        ncrop_frame = curr_frame[1477:1477+459,2054:2054+252,:]  # C33 & C34 @ 31ms plus new offset (6 before 5)
        
        # Gaussian blur + RGB2HSV
        ncrop_frame = cv2.GaussianBlur(ncrop_frame,(251,251),0)
        ncrop_frame_hsv = cv2.cvtColor(ncrop_frame, cv2.COLOR_BGR2HSV)
        
        if frame_no == 0:
            ocrop_frame = ncrop_frame
            ccrop_frame = ncrop_frame
            
            ocrop_frame_hsv = ncrop_frame_hsv
            ccrop_frame_hsv = ncrop_frame_hsv
            
        nc_new_frame = cv2.absdiff(ncrop_frame_hsv, ccrop_frame_hsv)
        no_new_frame = cv2.absdiff(ncrop_frame_hsv, ocrop_frame_hsv)
        co_new_frame = cv2.absdiff(ccrop_frame_hsv, ocrop_frame_hsv)
        
        av_crop_frame_nc = np.average(nc_new_frame, axis = (0,1)) #crop_frame_hsv
        av_crop_frame_no = np.average(no_new_frame, axis = (0,1))
        av_crop_frame_co = np.average(co_new_frame, axis = (0,1))
        
        # comparar old and new / current and new -> quien tenga el valor más grande es el ganador -> se salta el otro
        
        if av_crop_frame_co[2] > 75 and av_crop_frame_nc[2] > 75:      # Hardcoded. Update when more videos can be made in different environments.
            if last_frame_print == frame_no - 1:
                print("NEED INTERPOLATION at frames", last_frame_print-1, "and", frame_no-1)
                tot_interpol += 1
            else:
                frame_blink_list.append(frame_no-1)
                
            '''
            if NO > CO:
                frame_blink_list.append(frame_no)
            elif CO > NO:
                frame_blink_list.append(frame_no-1)
            '''
            
            cv2.imwrite("frames/framesNC/frame%dNC.jpg" % (frame_no-1), cv2.absdiff(ncrop_frame,ccrop_frame)) # ccrop_frame
            cv2.imwrite("frames/framesNO/frame%dNO.jpg" % (frame_no-1), cv2.absdiff(ncrop_frame,ocrop_frame)) # ccrop_frame
            cv2.imwrite("frames/framesCO/frame%dCO.jpg" % (frame_no-1), cv2.absdiff(ccrop_frame,ocrop_frame)) # ccrop_frame
            #cv2.imwrite("frames/frame%dv.jpg" % frame_no, crop_frame[:,:,2])
            last_frame_print = frame_no
            
        ocrop_frame_hsv = ccrop_frame_hsv
        ccrop_frame_hsv = ncrop_frame_hsv
        
        ocrop_frame = ccrop_frame
        ccrop_frame = ncrop_frame
        
    else:
        break
    frame_no += 1

# Save the list of frames that have the LED turned on.
np.savetxt('frametimetext/framelist'+ vidname +'.txt', frame_blink_list)
print("Total de interpolaciones", tot_interpol)

plt.show()
vidcap.release()





