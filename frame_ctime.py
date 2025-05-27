#!/usr/bin/env python

import os
import argparse
import numpy as np
import datetime as dt
import pytz
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
                time_obj = dt.datetime.strptime(rpi_time, "%Y:%m:%d:%H:%M:%S.%f")
            except ValueError:
                time_obj = dt.datetime.strptime(rpi_time, "%Y:%m:%d:%H:%M:%S")
            
            # # # Define the UTC-3 offset
            # utc_minus_3 = dt.timezone(dt.timedelta(hours=-3))

            # # Assign the timezone to the datetime object
            # time_obj = time_obj.replace(tzinfo=utc_minus_3)

            # # Convert to UTC before extracting epoch time
            # time_obj = time_obj.astimezone(dt.timezone.utc)
            
            # Convert to timezone-aware datetime (e.g., UTC)
            time_obj = pytz.timezone("Etc/GMT+3").localize(time_obj)

            # Convert to epoch time
            time_dt = int(time_obj.timestamp())

            data_rows.append([time_dt, led_color])

    # Convert data list into numpy array
    return data_rows

def load_blinkvideofile(file):
    filetxt = open(file, 'r')
    cols = filetxt.read()
    all_lines = cols.split('\n')

    vb_data = []
    frame_count = -1
    fps = -1

    # Read txt data and save in list
    for line in all_lines:
        if line != '' and line[0] != '#':
            # Frame number, time duration, led color
            frame_no, vidtime, led_color_detected = line.split(',')
            
            # Convert from time duration format to seconds only
            vid_timedelta = dt.datetime.strptime(vidtime, "%H:%M:%S.%f") - dt.datetime.strptime("0", "%S")
            vidseconds = vid_timedelta.total_seconds()
            
            vb_data.append([int(frame_no), vidseconds, led_color_detected])
        elif 'total frame count' in line:
            frame_count = int(line.split('=')[-1])
        elif 'fps' in line:
            fps = float(line.split('=')[-1])
    
    return vb_data, frame_count, fps

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
    for i in range(np.sum(counts) - np.argmax(counts)):
        # Filtered list always include the first value (if it does not work, try again with the following element of the original list)
        filtered = [array[i]]
        
        # Check all elements of the array from the starting point defined earlier
        for j in range(i+1, len(array)):
            # Check twice as there is a chance that the led detector algorithm could have skipped one blink
            for k in range(3):
                if abs(array[j] - filtered[-1] - estimated_step*(k+1)) <= tolerance*(k+1):
                    filtered.append(array[j])
                    break
            else:
                argidx.append(j)

        # Redo the filtering process if by using the k-element didn't produce a size good enough
        if len(filtered) >= np.argmax(counts):
            break
        else:
            argidx = [ii for ii in range(i+1)]

    # Return the removed elements index list and number of steps between every consecutive element
    return argidx, np.diff(filtered)/estimated_step

def fill_and_rename(gps_data, vb_data, vb_step):
    # Localize skipped elements and fill them temporally (based on spacing between steps) to fit missing colors. 
    # Initialize the list contaning temporal elements to compare led color order
    vb_led_fill = []

    # Check the head of the detected list to see if it's starting properly
    if vb_data[0][2] != gps_data[0][1]:
        vb_led_fill.append('f')
    vb_led_fill.append(vb_data[0][2])

    # Continue checking the rest of elements of the list adding elements if they are missing in list2
    for i in range(1, len(vb_data)):
        if vb_step[i-1] > 1:
            for j in range(int(np.round(vb_step[i-1]))-1):
                vb_led_fill.append('f')
        vb_led_fill.append(vb_data[i][2])            

    # Replace undefined detections to either red or green
    for i in range(len(vb_led_fill)):
        if vb_led_fill[i] == 'undefined':
            vb_led_fill[i] = gps_data[i][1]

    # Get the indexes for those elements that were added
    indexes = [i for i in range(len(vb_led_fill)) if vb_led_fill[i] == 'f']
    
    # Return the list without missing colors and the indexes of the filled positions.
    return vb_led_fill, indexes


