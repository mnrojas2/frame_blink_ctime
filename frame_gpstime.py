#!/usr/bin/env python

import os
import argparse
import numpy as np
import datetime as dt
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt

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

def filter_dynamic_step(array, tolerance=0.05):
    # Filter elements that are out of periodicity for led blinks (false positives)
    # Calculate consecutive differences
    differences = np.diff(array)

    # Find the most common step size
    unique_diffs, counts = np.unique(np.round(differences, decimals=6), return_counts=True)
    estimated_step = unique_diffs[np.argmax(counts)]

    # List the elements to remove (for the rest of vectors/lists)
    argidx = []
    
    # Filter elements that match the step pattern within a tolerance
    for k in range(np.sum(counts)-np.argmax(counts)):
        
        # Filtered list always include the first value (if it does not work, try again with the following element of the original list)
        filtered = [array[k]] 
        for i in range(k+1, len(array)):
            if abs(array[i] - filtered[-1] - estimated_step) <= tolerance:
                filtered.append(array[i])
            else:
                argidx.append(i)

        # Redo the filtering process if by using the k-element didn't produce a size good enough
        if len(filtered) >= np.argmax(counts):
            break
        else:
            argidx = [kk for kk in range(k+1)]

    return np.array(filtered), argidx



# Main
gpstime_file = './vids/logfile_1215_182923_camera.txt'
videoblinks_file = './vids/C0025_blinks_final.txt'
frames_path = './vids/C0025'

# Get GPStime and led data from logfile
gpstime_data = load_ledlogfile(gpstime_file)

# Open videoblinks_file
filetxt = open(videoblinks_file, 'r')
cols = filetxt.read()
all_lines = cols.split('\n')

vidblinks_data = []

# Read txt data and save in list
for line in all_lines:
    if line != '' and line[0] != '#':
        # Frame number, time duration, led color
        frame_no, vidtime, led_color_detected = line.split(',')
        
        # Convert from time duration format to seconds only
        vid_timedelta = dt.datetime.strptime(vidtime, "%H:%M:%S.%f") - dt.datetime.strptime("0", "%S")
        vidseconds = vid_timedelta.total_seconds()
        
        vidblinks_data.append([int(frame_no), vidseconds, led_color_detected])
        
# Check stability of led blinks and remove those detections that don't happen in sync (false positives)

# Produce a numpy array only containing the time of detected frames
vidblinks_time = np.array([blink_event[1] for blink_event in vidblinks_data])

# Filter led blink false positives
vidblinks_time_filtered, filtered_idx = filter_dynamic_step(vidblinks_time)
vidblinks_data_filtered = [vidblinks_data[i] for i in range(len(vidblinks_data)) if i not in filtered_idx]

# Merge this information with gpstime blink control data
vidblinks_leds = [viditem[2] for viditem in vidblinks_data_filtered]
gpstime_leds = [gpsitem[1] for gpsitem in gpstime_data]

# if both have the same led order and number ==> ok
# if both have the same led order but one of them is smaller ==> cut longer (check if there are missing led blinks)
# if both start with different starting points ==> fix shifting by removing first elements to get the closest match (based on the location of green led in both)
# if it contains undefined, but follows the split ==> change it to corresponding color

if vidblinks_leds == gpstime_leds:
    vidblink_frames = np.array([viditem[0] for viditem in vidblinks_data_filtered])
    gpstime_timestamp = np.array([gpsitem[0] for gpsitem in gpstime_data])

    # Fit a projection to adjust slopes
    coefficients = np.polyfit(gpstime_timestamp, vidblink_frames, deg=1)  # Fit a 1st-degree polynomial (linear)
    proj_timeblinks = np.polyval(coefficients, gpstime_timestamp)  # Adjusted y-values based on projection

    # Perform interpolation
    interp_func = interp1d(proj_timeblinks, gpstime_timestamp, kind='linear', fill_value="extrapolate")  # 'cubic' for smooth interpolation

    # Get the interpolated time for each frame
    total_frame_count = 19000
    framecount = np.arange((total_frame_count))
    gpstime_framecount = interp_func(framecount)
    
    for i in range(vidblink_frames.shape[0]):
        print(vidblink_frames[i], gpstime_timestamp[i])
    
    # Save the information in a new txt file
    frame_time = np.column_stack((framecount, gpstime_framecount))
    np.savetxt(f"{frames_path}_gpstime.txt", frame_time, fmt= '%.6f', delimiter=',', header="frame, timestamp")
    
    

plt.figure()
plt.plot(vidblinks_time, '.', c='g')
plt.plot(vidblinks_time_filtered, '.', c='r')

plt.figure()
plt.plot(gpstime_framecount, '.', c='cyan')
plt.show()