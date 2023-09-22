#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)

T_TOT = 5000
T_ON = 30
T_OFF = T_TOT - T_ON

led_state = True
t = time.time() #definir t en un momento en particular, como lo puede ser el inicio de un tiempo
counter = 0
try:
    while True:
        if time.time() - t >= counter:
            # Reset counter and print
            led_state = not led_state
            t = time.time()
            dato = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S.%f')
            print(f'Changing led_state at {dato} to {led_state}')
            print_bool = False
        
        # "Led on"
        if led_state:
            # Change state of PINOUT to HIGH
            GPIO.output(23, GPIO.HIGH)
            # Start timer to 30ms
            counter = T_ON/1000 # ms to s
            #time.sleep(0.030)
            
        # "Led off"
        elif not led_state:
            # Change state of PINOUT to LOW
            GPIO.output(23, GPIO.LOW)
            # Start timer to 5000-30ms
            counter = T_OFF/1000 # ms to s
            #time.sleep(4.970)
except KeyboardInterrupt:
    print("That's all folks!")
        
#La raspberry pi está conectada al GPS y toma prioridad desde ahí para determinar el tiempo.
#El whileloop requiere que se implemente con el contador de tiempo y no con un time.sleep.
#Se requiere saber el tiempo que toma la cámara en recibir un dato y actuar bajo el mismo.