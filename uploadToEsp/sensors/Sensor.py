"""
    MicroPython version

    Sensor
    Provides a framework for asyncio enabled classes that interact with external
    sensors by collecting data at a regular interval and making it available to
    other classes.
    
    When subclassing this Class to create your own sensor, there are N things to code/configure:
    1 - You need to provide your own __init__() function if you have additional config parameters
        e.g. Pins, I2C instance; this should include the "interval" and optional "name"
    2 - Call super().__init__(interval=interval, name=name) in your __init__() function to make sure
        the superclass is initialised correctly
    3 - Provide your own _init() function which actually initialises the attached sensor. See the
        comments on the _init() function for instructions - basically, it implements a state machine,
        and is called repeatedly by the main task, passing back the new state and any pause interval.
        This last allows timed waits for the sensor to perform its initialisation, rather than dodgy
        time.sleep() which halts everything!!
    4 - Provide your own _collectData() function to collect data from the sensor and store it in
        self.values, as per the example. Like _init(), it is a state machine and permits sensor trigger
        and any required wait for the correct sensor state before collecting data
    
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
        logger.debug(const("%s __init__"), self.__class__)
        '''
        try:
            super().__init__(interval=interval, name=name)
            #logger.debug(const("This is the subclass!!"))
        except:
            #logger.debug(const("This is the super class!!"))
            pass
        '''
        # Set up all your values before kicking things off...
        self.name = name
        self.values = {}			# This is what is returned by getValues()
        self.interval = interval	# Pause time between data collections
        asyncio.create_task(self.taskToRun())
        logger.debug(const("taskToRun taskToRun task created"))

    def _getUsecStr(self, ns):
        nsStr = str(ns)
        return nsStr[:len(nsStr)-3]
        
    async def taskToRun(self):
        """
            taskToRun
                Uses two async tasks
                _init() - takes what it takes to complete
                _collectData() - likewise
        """
        logger.debug(const("taskToRun entered: interval: %d"), self.interval)
        # Perform initialisation through _init task
        start = time.time_ns()
        task = asyncio.create_task(self._init())
        logger.debug(const("taskToRun _init task created"))
        result = await asyncio.wait_for(task, None)
        logger.debug('taskToRun: _init execute %s us', self._getUsecStr(time.time_ns() - start))
        if not result: # for the demo always True
            logger.error('taskToRun: init error: %s', result)
            return # give up
        self._ready = True
        # Get on with the data collection task...        
        while True:
            start = time.time_ns()
            logger.debug(const("taskToRun executing"))
            task = asyncio.create_task(self._collectData())
            result = await asyncio.wait_for(task, None)
            # Should do something with the result...
            end = time.time_ns()
            exec_ns = end - start
            exec_ms = int(self._getUsecStr(exec_ns))/1000
            logger.debug('taskToRun: _collectData execute %s us %d ms', self._getUsecStr(exec_ns), exec_ms)
            # Restore the interval!
            exec_ns = time.time_ns() - start
            waitTime = (self.interval*1000) - (exec_ns/1000000)        
            await asyncio.sleep_ms(int(waitTime))

    async def _init(self):
        '''
            REPLACE WITH YOUR SubClass METHOD!! This is just demo code!!
            
            _init - runs as a separate asyncio task, performs all init wait actions with asyncio.sleep[_ms]()
            
        '''
        demoInitPause = 100 # You need to get rid of these!
        demoInitTimes = 10
        logger.debug(const("_init executing: State:%d"), state)
        demoInitPause = 100
        for state in range(demoInitTimes):
            logger.debug('_init state: %d pause: %d', state, demoInitPause)
            await asyncio.sleep_ms(demoInitPause)
        return True

    async def _collectData(self):
        """
            REPLACE WITH YOUR SubClass METHOD!!

            _collectData - collects data from the sensor
                            Runs as a Task until complete from _taskToRun
        """
        self.values = {"None":None}
        logger.debug(const("_collectData executing: State:%d : values: %s"), self.values)
        await asyncio.sleep(0) # Cos we are doing nuffink
        return True

    def getValues(self):
        return self.values

class RandomSensor(Sensor):

    async def _collectData(self):
        import random
        r = random.randint(0,10)
        self.values = {"random":r}
        logger.debug(const("_collectData entered: %s"), self.values)
        return True

class WaitSensor(Sensor):

    async def _collectData(self):
        import random, time
        waitTime = random.randint(100,500)
        logger.debug(const("_collectData entered: waitTime: %d msec"),waitTime)
        await asyncio.sleep_ms(waitTime) # Cos we are doing nuffink
        return True

class WaitInitSensor(Sensor):
    
    async def _init(self):
        pause = 100 #
        times = 10
        for state in range(times):
            logger.debug('_init')
            await asyncio.sleep_ms(pause)
        return True

    async def _collectData(self):
        import random, time
        waitTime = random.randint(100,500)
        logger.debug(const("_collectData entered: waitTime: %d msec"),waitTime)
        await asyncio.sleep_ms(waitTime) # Cos we are doing nuffink
        return True

class DisplayController(Sensor):
    dataFunctions = []
    def __init__(self, dataFunctions, name = "DataController", interval=5):
        super().__init__(name = name, interval=interval)
        self.dataFunctions = dataFunctions
        #logger.debug(const("initialising"))
        
    def _collectData(self):
        values = {}
        for f in self.dataFunctions:
            values.update(f())
        logger.debug(const("_collectData executing: %s"), values)
        return 0, 0

# main coroutine to boot async tasks
async def theMain():
    #print("fred: creating...")
    #fred = Sensor(name="1 BasicSensor",interval=10)
    #print("wilma: creating...")
    #wilma = RandomSensor(name="2 Random",interval=5)
    logger.debug("creating Wait...")
    wait = WaitInitSensor(name="4 Wait",interval=5)
    #print("betty: creating...")
    #dc = DisplayController(([fred.getValues, wilma.getValues, wait.getValues]), name="3 Betty",interval = 2)
    print()
    
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

