import os
import numpy
import argparse
import droneData
import numpy as np
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Filters the timestamp where the leds blinked according to the system.')
parser.add_argument('vidname', type=str, help='Name of video (mp4 format).')

# Main
args = parser.parse_args()

# Output logged files
logfiles = {
    "C0008": "log_output_0429_095517.txt",
    "C0009": "log_output_0430_131016.txt",
    "C0010": "log_output_0430_134403.txt",
    "C0011": "log_output_0430_142543.txt",
    "C0012": "log_output_0430_153146.txt"
}

data, header = droneData.parse_source_logfile(f"info/{logfiles[args.vidname]}", show_labels=False)

def fixLedType(ledtype):
    # Fix a temporal issue with the green led count in the logfiles
    f_g = np.nonzero(np.where(ledtype > 1, 1, 0) == 1)[0][0]
    ledtype[f_g::5] = 2
    return ledtype

t = data["DateTimeRPI"]

altitude = data["Altitude"]
led_time = data["LastLedCamTime"]
led_type = data["LedCamType"]

altitude_ft = altitude[led_time > 0]
led_time_ft = led_time[led_time > 0]
led_type_ft = led_type[led_type > 0]
led_type_ft = fixLedType(led_type_ft)

# Create samples
smp = np.arange(altitude_ft.shape[0])
# print(smp.shape, altitude_ft.shape, led_time_ft.shape, led_type_ft.shape)

fig, ax1 = plt.subplots()
ax1.plot(smp, altitude_ft, 'b-')
ax1.set_xlabel('samples')
ax1.set_ylabel('altitude', color='b')

# Create a second subplot with its own y-axis
ax2 = ax1.twinx()
ax2.plot(smp, led_type_ft, color='g', linestyle='', marker='o')
ax2.plot(smp, np.where(led_type_ft > 1, 1.05, 1), color='r', linestyle='', marker='o')
ax2.set_ylabel('led_type', color='g')

# Show the plot
plt.show()