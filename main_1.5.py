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
    1.4 Added a Button on Pin, only announces presses for now
    1.5 Added web action handler - url /action + field "action"=<action> + params; removed WebServer.run()
    

"""
version = 1.5

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
from url_parse import url_parse

"""
    Following "wait_..." functions temporary placeholders for actual button actions
"""
async def wait_press(e, lcd):
    while True:
        await e.wait()
        e.clear()
        print("Press Event!")
        lcd[0] = "Pressed"

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
    actionHandler() - likely to be moved to a separate Controller object, which will also process
        the button presses in a MVC-type model
"""
# Handler for web "action" page accesses
def actionHandler(action, params):
    actions = {"network":("hostname","ssid","password"), "message":('message')}
    # Check required params
    if action in actions: # Legal action
        for x in actions[action]: # Check for param 
            if x not in params:
                return "" # Leave!
        # Don't really like hardcoded values here...
        if action == "network":
            # Network config
            # hostname, ssid, password
            hostname = url_parse(params['hostname'])
            ssid = url_parse(params['ssid'])
            password = url_parse(params['password'])
            # not sure what to do with the hostname for now! Would have to put in NetCreds...
            if ssid != "" and password != "":
                WiFiConnection.setNetCreds(ssid, password)
                logger.info(const("Network config updated: hostname: %s SSID: %s Pwd: %s"), hostname, ssid, "********")
        elif action == "message":
            # MOTD
            MOTD = url_parse(params['message'])
            logger.info(const("MOTD set: %s "), message )
    
        return("index.html")
    else: # Action not in actions!
        logger.error(const("Action '%s' requested, not implemented"), action)
        
    # Fall through to here
    return "" # Not implemented
        

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
    pb = Pushbutton(Pin(17, Pin.IN, Pin.PULL_DOWN))
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
            logger.warning("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ap_ssid, password, WiFiConnection.ap_ip)
            mode = "A"
        else:
            raise RuntimeError('Unable to connect to network or start AP mode')
    lcd[0] = WiFiConnection.getIp()
    lcd[1] = "%s S:%s"%(mode, WiFiConnection.ssid)
    await asyncio.sleep(5) # Let people read the IP/SSID
    lcd[1] = "%s H:%s"%(mode, WiFiConnection.hostname)
    await asyncio.sleep(5) # Let people read the IP/Hostname

    # 4
    ds = DS18B20(interval=10) # Update sensor values every 10 seconds

    # 5
    ws = WebServer([ds.getValues], actionHandler, "/webdocs") # default to port 80
        
    # 6
    # main task control loop
    # Display memory if in debug
    # Show some values on the LCD for now
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