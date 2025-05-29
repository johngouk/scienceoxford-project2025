"""

    SciOx Project for ESP
    Runs
    - a bunch of sensors, to be decided, but this one is using 2x DS18B20s on a single pin
    - an ENS160 & AHT21 combo, providing CO2/VOC data and Temp/RH respectively
    - an LCD, which shows
        - line0: IP address
        - line1: sensor outputs, rotating every second
    - a webserver, with all the html/js/css loaded on to the ESP
    
    Version
    1.0 Clean version for SciOxPyConf
    1.1 Moved everything into main
    1.2 Using modified sensor & LCD versions
    1.3 Moved flashLed code to separate coro in flashLed class
    1.4 Added a Button on Pin, only announces presses for now
    1.5 Added web action handler - url /action + field "action"=<action> + params; removed WebServer.run()
    1.6 Added ENS160AHT21 sensor - very cool
    2.0 Pins edited for new PCB
    2.1 Moved actionHandler to separate file for safety
    

"""
version = 2.2

import time, random, logging
from micropython import const
import asyncio
import random
import os, gc
from machine import Pin
import machine

machine.freq(240000000) # Juice things up a bit

#           ADJUST LOG LEVEL HERE->vvvvvv, values are DEBUG, INFO, WARNING, ERROR, FATAL
logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
try:
    from ESPLogRecord import ESPLogRecord
    logger.record = ESPLogRecord()
except ImportError:
    print('Unable to import ESPLogRecord!!')
    pass

from flashLed import flashLed
from printMem import printMem

from lcd.LCD import LCD

from web.WebServer import WebServer
from web.url_parse import url_parse
from web.MOTD import MOTD

#from sensors.ds18b20 import DS18B20
from sensors.ens160aht21 import ENS160AHT21

from button.pushbutton import Pushbutton

# Note that you can't use the module name "network" for your own stuff - Python has already used it! 
from networking.WiFiConnection import WiFiConnection
from web.actionHandler import actionHandler

"""
    Following "wait_..." functions temporary placeholders for actual button actions
"""
async def wait_press(e, lcd):
    """ wait_press: puts up the wifi mode, ssid and hostname for 10 secs """
    state = 0
    while True:
        await e.wait()
        e.clear()
        #print("Press Event!")
        state = (state + 1) % 3
        if state == 0:
            print('button state 0')
            lcd[0] = WiFiConnection.getIp()
        elif state == 1:
            print('button state 1')
            wifiInfo = f"Mode:{WiFiConnection.getMode()} SSID:{WiFiConnection.ssid} Hostname:{WiFiConnection.hostname}"
            lcd.scroll(0,wifiInfo)
        elif state == 2:
            print('button state 2')
            message = MOTD.getMessage()
            logger.debug("wait_press: MOTD:%s", message)
            lcd.scroll(0,message)

async def wait_long(e, lcd):
    while True:
        await e.wait()
        e.clear()
        #print("Long Event!")
        lcd[0] = "Long Event"
        await asyncio.sleep(5)
        lcd[0] = WiFiConnection.getIp()

async def wait_double(e, lcd):
    while True:
        await e.wait()
        e.clear()
        #print("Double Event!")
        lcd[0] = "Double Event"
        await asyncio.sleep(5)
        lcd[0] = WiFiConnection.getIp()
        
MOTD.setMessage("Hi, I'm your friendly environmental sensor!")

"""
************************************************

    main
    - starts all the different coroutines
    - Continuously runs to maintain everything - when this exists, everything else does

************************************************
"""
async def main():
    """
    ************************************************

        Programme starts here
        Order of commands is important, because you can't call an object
        that hasn't been initialised
        So:
        0 - Flash the LED
        1 - LCD to allow it to display something
        2 - Pushbutton enable
        3 - WiFi otherwise nothing happens
        4 - Temperature sensors, which are need to provide data for the...
        5 - Web server, which calls the other objects for data
        6 - The main loop

    ************************************************
    """
    # Dummy getValues for testing without sensors
    def getValues():
        return {"temp0":random.randint(2500,3000)/100, "temp1":random.randint(2000,3500)/100}


    logger.info("Program starting version %.2f", version)

    # 0 - flash the LED every second
    led = flashLed() # which is the default :-)

    # 1 - Initialise and start the LCD; it will continuously update to show
    #     the current values of lcd[0] and lcd[1]
    lcd = LCD() # Use the defaults
    lcd[0] = ("Starting v%.1f..." % version)
    await asyncio.sleep(1)

    # 2
    pb = Pushbutton(Pin(21, Pin.IN, Pin.PULL_UP))
    pb.press_func(None) # Event tracking
    pb.double_func(None)
    pb.long_func(None)

    asyncio.create_task(wait_press(pb.press, lcd))
    asyncio.create_task(wait_double(pb.double, lcd))
    asyncio.create_task(wait_long(pb.long, lcd))

    # 3
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
            logger.warning("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ssid, password, WiFiConnection.ap_ip)
            mode = "A"
        else:
            raise RuntimeError('Unable to connect to network or start AP mode')
    lcd[0] = WiFiConnection.getIp()
    lcd[1] = "%s S:%s"%(mode, WiFiConnection.ssid)
    await asyncio.sleep(5) # Let people read the IP/SSID
    lcd[1] = "%s H:%s"%(mode, WiFiConnection.hostname)
    await asyncio.sleep(5) # Let people read the IP/Hostname

    # 4
    #ds = DS18B20(interval=10, pin=33) # Update sensor values every 10 seconds
    ens = ENS160AHT21(interval = 30, temp_offset = -5)

    # 5
    #ws = WebServer([ds.getValues,ens.getValues], actionHandler, "/webdocs") # default to port 80
    #ws = WebServer([ds.getValues], actionHandler, "/webdocs") # default to port 80
    ws = WebServer([ens.getValues,], actionHandler, "/webdocs") # default to port 80
        
    # 6
    # main task control loop
    # Display memory if in debug
    # Show some values on the LCD for now
    while True:
        gc.collect()
        printMem("L", "LedLoop")
        values = getValues()
        #values = {1:1, 2:2, 3:3, 4:4}
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
