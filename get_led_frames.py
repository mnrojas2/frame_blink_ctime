#!/usr/bin/env python

import os
import argparse
import cv2 as cv
import numpy as np
from tqdm import tqdm


def main():
    print(f'Getting frames from {args.vidname}')

    # Get name of the file only
    vidfile = os.path.basename(args.vidname)[:-4]

    # Get list of frames from parser
    list_frames = args.get_frames

    # Open the video
    vidcap = cv.VideoCapture(args.vidname)
    
    # Get total frame count and frames per second
    total_frame_count = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv.CAP_PROP_FPS)

    # Make a list with the timestamp of all frames
    vidtimes = np.arange(total_frame_count)/fps

    # Initialize progress bar
    pbar = tqdm(desc='READING FRAMES', total=total_frame_count, unit=' frames', dynamic_ncols=True)
    frame_no = 0

    # Create output folders if they weren't created yet
    frames_path = os.path.normpath(os.path.dirname(args.vidname))+'/'+vidfile
    if not os.path.exists(frames_path):
        os.mkdir(frames_path)

    av_crop_frame_list = []

    # Download all frames, cropped to the range of the LED
    while(vidcap.isOpened()):
        frame_exists, curr_frame = vidcap.read()
        if frame_exists:
            if args.first_frame:
                cv.imwrite(f"{args.vidname[:-4]}.jpg", curr_frame)
                pbar.close()
                break
            else:
                # Crop the image to the place the LED is.
                crop_frame = curr_frame[1677:,3466:,:] # TOCO TESTS
                
                if list_frames != [] and frame_no in list_frames:
                    # Find frames listed at the start and save them
                    cv.imwrite(f"{frames_path}/gframe{frame_no}.jpg", curr_frame)
                    list_frames.remove(frame_no)
                    if len(list_frames) == 0:
                        pbar.close()
                        break
                
                else:
                    # Save all frames
                    cv.imwrite(f"{frames_path}/frame{frame_no}.jpg", crop_frame)
                    crop_frame = cv.GaussianBlur(crop_frame,(251,251),0)
                    crop_frame_hsv = cv.cvtColor(crop_frame, cv.COLOR_BGR2HSV)
                    
                    if frame_no == 0:
                        new_frame_hsv = 0*crop_frame
                    else:
                        new_frame_hsv = cv.subtract(crop_frame_hsv, last_frame_hsv)
                    
                    av_crop_frame = np.average(new_frame_hsv, axis = (0,1))
                    av_crop_frame_list.append(av_crop_frame)
                    last_frame_hsv = crop_frame_hsv
        else:
            pbar.close()
            break
        frame_no += 1
        pbar.update(1)

    # Release the file
    vidcap.release()


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(description='Extracts frames from a video cropped towards the position of the LED.')
    parser.add_argument('vidname', type=str, help='Directory of video (mp4 format).')
    parser.add_argument('-ff', '--first_frame', action='store_true', default=False, help="Number associated with the first frame and from where the count is starting. eg: 'frame0', 'frame1250'.")
    parser.add_argument('-gf', '--get_frames', metavar='frame', type=int, default=[], nargs='*', help="Get specific complete frame(s) from the video.")
    parser.add_argument('-wr', '--write', action='store_true', default=False, help='Enables saving frames when LED is ON.')

    # Get parser arguments
    args = parser.parse_args()

    # Main
    main()

