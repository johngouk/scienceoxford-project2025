"""

    MicroPython!!
    
    TestSensor - tests the Sensor class
    A new type of sensor, derived from the Sensor base class
    Overrides:
        __init__: performs sensor-specific initialisation
        _collectData: this is the function/method that gets the data from the sensor, at the
                        interval specified on the run(interval) call

"""
import asyncio
import random
from micropython import const

import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from sensors.Sensor import Sensor

class TestSensor(Sensor):
    def __init__(self, name = "TestSensor", writeLog=True):
        super().__init__(name=name, writeLog=writeLog)
        logger.debug(const("Executing sensor specific initialisation"))
        
    # SubClass data collection function implementation
    def _collectData(self):
        self.values = {"random":random.randint(1,10)}
        logger.debug(const("_collectData executing: values: %s"), self.values)
       
# main coroutine to boot async tasks
async def main():
    print("fred: creating...")
    fred = TestSensor("1 TestSensor")
    print("fred: running...")
    fred.run(interval=5)
    
    # main task control loop pulses board led
    while True:
        print("TestSensor values:", fred.getValues())
        await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')

# start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
