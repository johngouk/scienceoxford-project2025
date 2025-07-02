import asyncio
import os, gc
from machine import Pin, freq
freq(240000000) # Juice things up a bit
from flashLed import flashLed
from lcd.LCD import LCD

print("Debugging: all libraries imported")

async def main():
    # Flash the onboard LED
    led = flashLed(interval = 1)
    
    # Set up RGB LED
    red = Pin(14, Pin.OUT, Pin.PULL_DOWN)
    green = Pin(13, Pin.OUT, Pin.PULL_DOWN)
    blue = Pin(4, Pin.OUT, Pin.PULL_DOWN)
    
    # TO-DO 2: write code to turn on the red, green, or blue LED
    
    
    # Set up LCD display
    lcd = LCD()
    
    # TO-DO 1: edit the starting message
    lcd[0] = ("Welcome to")
    lcd[1] = ("Science Oxford")
    
    await asyncio.sleep(1)
    print("Debugging: everything initialised")

    print("Debugging: main loop starting")

    # Start loop
    while True:
        print("Debugging: main loop running")
        gc.collect()
        
        # TO-DO 3: write code to flash the red, green, or blue LED

        
        await asyncio.sleep(1)

# Run all of the code set up above
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()