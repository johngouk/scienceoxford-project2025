# Code to develop a means of implementing arbitrary delays
# without using time.sleep, but rather asyncio.sleep

import asyncio, time, random
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

def dt(loc, t2, t1):
    print(f'L: {loc} {t2} {t1} {time.ticks_diff(t2,t1)}')

class thing:

    def __init__(self, interval=5):
        logger.info('thing _init_')
        self._ready = False
        logger.info('class: %s', self.__class__)
        asyncio.create_task(self.thingToDo(interval))
        
    def _getUsecStr(self, ns):
        nsStr = str(ns)
        return nsStr[:len(nsStr)-3]
        
    async def thingToDo(self, interval):
        logger.info('thing: thingToDo')
        start = time.time_ns()
        task = asyncio.create_task(self._init(10))
        result = await asyncio.wait_for(task, None)
        logger.info('thingToDo: init returned %s execute %s us', result, self._getUsecStr(time.time_ns() - start))
        self._ready = True
        # Init done - crack on!
        while True:
            start = time.time_ns()
            pause = random.randint(1000,2000)
            await asyncio.sleep_ms(pause)
            exec_ns = time.time_ns() - start
            #print(exec_ns, self._getUsecStr(exec_ns))
            waitTime = (interval*1000) - (exec_ns/1000000)
            logger.info("ThingToDo: action: interval: %d sec: pause: %d waitTime %d msec", interval, pause, waitTime)
            await asyncio.sleep_ms(int(waitTime))
        
    async def _init(self, times): # Gets called repeatedly until it returns 0,0, otherwise returns state, waitTimeMs
        pause = 100 # 
        for state in range(times):
            #logger.info('_init state: %d pause: %d', state, pause)
            await asyncio.sleep_ms(pause)
        return True

class newThing(thing):
    def __init__(self):
        logger.info('newThing _init_')
        super().__init__()
        # print(f'class: {self.__class__}')

# main coroutine to boot async tasks
async def main():
    fred = thing()
    # betty = newThing()
    logger.info("fred: running...")
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