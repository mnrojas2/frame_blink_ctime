import numpy as np
import time, os, csv
from matplotlib import pyplot as plt
#from hovercal.library_rep.other import *

# plt.ion()

os.environ['TZ'] = 'UTC'



'''
Website with best description of columns I can find:
https://datfile.net/DatCon/fieldsV3.html

fname: which file without the extension

skip: Some of the files have blank data in the first few lines which crashes the loader, skip resolves this without missing useful data as this is well before launch
'''

time_fields = ['Clock:offsetTime', 'GPS:Time', 'GPS:Date']
gps_fields = [['RTKdata:Lon_P', 'RTKdata:Lat_P', 'RTKdata:Hmsl_P'],
              ['RTKdata:Lon_S', 'RTKdata:Lat_S', 'RTKdata:Hmsl_S'],
              ['GPS:Long', 'GPS:Lat', 'GPS:heightMSL'],
              ['IMU_ATTI(0):Longitude', 'IMU_ATTI(0):Latitude', 'IMU_ATTI(0):alti:D'],
              ['IMU_ATTI(1):Longitude', 'IMU_ATTI(1):Latitude', 'IMU_ATTI(1):alti:D'],
              ['IMU_ATTI(2):Longitude', 'IMU_ATTI(2):Latitude', 'IMU_ATTI(2):alti:D'],
              ['IMUCalcs(0):Long:C', 'IMUCalcs(0):Lat:C', 'IMUCalcs(0):height:C'],
              ['IMUCalcs(1):Long:C', 'IMUCalcs(1):Lat:C', 'IMUCalcs(1):height:C'],
              ['IMUCalcs(2):Long:C', 'IMUCalcs(2):Lat:C', 'IMUCalcs(2):height:C'],
              ]


# Convert from HHMMSS to absolute seconds
def HHMMSS2hms(hms):
    HH = (hms - hms % 10000) / 10000
    mm = hms - HH * 10000
    MM = (mm - mm % 100) / 100
    SS = mm % 100
    return HH, MM, SS

# Convert from HHMMSS to absolute seconds
def GPSDateTime2ctime(ymd, hms, timezone=-4):
    YYYY = (ymd - ymd % 10000) / 10000
    mm = ymd - YYYY * 10000
    MM = (mm - mm % 100) / 100
    DD = mm % 100
    hh, mm, ss = HHMMSS2hms(hms)
    ctime = []
    for i in range(len(YYYY)):
        date = (int(YYYY[i]), int(MM[i]), int(DD[i]),
                int(hh[i]), int(mm[i]), int(ss[i]), 0, 0, 0)
        ctime.append(time.mktime(date) - timezone*3600)
    return np.array(ctime)

def flatten(lists):
    fl = []
    for sublist in lists:
        for item in sublist:
            fl.append(item)
    return fl

class droneData(object):
    def __init__(self, log_file, fields=None, timezone=0, **kwargs):
        if fields == None: fields = gps_fields[0]
        self.load(log_file, fields=fields, timezone=timezone, **kwargs)
        self.test = 1

    def load(self, log_file, skip=100, skip2=0, fields=gps_fields[0], timezone=0, **kwargs):
        if np.ndim(fields) > 1: fields = flatten(fields)
        self.fields = fields
        fields = time_fields + fields

        csvfile = open(log_file, encoding="utf-8")
        reader = csv.DictReader(csvfile)
        data = []

        for i, row in enumerate(reader):
            if i < skip:
                continue
            # Current loading, have to alter this to change which data is loaded form teh giant csv files
            one_row = [row[fld] for fld in fields]
            data.append(one_row)

        # Loads as strings, this converts to floats
        flight_arr = np.array(data)
        flight_arr[flight_arr == ''] = 'NaN'
        flight_arr = flight_arr.astype(float)
        flight_arr = flight_arr[np.isnan(flight_arr).sum(axis=1) == 0]
        flight_arr = flight_arr[(flight_arr == 0).sum(axis=1) == 0]
        flight_arr = flight_arr[skip2:]

        # Add ctime information
        gps_secs = GPSDateTime2ctime(flight_arr[:,2], flight_arr[:, 1], timezone=timezone)

        tags = np.where(np.diff(gps_secs) > 0.5)[0] + 1
        clock = flight_arr[:, 0] # Time from the internal IMU clock

        # Find clock difference between gps tics and clocks
        #error = gps_secs - np.mean(gps_secs[tags]) - (clock - np.mean(clock[tags]))

        # Find the largest gps time tick compared to the internal IMU clock
        #dt0 = error[tags].max()

        # Correct the GPS time adding the fractions of a second from the IMU clock
        #ctime = gps_secs - (error - dt0)
        #ctime = clock + np.max(gps_secs[tags] - clock[tags])
        ctime = clock + np.mean(gps_secs[tags] - clock[tags])

        # Find refresh data frames
        dtags = np.where(np.diff(flight_arr[:, 3]) != 0)[0]+1

        # Store ctime
        self.ct = ctime[dtags]

        # Store data in array
        self.data = flight_arr[dtags, 3:]

        # Store auxiliary time data
        self.timedata = flight_arr[dtags, :3]

    def plot(self, index, ylabel=None, title=None, new=True):
        if new: plt.figure()
        plt.plot(self.ct, self.data[:,index])
        plt.xlabel("ctime [s]")
        plt.ylabel(ylabel)
        plt.title(title)


