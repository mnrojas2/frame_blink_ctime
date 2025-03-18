=================
Frame LED - ctime 
=================

Synchronizes a video with CTime, based on the information given by the LED status seen on camera.

Usage:

1) Run ``python frame_blinks.py <directory of the video>`` to scan the complete video and get all the frames where the blink was on (and some outliers).
    
    Note: If led position has changed from the bottom right corner, please update its position in line 95, defining the coordinates of the cropped section containing the LED in the image.
    
    Returns a folder with the found frames, a txt file indicating frame, video time and detected color for each frame, and a Value channel (from HSV) table for all frames, indicating its relation with former and latter frames.
    
    Note 2: The last created file is made to analyze changes to do in line 119, which selects a frame when its standard deviation of the Value channel (HSV), is higher than a threshold (currently 1.1).

2) Run ``python frame_ctime.py <directory of the frames folder> <directory of the RF source LED data>`` to filter the found blink frames and match them with GPStime data from the same flight.
    Returns a txt file indicating video time and gps time for all frames of the video.