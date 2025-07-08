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
from web.actionHandler import actionHandler
from sensors.ens160aht21 import ENS160AHT21
from button.pushbutton import Pushbutton
from networking.WiFiConnection import WiFiConnection

print("Debugging: all libraries imported")

data = True
MOTD.setMessage("Message of the Day!")

async def wait_press(e, lcd):
    '''
    Sets up what happens when you press the button
    Toggles between: showing the Message Of The Day
        this is set on line 35 above
    and: clearing the screen in preperation for showing data
        this is set further down in the main loop
    '''
    global data
    while True:
        await e.wait()
        e.clear()
        print("Debugging: button pressed")
        
        if data == True:
            print("Debugging: scrolling message of the day")
            message = MOTD.getMessage()
            lcd.clear()
            lcd.scroll(0, message)
            data = False
        else:
            lcd[0] = ""
            lcd[1] = ""
            data = True

async def wait_double(e, lcd):
    '''
    Sets up what happens when you double-press the button
    Shows the WiFi SSID and IP address for 5 seconds
    then: clears the screen in preperation for showing data
        this is set further down in the main loop
    '''
    global data
    while True:
        await e.wait()
        e.clear()
        print("Debugging: button double-pressed")
        
        if data == True:
            print("Debugging: showing network IDs")
            lcd.clear()
            lcd[0] = WiFiConnection.ssid
            lcd[1] = WiFiConnection.getIp()
            data = False
        else:
            lcd[0] = ""
            lcd[1] = ""
            data = True

async def wait_long(e, lcd):
    '''
    Sets up what happens when you long-press the button
    Does nothing at the moment
    '''
    while True:
        await e.wait()
        e.clear()
        print("Debugging: button long-pressed")

async def main():
    """
    ************************************************
        Order of commands is important, because you can't call an object
        that hasn't been initialised
        So:
        0 - LEDs
        1 - LCD display
        2 - Pushbutton
        3 - WiFi
        4 - Sensors
        5 - Web server
        6 - The main loop

    ************************************************
    """    
    # 0 - flash the onboard LED every second
    led = flashLed(interval = 1)
    # set up the RGB LED pins
    red = Pin(14, Pin.OUT, Pin.PULL_DOWN)
    green = Pin(13, Pin.OUT, Pin.PULL_DOWN)
    blue = Pin(4, Pin.OUT, Pin.PULL_DOWN)
    
    # 1 - Initialise and start the LCD
    lcd = LCD()
    lcd[0] = "Welcome to"
    lcd[1] = "Science Oxford"
    await asyncio.sleep(5)
    
    # 2 - Set up the button
    pb = Pushbutton(Pin(21, Pin.IN, Pin.PULL_UP))
    pb.press_func(None)
    pb.double_func(None)
    pb.long_func(None)
    asyncio.create_task(wait_press(pb.press, lcd))
    asyncio.create_task(wait_double(pb.double, lcd))
    asyncio.create_task(wait_long(pb.long, lcd))
    await asyncio.sleep(1)

    # 3 - Set up WiFi
    ssid = 'ssid'
    password = 'password'
    if WiFiConnection.start_ap_mode(ssid=ssid, password=password):
        logger.warning("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ssid, password, WiFiConnection.ap_ip)
    else:
        raise RuntimeError('Unable to start AP mode')
    lcd[0] = WiFiConnection.ssid
    lcd[1] = WiFiConnection.getIp()
    await asyncio.sleep(1)
    
    # 4 - set up the sensor
    ens = ENS160AHT21(interval = 30, temp_offset = 0)
    await asyncio.sleep(1)
    
    # 5 - no webserver code for Session 1
    ws = WebServer([ens.getValues], actionHandler, "/webdocs") # default to port 80
    
    print("Debugging: everything initialised")
    
    # 6 - main task control loop
    print("Debugging: main loop starting")
    while True:
        gc.collect()
        # flashes the red LED
        if red.value() == 1:
            red.off()
        else:
            red.on()
        
        # if you are in data displaying mode...
        if data == True:
            # get all sensor data
            values = ens.getValues()
            print("Debugging: all sensor data - ", ens.getValues(), "\n")
            temp = values.get('AHT_Temp')
            humidity = values.get('RH')
            co2 = values.get('CO2')
            voc = values.get('VOC')
            
            # TO-DO: write code to display values on the LCD
            lcd[0] = "Temperature: " + str(round(temp)) + "C"
            lcd[1] = "Humidity:    " + str(round(humidity)) + "%"
        
        await asyncio.sleep(1)


# Run all of the code set up above
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()