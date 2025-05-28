#!/usr/bin/env python

import os
import argparse
import numpy as np
import astropy.units as u
from astropy.io import ascii


# Main
def merge_pwr2altaz():
    # Normalize paths to prevent issues with generating strings
    altaz_path = os.path.normpath(args.dir_altaz) # './altaz_files/'

    # Load file with table match for Flight and logfile
    fdir = open(args.filetable, 'r') # './altaz_files/FLY-log-table.txt'
    cols = fdir.read()
    all_lines = cols.split('\n')
    
    filename = ''
    f_altaz = altaz_path + filename
        
    # Load altaz file
    data_altaz = ascii.read(f'{altaz_path}/{f_altaz}', fast_reader=False)

    # Get time row from altaz
    t_altaz = data_altaz['ctime'].data
    
    # Add calculated power column to the altaz data
    data_altaz['power'] = adc_dB_interpol * u.dB # FBI, OPEN UP!

    # Save the new altaz file
    print(f"Saving data in '{altaz_path}/{os.path.splitext(os.path.basename(f_altaz))[0]}_pwr2{os.path.splitext(f_altaz)[1]}'")
    data_altaz.write(f'{altaz_path}/{os.path.splitext(os.path.basename(f_altaz))[0]}_pwr2{os.path.splitext(f_altaz)[1]}', overwrite=True)
            

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(description='Reads ADC data from logfile, converts it to output power (dBm) and adds it to a new column in the corresponding Altaz file.')
    parser.add_argument('dir_altaz', type=str, help='Directory of the folder containing the Altaz files.')
    parser.add_argument('dir_fctime', type=str, help='Directory of the folder containing the frame ctime log files.')
    
    # Load argparse arguments
    args = parser.parse_args()
    
    # Run main
    merge_pwr2altaz()