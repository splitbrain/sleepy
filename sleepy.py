#!/usr/bin/python2
# -*- coding: utf-8 -*-

import Tkconstants as TkC
from Tkinter import Tk, Frame, Label
from PIL import ImageTk as itk
#import sensor
import sim_sensor as sensor
import glob
import json
import os
import sys
import time
import tkFont
import urllib
import urllib2
import thread
import datetime
import math


class Palette:
    def __init__(self):
        pass

    background = "#192D2B"
    primary = "#694330"
    secondary = "#948358"


class Weather(Frame):
    widgets = {}
    blank = None
    images = {}

    def __init__(self, parent, w, h):
        """
        Create the GUI elements that display the weather data
        """
        Frame.__init__(self, parent)
        self.parent = parent
        self.config(
            height=h,
            width=w,
            bg="gray",
        )

        self.load_images()

        # to be able to size labels in pixels, they need an image assigned
        self.blank = itk.PhotoImage(file="pix/Blank.gif")

        font10 = tkFont.Font(family='Droid Sans', size=9)
        font8 = tkFont.Font(family='Droid Sans', size=8)

        for i in range(0, 5):
            self.widgets[i] = {}
            self.widgets[i]['frame'] = Frame(self, width=(w / 5),
                                             height=h, bg=Palette.background)
            self.widgets[i]['frame'].place(x=((w / 5) * i), y=0)

            self.widgets[i]['iconholder'] = Label(self.widgets[i]['frame'],
                                                  image=self.images['none'], 
                                                  bg=Palette.background,
                                                  borderwidth=0)
            self.widgets[i]['iconholder'].place(x=8, y=0)

            self.widgets[i]['line1'] = Label(self.widgets[i]['frame'], 
                                             text="??h ??°", 
                                             bg=Palette.background, 
                                             fg=Palette.secondary,
                                             width=(w / 5), 
                                             compound="center", 
                                             image=self.blank, font=font10)
            self.widgets[i]['line1'].place(x=0, y=48)

            self.widgets[i]['line2'] = Label(self.widgets[i]['frame'], 
                                             text="???", bg=Palette.background, 
                                             fg=Palette.secondary, width=(w / 5),
                                             compound="center", image=self.blank,
                                             font=font8)
            self.widgets[i]['line2'].place(x=0, y=64)

    def load_images(self):
        """
        Preloads the weather images
        """
        for f in glob.glob('pix/weather/*.png'):
            base = os.path.splitext(os.path.basename(f))[0]
            self.images[base] = itk.PhotoImage(file=f)


    def update_data(self, weather_data):
        """
        Update the weather display with the given data
        """
        for i in range(0, 5):
            self.widgets[i]['line1'].config(
                text="%d° %sh" % (
                    weather_data['list'][i]['main']['temp'] - 273.15,
                    datetime.datetime.fromtimestamp(
                        weather_data['list'][i]['dt']).strftime('%H').lstrip('0')
                )
            )
            self.widgets[i]['line2'].config(
                text=weather_data['list'][i]['weather'][0]['main']
            )

            self.widgets[i]['iconholder'].config(
                image=self.images[weather_data['list'][i]['weather'][0]['icon']]
            )


