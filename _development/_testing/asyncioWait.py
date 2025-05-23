# Code to develop a means of implementing arbitrary delays
# without using time.sleep, but rather asyncio.sleep

import asyncio, time
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

def dt(loc, t2, t1):
    print(f'L: {loc} {t2} {t1} {time.ticks_diff(t2,t1)}')

class thing:

    def __init__(self, interval=5):
        self._ready = False
        print(f"class:{self.__class__}")
        asyncio.create_task(self.thingToDo(interval))
        
    async def thingToDo(self, interval):
        print("thingToDo")
        pause_s = 0
        state = 0
        pause_s, state = self._init(state)
        print(f"thingToDo: pause:{pause_s} state:{state}")
        while pause_s > 0:
            await asyncio.sleep(pause_s)
            pause_s, state = self._init(state)
            print(f"thingToDo: pause:{pause_s} state:{state}")
        self._ready = True
        # Init done - crack on!
        while True:
            print("ThingToDo: action")
            await asyncio.sleep(interval)
        
    def _init(self, state): # Gets called repeatedly until it returns 0,0, otherwise returns state, waitTimeMs
        if state == 0:
            print("_init: first pass")
            return 2, 1
        elif state == 1:
            print("_init: second pass")
            return 5, 2
        else: # Any other value
            print("_init: Final pass")
            return 0,0

class newThing(thing):
    def __init__(self):
        super().__init__()
        # print(f'class: {self.__class__}')

# main coroutine to boot async tasks
async def main():
    fred = thing()
    betty = newThing()
    print("fred: running...")
    #fred.run()
    await asyncio.sleep(1)  # Let things settle down before we get values
    
    # main task control loop pulses board led
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
    
    # start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()