def YMDHMS2ctime(YMDHMS):
    valid = YMDHMS != "-1"
    ctimes = -np.ones(len(YMDHMS))
    ymds = []
    hmss = []
    fracs = []
    for ymdhms in YMDHMS[valid]:
        YY, MM, DD, HH, mm, SS = ymdhms.split(":")
        if "." not in SS:
            print(ymdhms)
        ss, frac = SS.split(".")
        ymds.append(int(YY+MM+DD))
        hmss.append(int(HH+mm+ss))
        fracs.append(float("0." + frac))
    ctimes[valid] = GPSDateTime2ctime(np.array(ymds), np.array(hmss), timezone=-4)
    ctimes[valid] += np.array(fracs)
    return ctimes


def LED(status):
    led = []
    for st in status:
        if st[0] == "r":
            led.append(1)
        elif st[0] == "g":
            led.append(2)
        else:
            led.append(0)
    return np.array(led)


def INCL(incl_data):
    idata = []
    for incl in incl_data:
        if len(incl) == 28:
            pitch = decode_incl_word(incl[8:14])
            roll = decode_incl_word(incl[14:20])
            yaw = decode_incl_word(incl[20:26])
            idata.append([pitch, roll, yaw])
        else:
            idata.append([-1, -1, -1])
    return np.array(idata)


def decode_incl_word(incl_word):
    #print(incl_word)
    if incl_word[0] == "0": sign = 1
    else: sign = -1
    angle = float(incl_word[1:4]) + float(incl_word[4:6])/100
    return sign * angle

def parse_source_logfile(filename, skip=10, show_labels=True):
    with open(filename, "r") as logfile:
        header = logfile.readline()
        header = header.split("=")[1]
        header = header.split(",")
        config = {}
        for h in header:
            name, value = h.split(":")
            try:
                config[name] = eval(value)
            except:
                config[name] = value
        labels = logfile.readline()
        labels = labels.split(",")
        assert len(labels) >= len(log_file_labels)

    data = {}
    for key in log_file_labels.keys():
        if show_labels:
            print(key)
        par = log_file_labels[key]
        raw_data = np.loadtxt(filename, skiprows=skip+2, delimiter=",", usecols=(par["col"]), dtype=par["dtype"])
        data[key] = par["eval"](raw_data)
    return data, header

def same(data): return data


log_file_labels = {
    "DateTimeRPI": {"dtype": str, "eval": YMDHMS2ctime, "col": 0},
    "DateTimeArduino": {"dtype": str, "eval": YMDHMS2ctime, "col": 1},
    "ArduinoMillis": {"dtype": int, "eval": same, "col": 2},
    "AttOutputStatus": {"dtype": int, "eval": same, "col": 3},
    "PowerDetectorSignal": {"dtype": int, "eval": same, "col": 4},
    "Temperature": {"dtype": float, "eval": same, "col": 5},
    "Pressure": {"dtype": float, "eval": same, "col": 6},
    "Altitude": {"dtype": float, "eval": same, "col": 7},
    "Humidity": {"dtype": float, "eval": same, "col": 8},
    "InclinometerFrame": {"dtype": str, "eval": INCL, "col": 9},
    "LastLedCamTime": {"dtype": str, "eval": YMDHMS2ctime, "col": 10},
    "LedCamType": {"dtype": str, "eval": LED, "col": 11},
    "DroneSignal": {"dtype": int, "eval": same, "col": 12},
    "DT": {"dtype": str, "eval": same, "col": 13}
}