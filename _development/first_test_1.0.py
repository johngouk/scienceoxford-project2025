import asyncio
import os, gc
from machine import Pin, freq

freq(240000000) # Juice things up a bit

from flashLed import flashLed
from lcd.LCD import LCD

async def main():
    '''
    Challenge #3 - can you change the speed of the LED's flash?
    Just ask them if they can work it out, don't point them to this section
    '''
    #Flash the onboard LED for debugging
    led = flashLed(interval = 1)
    
    # Set up RGB LED
    red = Pin(14, Pin.OUT, Pin.PULL_DOWN)
    green = Pin(13, Pin.OUT, Pin.PULL_DOWN)
    blue = Pin(4, Pin.OUT, Pin.PULL_DOWN)
    
    '''
    Challenge #2 - add new code to turn on the red, green or blue LED
    Give them the syntax and place to add it
    LED.on()
    LED.off()
    '''
    
    '''
    Challenge #1 - edit the code below to change the display message
    Explain difference between lcd[] and print()
    '''
    # Initialise the display and set message
    lcd = LCD()
    lcd[0] = ("Welcome to")
    lcd[1] = ("Science Oxford")
    
    print("Debugging: everything initialised")
    
    # start loop
    while True:
        '''
        Challenge #4 - make something repeat!
        e.g. if red == 1: red.off() else: red.on()
        e.g. repeat loop counting and editing the LCD?
        think of some basic things to do...
        '''
        gc.collect()
        await asyncio.sleep(1)
    
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
    
'''
After we've played with this code for a while, and discussed what each section does
and discussed importance of libraries...
switch to session1.py to add in the sensors and pushbutton
'''