class Sleepy(Frame):
    clock = None
    calendar = None
    weather = None
    temperature = None
    sleep_phase = None

    def __init__(self, parent):
        Frame.__init__(self, parent, background=Palette.background)
        self.parent = parent
        self.pack(fill=TkC.BOTH, expand=1)

        # init the clock
        clock_font = tkFont.Font(family='Droid Sans', size=52, weight='bold')
        self.clock = Label(self, text="??:??", fg=Palette.primary, 
                           bg=Palette.background, font=clock_font)
        self.clock.place(x=0, y=0)

        # init the calendar
        calendar_font = tkFont.Font(family='Droid Sans', size=12)
        self.calendar = Label(self, text="?? ?????, ???", 
                              fg=Palette.secondary, bg=Palette.background, 
                              font=calendar_font)
        self.calendar.place(x=4, y=70)

        #init the sleep phase indicator
        sleep_phase_font = tkFont.Font(family='Droid Sans', size=14)
        self.sleep_phase = Label(self, text="Heavy sleep", 
                              fg=Palette.primary, bg=Palette.background,
                              font=sleep_phase_font)
        self.sleep_phase.place(x=4, y=90)

        # init the weather
        self.weather = Weather(self, 320, 82)
        self.weather.place(x=0, y=(240 - 82))

        # init the temperature
        temperature_font = tkFont.Font(family='Droid Sans', size=12)
        self.temperature = Label(self, text="?? °C", fg=Palette.secondary, 
                                 bg=Palette.background, font=temperature_font)
        self.temperature.place(x=240, y=50)

        # print tkFont.families()
        ''' ('Century Schoolbook L', 'Droid Sans Mono', 'Droid Sans Ethiopic', 
        'Droid Sans Thai', 'DejaVu Sans Mono', 'URW Palladio L', 
        'Droid Arabic Naskh', 'URW Gothic L', 'Dingbats', 'URW Chancery L', 
        'FreeSerif', 'DejaVu Sans', 'Droid Sans Japanese', 'Droid Sans Georgian',
        'Nimbus Sans L', 'Droid Serif', 'Droid Sans Hebrew', 
        'Droid Sans Fallback', 'Standard Symbols L', 'Nimbus Mono L', 
        'Nimbus Roman No9 L', 'FreeSans', 'DejaVu Serif', 'Droid Sans Armenian',
        'FreeMono', 'URW Bookman L', 'Droid Sans') '''

        # start working
        self.update_clock()
        self.update_temperature()
        self.fetch_weather_thread()
        self.monitor_sleep_phase_thread()

    def update_clock(self):
        """
        Updates the clock every ten seconds (less precision = less stuff to do)
        """
        now = time.strftime("%H:%M")
        self.clock.configure(text=now)
        cal = time.strftime("%A, %B %d")
        self.calendar.configure(text=cal)

        self.parent.after(10000, self.update_clock)

    def update_sleep_phase(self,sleep_phase):
        """
        Change the current sleep phase indication
        """
        self.sleep_phase.configure(text=sleep_phase)

    def update_temperature(self):
        """
        Update the temperature every minute
        """
        t = sensor.DS18B20()
        temp = "%0.2f °C" % (t.read_temp())
        self.temperature.configure(text=temp)
        self.parent.after(60*1000, self.update_temperature)

    def fetch_weather_thread(self):
        """
        start a thread to fetch new weather data
        """
        thread.start_new_thread(self.fetch_weather, ())

    def fetch_weather(self):
        """
        fetch new weather data
        """
        apikey = "f4b0ead5b6a13da37d586a327730ae0b"  # FIXME move to config
        location = "Berlin,de"

        values = {
            'q': location,
            'APPID': apikey,
            'mode': json
        }

        try:
            response = urllib2.urlopen(
                'http://api.openweathermap.org/data/2.5/forecast?' + 
                urllib.urlencode(values))
            data = response.read()
            weather_data = json.loads(data)
            self.weather.update_data(weather_data)

            # call again in 1 hour
            self.parent.after(1000 * 60 * 60, self.fetch_weather_thread)
        except urllib2.URLError as e:
            print e.reason
            # call again in 1 minute
            self.parent.after(1000 * 60 * 1, self.fetch_weather_thread)

    def monitor_sleep_phase_thread(self):
        """
        start a thread to monitor the sleep phase
        """
        thread.start_new_thread(self.monitor_sleep_phase, ())


    def monitor_sleep_phase(self):
        """
        monitor the sleep status of the sleeper
        """
 
       #speedup_factor speeds up the process for testing
        #it should be set to 1 for normal operation
        speedup_factor=100
 
        #constants
        #FIXME: add to configuration file
        accelerometer_calibrated_one=1.02
        accelerometer_time_resolution=1.0/speedup_factor
        awake_threshold=0.2
        light_sleep_threshold=0.05
        awake_time_constant=600/speedup_factor
        light_sleep_time_constant=600/speedup_factor
 
        #assume at beginning that sleeper is fast asleep and has been forever
        sleep_phase='heavy sleep'
        last_awake_spike_time=float("-inf")
        last_light_sleep_spike_time=float("-inf")
       
        accelerometer=sensor.ADXL345()
        while True:
            prev_status=sleep_phase
            now=time.time()
            (x,y,z)=accelerometer.getAxes(True)
            resultant=math.sqrt(x**2+y**2+z**2)
            spike=math.fabs(resultant-accelerometer_calibrated_one)
            #print(spike)
            if spike>awake_threshold:
                last_awake_spike_time=now
            elif spike>light_sleep_threshold:
                last_light_sleep_spike_time=now
 
            if now - last_awake_spike_time < awake_time_constant:
                sleep_phase='awake'
            elif now - last_light_sleep_spike_time < light_sleep_time_constant:
                sleep_phase='light sleep'
            else:
                sleep_phase='heavy sleep'
 
            if sleep_phase != prev_status:
                self.update_sleep_phase(sleep_phase)
 
            time.sleep(accelerometer_time_resolution)

def main():
    root = Tk()
    root.geometry("320x240")
    root.wm_title('sleepy')
    if len(sys.argv) > 1 and sys.argv[1] == 'fs':
        root.wm_attributes('-fullscreen', True)
    app = Sleepy(root)
    root.mainloop()


if __name__ == '__main__':
    main()
