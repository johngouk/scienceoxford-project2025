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
        self.name = name
        self.values = {}			# This is what is returned by getValues()
        self.interval = interval	# Pause time between data collections
        self._ready = True
        asyncio.create_task(self.taskToRun(self.interval))
        
    async def taskToRun(self, interval):
        """
        taskToRun
        Performs any sensor-specific initialisation, because many need pauses in this process
            which can only be handled from inside an async def function, using asyncio.sleep[_ms]()
        Calls the actual data collection routine from a "while True" loop
            with an asyncio.sleep for the interval value
        interval: seconds to sleep
        
        In order to permit the called _init and _collectData functions to perform multiple steps
            to get a reading, they return a tuple (pause, state) where
        pause: seconds to wait before invoking _init/_collectData again
        state: the current state of _init/_collectData, so they can know what the next step is when
                invoked again        
        """
        logger.debug(const("taskToRun entered: interval: %d"), interval)
        # Save the interval!
        self.interval = interval
        # _init() has to cope with sensors that require substantial wait intervals during
        # initialisation. This loop calls _init() until it returns a 0s payse interval
        # to indicate it has completed.
        pause_s = 0
        state = 0
        pause_s, state = self._init(state)
        logger.debug(const("taskToRun init loop: state: %d pause: %d"), state, pause_s)
        while pause_s > 0:
            await asyncio.sleep(pause_s)
            pause_s, state = self._init(state)
            logger.debug(const("taskToRun init loop: state: %d pause: %d"), state, pause_s)
        self._ready = True
        # Get on with the data collection task...        
        while True:
            # Restore the interval!
            interval = self.interval
            logger.debug(const("taskToRun executing"))
            # _collectData() has to deal with sensors that have initialisation times,
            # so we need to keep calling _collectData() as long as it needs one...
            pause_s = 0
            state = 0
            pause_s, state = self._collectData(state)
            while pause_s > 0:
                interval = interval -  pause_s
                if interval < 0: interval = 0
                # THe sensor needs a startup time... wait for it
                # note that _collectData has to return its state!!
                logger.debug(const("taskToRun pausing: Pause:%d"), pause_s)
                await asyncio.sleep(pause_s)
                pause_s, state = self._collectData(state)
            logger.debug(const("taskToRun pausing: Pause:%d"), interval)
            await asyncio.sleep(interval)

    def _init(self, state):
        '''
            REPLACE WITH YOUR SubClass METHOD!! This is just demo code!!
            
            _init - Initialises the sensor, called repeatedly until it returns 0,0,
                otherwise returns state, waitTimeSec (can be a fraction for ms)
        '''
        logger.debug(const("_init executing: State:%d"), state)
        if state == 0:
            logger.debug(const("_init: first pass: State:%d"), state)
            state = 1
            pause_s = 2
        elif state == 1:
            logger.debug(const("_init: second pass: State:%d"), state)
            state = 2
            pause_s = 5
        else: # Any other value
            logger.debug(const("_init: final pass: State:%d"), state)
            state = 0
            pause_s = 0
        # Just in case...
        return pause_s, state

    def _collectData(self, state):
        """
            REPLACE WITH YOUR SubClass METHOD!!

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
    
    def __init__(self, interval=5, name=""):
        super().__init__(interval=interval, name=name)
        # Do special init tasks for this sensor
        pass

    def _init(self, state):
        logger.debug(const("%s _init entered: State: %d: Time: %d"),self.__class__, state, time.time())
        if state == 0:
            # first time through
            state = 1
            pause = 1
            logger.debug(const("%s _init : State: %d: :Pause: %d"),self.__class__, state, pause)
        elif state == 1:
            state = 0
            pause = 0
            logger.debug(const("%s _init : %s"),self.__class__, self.values)
        return pause, state # All done
        # Should probably handle the case of state != [0,1]!

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

class WaitInitSensor(Sensor):
    
    def __init__(self, interval=5, name=""):
        super().__init__(interval=interval, name=name)
        # Do special init tasks for this sensor
        pass

    def _init(self, state):
        logger.debug(const("%s _init entered: State: %d: Time: %d"),self.__class__, state, time.time())
        if state == 0:
            # first time through
            state = 1
            pause = 1000
            logger.debug(const("%s _init : State: %d: :Pause: %d"),self.__class__, state, pause)
            await asyncio.sleep_ms(pause)
            pause = 0
        elif state == 1:
            state = 0
            pause = 0
            logger.debug(const("%s _init : %s"),self.__class__, self.values)
        return pause, state # All done
        # Should probably handle the case of state != [0,1]!

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
    def __init__(self, dataFunctions, name = "DataController", interval=5):
        super().__init__(name = name, interval=interval)
        self.dataFunctions = dataFunctions
        #logger.debug(const("initialising"))
        
    def _collectData(self, state):
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

