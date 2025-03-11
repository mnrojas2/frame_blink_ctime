#!/usr/bin/env python

import os
import argparse
import droneData
import numpy as np
import cv2
from datetime import datetime
from matplotlib import pyplot as plt


def fixLedType(ledtype):
    # Fix a temporal issue with the green led count in the logfiles
    f_g = np.nonzero(np.where(ledtype > 1, 1, 0) == 1)[0][0]
    ledtype[f_g::5] = 2
    return ledtype


# Main
def main():
    # Get name of the file only
    vidfile = os.path.basename(args.vidname)[:-4]
    
    # Output logged files
    logfiles = {
        "C0008": "log_output_0429_095517.txt",
        "C0009": "log_output_0430_131016.txt",
        "C0010": "log_output_0430_134403.txt",
        "C0011": "log_output_0430_142543.txt",
        "C0012": "log_output_0430_153146.txt"
    }

    # From comparing videos to the plots, we can find out when the first green led blinks seen on video are in the timescale of the logfile.
    # tuple = (number of times the green led blinked before being recorded on video (logfile data), number of times the led blinked before the first green (on video))
    v_blink = {
        "C0008": (1, 2),
        "C0009": (1, 2),
        "C0010": (1, 0),
        "C0011": (1, 1),
        "C0012": (1, 0)
    }

    data, _ = droneData.parse_source_logfile(f"info/{logfiles[vidfile]}", show_labels=False)

    # Get data from logfile
    t = data["DateTimeRPI"]
    altitude = data["Altitude"]
    led_time = data["LastLedCamTime"]
    led_type = data["LedCamType"]

    # Adjust all columns removing the rows where are empty values in LastLedCamTime or LedCamType
    t_ft = t[led_time > 0]
    altitude_ft = altitude[led_time > 0]
    led_time_ft = led_time[led_time > 0]
    led_type_ft = led_type[led_time > 0]

    # Fix green blink in logfile data (temporal)
    led_type_ft = fixLedType(led_type_ft)

    # Plotting
    # First plot
    if args.plot:
        # Create samples for x-axis
        smp = np.arange(altitude_ft.shape[0])

        #   First subplot
        fig, ax1 = plt.subplots()
        ax1.plot(smp, altitude_ft, 'b-')
        ax1.set_xlabel('samples')
        ax1.set_ylabel('altitude', color='b')

        #   Second subplot with its own y-axis
        ax2 = ax1.twinx()
        ax2.plot(smp, led_type_ft, color='g', linestyle='', marker='o')
        ax2.plot(smp, np.where(led_type_ft > 1, 1.05, 1), color='r', linestyle='', marker='o')
        ax2.set_ylabel('led_type', color='g')
        plt.title("Altitude & blink LEDs vs time (from logfile)")
        
        # Show the plots
        plt.show()

    # Get starting point from first blink seen on video
    vid_start = 5 * v_blink[vidfile][0] - v_blink[vidfile][1]

    # Adjust arrays to show only values seen on video
    t_fit = t_ft[vid_start:]
    altitude_fit = altitude_ft[vid_start:]
    led_time_fit = led_time_ft[vid_start:]
    led_type_fit = led_type_ft[vid_start:]

    # Create new samples for plotting
    smp = np.arange(altitude_fit.shape[0])
    # print(smp.shape, altitude_ft.shape, led_time_ft.shape, led_type_ft.shape)

    # Second plot
    if args.plot:
        #   First subplot
        fig, ax1 = plt.subplots()
        ax1.plot(smp, altitude_fit, 'b-')
        ax1.set_xlabel('samples')
        ax1.set_ylabel('altitude', color='b')

        #   Second subplot with its own y-axis
        ax2 = ax1.twinx()
        ax2.plot(smp, led_type_fit, color='g', linestyle='', marker='o')
        ax2.plot(smp, np.where(led_type_fit > 1, 1.05, 1), color='r', linestyle='', marker='o')
        ax2.set_ylabel('led_type', color='g')
        plt.title("Altitude & blink LEDs vs time (adjusted to video)")

        # Show the plots
        plt.show()

    # Get list of frames where the led was blinking
    frame_list = [int(x[5:-4]) for x in os.listdir(f"frames/{vidfile}/")]
    frame_list.sort()

    # Create an array with values covering the complete video
    vidcap = cv2.VideoCapture(args.vidname)
    total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    vidcap.release()

    frames = np.arange(0, total_frame_count, 1)
    # frames = np.char.add('frame', frames.astype(str))
    
    # Create an array with timestamp values for each frame
    timestamps = t_fit[0] + (t_fit[-1] - t_fit[0])/(frame_list[-1] - frame_list[0]) * (frames - frame_list[0])
    dt_stamps = np.array([datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f') for ts in timestamps])
    
    # Save the list of frames and timestamps
    np.savetxt(f"./info/timelist{vidfile}.txt", np.column_stack((frames, dt_stamps)), fmt='%s', delimiter=',', header='frame,UTCtimestamp', comments='')


if __name__=='__main__': 
    # Initialize parser
    parser = argparse.ArgumentParser(description='Filters the timestamp where the leds blinked according to the system.')
    parser.add_argument('vidname', type=str, help='Directory of video (mp4 format).')
    parser.add_argument('-p', '--plot', action='store_true', default=False, help='Show plots from the process.')
    
    # Get all parser arguments
    args = parser.parse_args()

    # Main
    main()
