"""

    SciOx Project for ESP
    Runs
    - a bunch of sensors, to be decided, but this one is using 2x DS18B20s on a single pin
    - an LCD, which shows
        - IP address
        - alternately GC mem_free, and sensor output
    - a webserver, with all the html/js/css loaded on to the ESP
    

"""
version = 1.0

import time, random, logging
from micropython import const
import asyncio
import random
import os, gc
from machine import Pin

logging.basicConfig(level=logging.WARNING, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
try:
    from ESPLogRecord import ESPLogRecord
    logger.record = ESPLogRecord()
except ImportError:
    pass

from RequestParser import RequestParser
from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from LCD import LCD
from flashLed import flashLed
from WebServer import WebServer
from ds18b20 import DS18B20
from printMem import printMem


"""
************************************************

    line0, line1
    These two functions are just helpers to provide
    strings that will be displayed in the LCD
    
************************************************
"""
showMem = False
def line1():
    global showMem
    part1 = ""
    if showMem:
        showMem = False
        part1 = str(gc.mem_free())
    else:
        showMem = True        
        values = ds.getValues()
        if values != {}:
            part1 = str("{:2.2f}C").format(values["temp0"]) + ' '+str("{:2.2f}C").format(values["temp1"])
    return part1

def line0():
    return WiFiConnection.st_ip

def getValues():
    return {"temp0":random.randint(2500,3000)/100, "temp1":random.randint(2000,3500)/100}

"""
************************************************

    main
    - starts all the different coroutines
    - Continuously runs to maintain everything
    - flashes the LED on the board every 1 sec to show it's working

************************************************
"""
async def main():
    # Start background tasks
    asyncio.create_task(lcd.updateLCD(2, line0,line1))
    ds.run(10)

    # start web server task
    ws.run()
    
    # main task control loop pulses board led
    while True:
        gc.collect()
        printMem("L", "LedLoop")
        flashLed.toggle_red_led()
        await asyncio.sleep(1)


"""
************************************************

    Programme starts here
    Order of commands is important, because you can't call an object
    that hasn't been initialised
    So:
    1 - LCD to allow it to display something
    2 - WiFi otherwise nothing happens
    3 - Temperature sensors, which are need to provide data for the...
    4 - Web server, which calls the other objects for data
    5 - The main loop

************************************************
"""

logger.info("Program starting version %.2f", version)

# 1
lcd = LCD() # Use the defaults
lcd.putstr("Starting v%.2f ..." % version)

# 2
ok = WiFiConnection.start_station_mode()
if ok:
    # Set up as STA
    pass
else:
    logger.warning("WiFi STA mode failed, cause %s : trying AP mode", WiFiConnection.statusText)
    password = 'password'
    if WiFiConnection.start_ap_mode(ssid="", password=password):
        logger.info("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ap_ssid, password, WiFiConnection.ap_ip)
    else:
        raise RuntimeError('Unable to connect to network or start AP mode')

# 3
ds = DS18B20()

# 4
ws = WebServer([ds.getValues], "/webdocs")
#ws = WebServer([getValues], "/webdocs")

# 5
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
