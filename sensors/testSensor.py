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
from sensors.Sensor import Sensor

from micropython import const

class TestSensor(Sensor):
    def __init__(self, name = "TestSensor", writeLog=True):
        super().__init__(name=name, writeLog=writeLog)
        self.logMsg(const("{0} {1} __init__ executing sensor specific initialisation: "), self.name, type(self))
        
    # SubClass data collection function implementation
    def _collectData(self):
        self.values = {"random":random.randint(1,10)}
        self.logMsg(const("{0} {1} _collectData executing: values: {2}"), self.name, type(self), self.values)
       
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
    
    # start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
