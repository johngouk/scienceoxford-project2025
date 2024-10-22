import asyncio
from machine import Pin
from button.pushbutton import Pushbutton


"""
    All based on callbacks, set by calling the appropriate API function

    def press_func(func=False, args=())
    def release_func(func=False, args=())
    def double_func(func=False, args=())
    def long_func(func=False, args=())
    
    PROBLEM:
    It appears that pressing a button causes the press function to be called immediately,
    so that a double press generates
        Button pressed
        Button pressed
        Button double pressed
    which isn't what you want really! I'd like to get a single notification for a single or a double press,
    which rather involves a timeout...
    Same is true for the long press - you get a single press, then a long press.
    I don't see how using the Event mechanism would be any better.
    
    Events:
    press
    release
    double
    long

"""

def got_press():
    print("Button pressed")

def got_released():
    print("Button released")

def got_double():
    print("Button double pressed")

def got_long():
    print("Button long pressed")
    
async def wait_press(e):
    while True:
        await e.wait()
        e.clear()
        print("Press Event!")

async def wait_long(e):
    while True:
        await e.wait()
        e.clear()
        print("Long Event!")

async def wait_double(e):
    while True:
        await e.wait()
        e.clear()
        print("Double Event!")

async def main():
    Pushbutton.long_press_ms = 700 # Default 1000
    Pushbutton.double_click_ms = 300 # Default 400

    pb = Pushbutton(Pin(17, Pin.IN, Pin.PULL_DOWN))
    
    #pb.press_func(got_press)
    #pb.double_func(got_double)
    #pb.release_func(got_released)

    #pb.press_func(None) # Event tracking
    pb.double_func(None)
    pb.long_func(None)

    #asyncio.create_task(wait_press(pb.press))
    asyncio.create_task(wait_double(pb.double))
    asyncio.create_task(wait_long(pb.long))

    while True:
        #await pb.press.wait()
        #pb.press.clear()
        await asyncio.sleep(1)

if __name__ == '__main__':
    print("starting button test...")
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
        