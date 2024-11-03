import asyncio
import random
import gc

def mem():
    gc.collect()
    return gc.mem_free()

#from machine import Pin
start = mem()
#from button.FSMButton import FSMButton
from button.FSMState import FSMButton
after_import = mem()

class Pin():
    IN = 0
    PULL_DOWN = 1
    pinValue = False
    def __init__(self, gpio, dir, pull):
        print("Pin: making pin")
        self.gpio = gpio
        asyncio.create_task(self.run())
        
    def __call__(self):
        # This needs to be an array of appropriate test values!
        #print("Pin.__call__: %s"%self.pinValue)
        return self.pinValue
    
    async def run(self):
        """ Modifies the pin value through time according to schedule
            Code checks every 50ms
            Press:  False... True for > 50ms, False > 300ms
            Double: False... True for > 50ms, False < 300ms, True for > 50ms, False...
            Long:   False... True for > 700ms, False...
        """
        press = [(False,500),(True, 200), (False, 500)]
        double = [(False,500),(True, 200), (False, 200),(True, 200),(False, 500)]
        long = [(False,500),(True, 1000), (False, 500)]
        while True:
            #print("Running Press:")
            for x in press: 
                #print("Pin.run:press %s %d"%(x[0], x[1]))
                self.pinValue = x[0]
                await asyncio.sleep_ms(x[1])
            #print("Running Double:")
            for x in double: 
                #print("Pin.run:double %s %d"%(x[0], x[1]))
                self.pinValue = x[0]
                await asyncio.sleep_ms(x[1])
            #print("Running Long:")
            for x in long: 
                #print("Pin.run:long %s %d"%(x[0], x[1]))
                self.pinValue = x[0]
                await asyncio.sleep_ms(x[1])
                
    def value(self):
        print("Pin.value: %s"%self.pinValue)
        return self.pinValue
    
    # How to emulate various pin pushes/releases:
    # debounce = 50msec; long = 700msec; double = 300msec
    # Press: OFF for >50msec; 700msec > ON > 50msec; OFF...
    def __getitem__(self):
        # This needs to be an array of appropriate test values!
        print("Pin.__getitem__: %s"%self.pinValue)
        return self.pinValue


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

async def wait_release(e):
    while True:
        await e.wait()
        e.clear()
        print("Release Event!")

async def main():
    #pb = FSMButton(Pin(17))
    #print("making button")
    before_pin = mem()
    pin = Pin(17, Pin.IN, Pin.PULL_DOWN)
    after_pin = mem()
    pb = FSMButton(pin)
    init_used = mem()
    pb.press_func(None) # Event tracking
    pb.double_func(None)
    pb.long_func(None)
    #pb.release_func(None)
    event_used = mem()
    print("start:",start)
    print("import used:", start-after_import)
    print("before pin:", start - before_pin)
    print("after pin:", start - after_pin)
    print("init pb used:", start-init_used)
    print("event pb used:",start-event_used)

    asyncio.create_task(wait_press(pb.press))
    asyncio.create_task(wait_double(pb.double))
    asyncio.create_task(wait_long(pb.long))
    #asyncio.create_task(wait_release(pb.release))
    
    while True:
        loop = mem()
        print("loop used:",start-loop)
        await asyncio.sleep(5)
                
if __name__ == "__main__":
    print("starting button test...")
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
    
    