"""

    Controller
    Class to perform the Controller role in a an MVC-like implementation
    
    Handles
    - pushbutton inputs (Press, DoublePress, LongPress)
    - LCD output (values, messages, scrolls etc.)
    - web page initiated actions (config, MOTD and so on)
    - NeoPixel output
    - restarts

"""
# Handy script for checking target implementation
import sys
if sys.implementation.name == "micropython":
    print("micropython")
    from micropython import const
    #     Do something     
elif sys.implementation.name == "cpython":
    print("lappie")
    def const(x):
        return x
        
import os
if "ESP32" in os.uname().machine:
    print("ESP32")
#     Do something     
    if "S3" in os.uname().machine:
        print("S3")
#     Do something     
elif "ESP8266" in os.uname().machine:
    print ("ESP8266")
#     Do something     



import asyncio, time, random, logging
from machine import Pin
from micropython import const

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from button.pushbutton import Pushbutton

class Controller():
    
    actionCmds = ["file", "data", "cmd", "config"]
    
    def __init__(self, pb, lcd, np, wc, sensors, interval=10):
        """ pb - pushbutton object; lcd - LCD object; np - NeoPixel object; wc - WiFiConnection; sensors - list of sensors with getValues() function"""
        self.pb = pb
        self.lcd = lcd
        self.np = np
        self.wc = wc
        self.sensors = sensors
        self.pb.press_func(None) # Event tracking
        self.pb.double_func(None)
        self.pb.long_func(None)
        asyncio.create_task(self.wait_press(self.pb.press, self.lcd))
        asyncio.create_task(self.wait_double(self.pb.double, self.lcd))
        asyncio.create_task(self.wait_long(self.pb.long, self.lcd))
        pass
        asyncio.create_task(self._run(interval))
        
    async def _run(self, interval):
        asyncio.create_task(self._second())        
        while True:
            # need to start whatever tasks we need at various intervals to handle the
            # various things that go on regularly 
            print("DC loop:", time.time())
            await asyncio.sleep(interval)
    
    async def _second(self):
        # Does whatever needs to happen every second?
        while True:
            # Do thing
            print("Do second tasks")
            await asyncio.sleep(1)
        
    
    """
        Following "wait_..." functions temporary placeholders for actual button actions
    """
    async def wait_press(self, e, lcd):
        while True:
            await e.wait()
            e.clear()
            print("Press Event!")

    async def wait_long(self, e, lcd):
        while True:
            await e.wait()
            e.clear()
            print("Long Event!")

    async def wait_double(self, e, lcd):
        while True:
            await e.wait()
            e.clear()
            print("Double Event!")
     
async def main():
    pb = Pushbutton(Pin(17, Pin.IN, Pin.PULL_DOWN))
    dc = Controller(pb, None, None, None, None)
    while True:
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
