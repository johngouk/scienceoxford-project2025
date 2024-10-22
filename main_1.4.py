"""

    SciOx Project for ESP
    Runs
    - a bunch of sensors, to be decided, but this one is using 2x DS18B20s on a single pin
    - an LCD, which shows
        - line0: IP address
        - line1: sensor outputs, rotating every second
    - a webserver, with all the html/js/css loaded on to the ESP
    
    Version
    1.0 Clean version for SciOxPyConf
    1.1 Moved everything into main
    1.2 Using modified sensor & LCD versions
    1.3 Moved flashLed code to separate coro in flashLed class - NEEDS FIXING
    1.4 Added a Button on Pin, only announces presses for now; 
    

"""
version = 1.3

import time, random, logging
from micropython import const
import asyncio
import random
import os, gc
from machine import Pin

#           ADJUST LOG LEVEL HERE->vvvvvv, values are DEBUG, INFO, WARNING, ERROR, FATAL
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
from button.pushbutton import Pushbutton


async def wait_press(e, lcd):
    while True:
        await e.wait()
        e.clear()
        print("Press Event!")

async def wait_long(e, lcd):
    while True:
        await e.wait()
        e.clear()
        print("Long Event!")

async def wait_double(e, lcd):
    while True:
        await e.wait()
        e.clear()
        print("Double Event!")

"""
************************************************

    main
    - starts all the different coroutines
    - Continuously runs to maintain everything
    - flashes the LED on the board every 1 sec to show it's working

************************************************
"""
async def main():
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
    # Dummy getValues for testing without sensors
    def getValues():
        return {"temp0":random.randint(2500,3000)/100, "temp1":random.randint(2000,3500)/100}


    logger.info("Program starting version %.2f", version)

    # 0 - flash the LED every second
    # FIX THIS!
    #led = flashLed() # which is the default :-)

    # 1 - Initialise and start the LCD; it will continuously update to show
    #     the current values of lcd[0] and lcd[1]
    lcd = LCD() # Use the defaults
    lcd[0] = ("Starting v%.1f..." % version)
    await asyncio.sleep(1)

    pb = Pushbutton(Pin(17, Pin.IN, Pin.PULL_DOWN))
    pb.press_func(None) # Event tracking
    pb.double_func(None)
    pb.long_func(None)

    asyncio.create_task(wait_press(pb.press, lcd))
    asyncio.create_task(wait_double(pb.double, lcd))
    asyncio.create_task(wait_long(pb.long, lcd))


    # 2
    ok = WiFiConnection.start_station_mode()
    mode = "?"
    if ok:
        # Set up as STA
        # Need to tell people SSID and password
        mode = "S"
    else:
        logger.warning("WiFi STA mode failed, cause %s : trying AP mode", WiFiConnection.statusText)
        password = 'password'
        if WiFiConnection.start_ap_mode(ssid="", password=password):
            logger.warning("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ap_ssid, password, WiFiConnection.ap_ip)
            mode = "A"
        else:
            raise RuntimeError('Unable to connect to network or start AP mode')
    lcd[0] = WiFiConnection.getIp()
    lcd[1] = "%s S:%s"%(mode, WiFiConnection.ssid)
    await asyncio.sleep(5) # Let people read the IP/SSID
    lcd[1] = "%s H:%s"%(mode, WiFiConnection.hostname)
    await asyncio.sleep(5) # Let people read the IP/Hostname

    # 3
    ds = DS18B20(interval=10) # Update sensor values every 10 seconds

    # 4
    ws = WebServer([ds.getValues], "/webdocs")
    #ws = WebServer([getValues], "/webdocs")
    
    # start web server task
    ws.run()
    
    # main task control loop pulses board led
    while True:
        gc.collect()
        printMem("L", "LedLoop")
        values = ds.getValues()
        for k in values.keys():
            lcd[1] = "%s:%.1f"%(str(k), values[k])
            await asyncio.sleep(1)
        await asyncio.sleep(1)




try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