def get_video_ctime(video_path, blinktime_file):
    # From a video blinks file (in frames_path) and the RF Source gps time data (containing the moments when the led was set to blink)
    # get the time of each frame of the video
    
    # Get GPStime and led data from logfile
    gpstime_data = load_ledlogfile(blinktime_file)

    # Open video blinks file (same name as video plus '_blinks.txt')
    vidblinks_data, total_frame_count, fps = load_blinkvideofile(os.path.basename(video_path)[:-4]+'_blinks.txt')

    # Produce a numpy array only containing the time of detected frames
    vidblinks_time = np.array([blink_event[1] for blink_event in vidblinks_data])

    # Filter led blink false positives (positions that are not equally separated from the rest)
    filtered_idx, vb_steps = filter_dynamic_step(vidblinks_time)
    vidblinks_data_filtered = [vidblinks_data[i] for i in range(len(vidblinks_data)) if i not in filtered_idx]

    vidblinks_led_filled, filled_indexes = fill_and_rename(gpstime_data, vidblinks_data_filtered, vb_steps)

    # Remove skipped elements from videoframes and gpstime data
    gpstime_data_filtered = [gpstime_data[i] for i in range(len(gpstime_data)) if i not in filled_indexes]
    vidblinks_led_filtered = [vidblinks_led_filled[i] for i in range(len(gpstime_data)) if i not in filled_indexes]

    # Repeat replacing undefined detections but this time in the video data array (perhaps pointless)
    for i in range(len(vidblinks_data_filtered)):
        if vidblinks_data_filtered[i][2] == 'undefined':
            vidblinks_data_filtered[i][2] = vidblinks_led_filtered[i]
        
    # Get list of blink frames and gps time to associate both
    vidblink_frames = np.array([viditem[0] for viditem in vidblinks_data_filtered])
    gpstime_timestamp = np.array([gpsitem[0] for gpsitem in gpstime_data_filtered])

    # Fit a projection to adjust slopes
    coefficients = np.polyfit(gpstime_timestamp, vidblink_frames, deg=1)    # Fit a 1st-degree polynomial (linear)
    proj_timeblinks = np.polyval(coefficients, gpstime_timestamp)           # Adjusted y-values based on projection

    # Perform interpolation
    interp_func = interp1d(proj_timeblinks, gpstime_timestamp, kind='linear', fill_value="extrapolate")

    # Get the interpolated time for each frame
    framecount = np.arange((total_frame_count))
    gpstime_framecount = interp_func(framecount)
    vidtimes = [dt.timedelta(seconds=value) for value in np.arange(total_frame_count)/fps]

    # Save the information in a new txt file
    frame_time = np.column_stack((framecount, vidtimes, gpstime_framecount))
    np.savetxt(f"{video_path}_vidctime.txt", frame_time, fmt= '%.6f,%s,%.6f', delimiter=',', header="frame, videotime, ctime")
    print(f"Video-GPStime syncronization results in {video_path}_vidctime.txt!")

    plt.figure()
    plt.plot([item[0] for item in vidblinks_data], vidblinks_time, '.', c='g')
    plt.plot(vidblink_frames, [item[1] for item in vidblinks_data_filtered], '.', c='r')
    
    plt.figure()
    plt.plot(framecount, gpstime_framecount, '.', c='y')
    plt.plot(vidblink_frames, gpstime_timestamp, '.', c='b')
    plt.show()


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(description='Produce a list with all frames where the LED is on.')
    parser.add_argument('frame_path', type=str, help='Directory of video (mp4 format).')
    parser.add_argument('gpstime', type=str, help="Number associated with the first frame and from where the count is starting. eg: 'frame0', 'frame1250'.")

    # Get parse data
    args = parser.parse_args()
    
    get_video_ctime(args.frame_path, args.gpstime)
    