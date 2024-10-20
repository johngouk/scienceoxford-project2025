"""
    MicroPython version

    Sensor
    Provides a framework for asyncio enabled classes that interact with external
    sensors by collecting data at a regular interval and making it available to
    other classes.
    
"""
import asyncio, time
from micropython import const

import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

class Sensor:
    """" Sensor: the base class for sensors
            Sensor(name = "name")
                name: some name you might need to identify it
            
            run(interval = 5)
                interval: the interval in seconds between sensor scans
                
            getValues()
                returns a tuple of current values e.g. ("temp":25.6, "RH":55, "CO2":440)
    """
    
    def __init__(self, interval = 5, name="Sensor"):
        logger.debug(const("initialising"))
        self.name = name
        self.values = {}
        self.interval = interval
        # Need to call run() after all init completed!

    def run(self):
        """
        run: A function that just returns having started the object's asyncio task
        
        """
        logger.debug(const("run executing"))
        asyncio.create_task(self.taskToRun(self.interval))
        
    async def taskToRun(self, interval):
        """
        taskToRun
        Calls the actual service routine from a "while True" loop
        with an asyncio.sleep for the interval value
        interval: seconds to sleep
        
        In order to permit the called _collectData to perform multiple steps
        to get a reading, it returns a tuple (pause, state) where
        pause: seconds to wait before invoking _collectData again
        state: the current state of _collectData, so it can know what the next step is when
                invoked again        
        """
        logger.debug(const("taskToRun entered: interval: %d"), interval)
        # Save the interval!
        self.interval = interval
        while True:
            # Restore the interval!
            interval = self.interval
            logger.debug(const("taskToRun executing"))
            # _collectData has to deal with sensors that have initialisation times,
            # so we need to keep calling c_collectData as long as it needs one...
            pause_s = 0
            state = 0
            pause_s, state = self._collectData(state)
            while pause_s > 0:
                interval = interval -  pause_s
                if interval < 0: interval = 0
                # Data Collector needs a startup time... wait for it
                # note that _collectData has to return its state!!
                logger.debug(const("askToRun pausing: Pause:%d"), pause_s)
                await asyncio.sleep(pause_s)
                pause_s, state = self._collectData(state)
            logger.debug(const("taskToRun pausing: Pause:%d"), interval)
            await asyncio.sleep(interval)

    def _collectData(self, state):
        """
            _collectData - collects data from the sensor
            There are lots of sensors that reuqire startup/scan times before they can return
            a value, so we have to build in some logic for that
            state: the current state of _collectData, which is returned along
                    with the next pause interval time to the calling async routine
                    Set it to zero when you're done
        """
        self.values = {"None":None}
        logger.debug(const("_collectData executing: State:%d : values: %s"), state, self.values)
        return 0, 0

    def getValues(self):
        return self.values

class RandomSensor(Sensor):

    def _collectData(self, state):
        import random
        r = random.randint(0,10)
        self.values = {"random":r}
        logger.debug(const("_collectData entered: %s"), self.values)
        return 0, 0

class WaitSensor(Sensor):

    def _collectData(self, state):
        import random, time
        logger.debug(const("_collectData entered: State: %d: Time: %d"),state, time.time())
        pause = 0.005
        if state == 0:
            # first time through
            state = 1
            logger.debug(const("_collectData waiting: State: %d: :Pause: %d"), state, pause)
            return pause, state
        elif state == 1:
            r = random.randint(0,10)
            self.values = {"wait":r}
            logger.debug(const("_collectData collecting: %s"), self.values)
            return 0, 0 # All done
        # Should probably handle the case of state != [0,1]!

class DisplayController(Sensor):
    dataFunctions = []
    def __init__(self, dataFunctions, name = "DataController"):
        super().__init__(name = name)
        self.dataFunctions = dataFunctions
        logger.debug(const("initialising"))
        
    def _collectData(self, state):
        values = {}
        for f in self.dataFunctions:
            values.update(f())
        logger.debug(const("_collectData executing: %s"), values)
        return 0, 0

# main coroutine to boot async tasks
async def theMain():
    print("fred: creating...")
    fred = Sensor("1 BasicSensor")
    print("wilma: creating...")
    wilma = RandomSensor("2 Random")
    print("wait: creating...")
    wait = WaitSensor("4 Wait")
    print("betty: creating...")
    dc = DisplayController(([fred.getValues, wilma.getValues, wait.getValues]), "3 Betty")
    print()
    print("fred: running...")
    fred.run(interval=10)
    print("wilma: running...")
    wilma.run(interval=5)
    print("betty: running...")
    dc.run(interval = 2)
    print("wait:running...")
    wait.run(5)
    
    # main task control loop pulses board led
    while True:
        logger.debug("Main running...") #,time.time())
        await asyncio.sleep(10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
    
    # start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(theMain())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()

