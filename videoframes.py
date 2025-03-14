#!/usr/bin/env python

"""
# Produce a list with all frames where the LED is on
# Author: mnrojas2
"""

import os
import argparse
import cv2 as cv
import numpy as np
import datetime as dt
import re
from scipy.interpolate import interp1d
from tqdm import tqdm


def load_ledlogfile(file):
    # Load rfmeasure file
    filetxt = open(file, 'r')
    cols = filetxt.read()
    all_lines = cols.split('\n')

    data_rows = []

    # Read txt data and save in list
    for line in all_lines:
        if line != '' and line[0] != '#':
            # LastLEDState,LEDColor
            rpi_time, led_color = line.split(',')
            # Convert datetime to timestamp
            try:
                time_dt = dt.datetime.strptime(rpi_time, "%Y:%m:%d:%H:%M:%S.%f").timestamp()
            except ValueError:
                time_dt = dt.datetime.strptime(rpi_time, "%Y:%m:%d:%H:%M:%S").timestamp()

            data_rows.append([time_dt, led_color])

    # Convert data list into numpy array
    return data_rows


def main():
    list_frames = args.get_frames
    
    # Get name of the file only
    vidfile = os.path.basename(args.vidname)[:-4]
    
    try:
        new_list = [int(os.path.splitext(x.replace('frame', ''))[0]) for x in os.listdir(frames_path)]
        new_list.sort()
    except:
        new_list = []    
    
    # Load the video e.g: 'C0014'
    vidcap = cv.VideoCapture(args.vidname)
    
    # Get total frame count and frames per second
    total_frame_count = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv.CAP_PROP_FPS)

    # Make a list with the timestamp of all frames
    vidtimes = np.arange(total_frame_count)/fps

    # Set counters for all frames and for last frame with a peak (LED turned on)
    pbar = tqdm(desc='READING FRAMES', total=total_frame_count, unit=' frames')
    frame_no = -1

    # Set lists to save data
    frame_blink_list = []
    frame_stats_list = []
    
    # Create output folders if they weren't created yet
    frames_path = os.path.normpath(os.path.dirname(args.vidname))+'/'+vidfile
    if not os.path.exists(frames_path):
        os.mkdir(frames_path)

    # Whileloop
    while(vidcap.isOpened()):
        # Get a frame from the video
        frame_exists, curr_frame = vidcap.read()
        if frame_exists: # and frame_no < 150
            if args.first_frame:
                cv.imwrite(f"{args.vidname[:-4]}.jpg", curr_frame)
                break
            
            elif list_frames != [] and (frame_no+1) in list_frames:
                cv.imwrite(f"{frames_path}/frame{(frame_no+1)}.jpg", curr_frame)
                list_frames.remove((frame_no+1))
                if len(list_frames) == 0:
                    break
            
            
            else:
                # Crop the frame to get only the LED position
                ncrop_frame = curr_frame[1677:,3466:,:] 
                
                if args.cropped_frames and (frame_no+1) in new_list:
                    cv.imwrite(f"{frames_path}/frame{(frame_no+1)}.jpg", ncrop_frame)
                
                # Apply a Gaussian blur and convert the matrix from RGB to HSV
                ncrop_frame_gss = cv.GaussianBlur(ncrop_frame,(251,251),0)
                ncrop_frame_hsv = cv.cvtColor(ncrop_frame_gss, cv.COLOR_BGR2HSV)
                    
                if frame_no >= 0:
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
                        # If the middle frame has the highest value, then a peak is found
                        if av_crop_frame_o[2] < av_crop_frame_c[2] and av_crop_frame_n[2] < av_crop_frame_c[2]:
                            # Save the image
                            cv.imwrite(f"{frames_path}/frame{frame_no}.jpg", ccrop_frame)
                            
                            # Get the color of the frame
                            if av_crop_frame_c[0] < 10 or 140 < av_crop_frame_c[0]: 
                                led_col = 'r' 
                            elif 30 < av_crop_frame_c[0] < 100:
                                led_col = 'g'
                            else:
                                led_col = 'undefined'
                            
                            # Save the frame name, video time and color defined
                            print('\n', frame_no, dt.timedelta(seconds=vidtimes[frame_no]))
                            frame_blink_list.append([frame_no, dt.timedelta(seconds=vidtimes[frame_no]), led_col])
                        
                    # Update old frames for next loop.
                    ocrop_frame_hsv = ccrop_frame_hsv
                    ccrop_frame_hsv = ncrop_frame_hsv
                    # ocrop_frame = ccrop_frame
                    ccrop_frame = ncrop_frame_gss
                    
                # If the whileloop is starting, just update the frames but don't do anything
                else:
                    # ocrop_frame = ncrop_frame
                    ccrop_frame = ncrop_frame_gss
                    
                    ocrop_frame_hsv = ncrop_frame_hsv
                    ccrop_frame_hsv = ncrop_frame_hsv
                
        else: break
        
        frame_no += 1
        pbar.update(1)
    pbar.close()
    vidcap.release()

    # Save the list of frames that have the LED turned on.
    np.savetxt(f"{frames_path}_blinks.txt", frame_blink_list, fmt= '%s', delimiter=',', header="name,vidtime,color")
    
    # Save data from the comparison between contiguous frames in relation with the brightness
    np.savetxt(f"{frames_path}_stats.txt", frame_stats_list, fmt='%1.4f', delimiter=',', header="frame,min,max,range,std")

    # Get GPStime and led data from logfile
    gpstime_log = load_ledlogfile('./vids/logfile_1215_182923_camera.txt')
    
    ### Remove points that are undefined, keep those that are to be sure good
    time_blinks = np.array([x[1].total_seconds() for x in frame_blink_list])
    
    tb_diff = np.diff(time_blinks)
    # Get blink timestamps from video data
    for frame_data in frame_blink_list:
        frame_num = frame_data[0]
        frame_timedelta = frame_data[1].total_seconds()
        frame_ledcolor = frame_data[2]
        
        if frame_ledcolor == 'undefined':
            # remove row #
            cdad = 0
            
    

    ### Sync gpstime data with video points
    # if gpstime[0].color == frame_data.color -> it's sync else move until both are green
    
    # Interpolate frames
    """
    # Fit a projection to adjust slopes
    coefficients = np.polyfit(gpstime, time_blinks, deg=1)  # Fit a 1st-degree polynomial (linear)
    proj_timeblinks = np.polyval(coefficients, gpstime)  # Adjusted y-values based on projection

    # Perform interpolation
    interp_func = interp1d(x, proj_timeblinks, kind='cubic', fill_value="extrapolate")  # 'cubic' for smooth interpolation

    # Interpolated x-values
    framecount = np.arange((total_frame_count))
    gpstime_framecount = interp_func(framecount)
    """
    
    
    ### Return a txt with all frames with gpstime


if __name__=='__main__': 
    # Initialize parser
    parser = argparse.ArgumentParser(description='Produce a list with all frames where the LED is on.')
    parser.add_argument('vidname', type=str, help='Directory of video (mp4 format).')
    parser.add_argument('-ff', '--first_frame', action='store_true', default=False, help="Number associated with the first frame and from where the count is starting. eg: 'frame0', 'frame1250'.")
    parser.add_argument('-gf', '--get_frames', metavar='frame name', type=int, default=[], nargs='*', help="Get specific complete frame(s) from the video.")
    parser.add_argument('-cf', '--cropped_frames', action='store_true', default=False, help="Get specific cropped frame(s) from the video.") # metavar='frame', type=int, default=[], nargs='*',
    # parser.add_argument('-wr', '--write', action='store_true', default=False, help='Enables saving frames when LED is ON.')

    # Get parse data
    args = parser.parse_args()
    
    # Main
    main()
