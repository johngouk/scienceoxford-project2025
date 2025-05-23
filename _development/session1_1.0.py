import time, random, logging
from micropython import const
import asyncio
import random
import os, gc
from machine import Pin
import machine

machine.freq(240000000) # Juice things up a bit

'''
QUESTION FOR JOHN
Is this needed for the starter code, or it is debugging for when you were experimenting?
Suggestion to remove for Session 1, and add back in when adding in all the webserver stuff later on
'''

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
from sensors.ens160aht21 import ENS160AHT21
from button.pushbutton import Pushbutton

'''
Maybe skip this part, I was experimenting with adding if statements as that will be familiar to them
'''
data = False
MOTD = "Welcome to Science Oxford!"
startTop = "Hello"
startBottom = "World!"

async def wait_press(e, lcd):
    global data
    while True:
        await e.wait()
        e.clear()
        print("Debugging: button pressed")
        
        if data == True:
            print("Debugging: displaying message of the day")
            lcd.scroll(0, MOTD)
            lcd[1] = ""
            data = False
        
        else:
            print("Debugging: displaying data")
            data = True

'''
Below is the main loop that makes everything work
'''
print("Debugging: entering main loop")

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
    # fake temperature values for testing
    def getValues():
        return {"temp0":random.randint(2500,3000)/100, "temp1":random.randint(2000,3500)/100}
    
    # 0 - flash the onboard LED every second - useful for debugging
    led = flashLed()
    # set up the RGB LED pins
    red = Pin(14, Pin.OUT, Pin.PULL_DOWN)
    green = Pin(13, Pin.OUT, Pin.PULL_DOWN)
    blue = Pin(4, Pin.OUT, Pin.PULL_DOWN)
    
    # 1 - Initialise and start the LCD
    lcd = LCD()
    lcd[0] = (startTop)
    lcd[1] = (startBottom)
    await asyncio.sleep(1)
    
    # 2 - Set up the button
    pb = Pushbutton(Pin(21, Pin.IN, Pin.PULL_UP))
    pb.press_func(None)
    asyncio.create_task(wait_press(pb.press, lcd))

    # 3 - no wifi code for Session 1
    
    # 4 - set up the sensor
    ens = ENS160AHT21(interval = 30)
    
    # 5 - no webserver for Session 1
    
    print("Debugging: everything initialised")
    
    # 6 - main task control loop
    while True:
        gc.collect()
        #printMem("L", "LedLoop")
        values = getValues()
        if red.value() == 1:
            red.off()
        else:
            red.on()
            
        '''
        Sarah to-do - replace with real sensor data
        '''
        if data == True:
            lcd[0] = ""
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