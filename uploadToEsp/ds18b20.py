# This will be a new Class that has an async update action
# built in, and will return the last accessed temp on demand

import asyncio, time, random # Required for testing
import onewire, ds18x20
from machine import Pin
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from sensors.Sensor import Sensor

class DS18B20(Sensor):

    def __init__(self, interval = 5, name = "DS18B20", pin=13):
        super().__init__(interval=interval, name=name)
        self.pin = pin
        self.values = {}
        
    def _init(self, state):
        logger.info(const("initialising sensor(s) on pin %d"), self.pin)
        logger.debug(const("initialising OneWire on Pin %d"), self.pin)
        try:
            ow = onewire.OneWire(Pin(self.pin)) # create a OneWire bus on GPIO12
        except Exception as e:
            logger.error("Error %s initialising DS18B20 OneWire - check pins: %d", e, self.pin)
            raise e
        try:
            logger.debug(const("initialising ds18x20 on Pin %d"), self.pin)
            self.ds = ds18x20.DS18X20(ow)
            logger.debug(const("scanning for ds18x20s..."))
            self.roms = self.ds.scan()
            logger.debug(const("found ds18x20s %s"), str(self.roms))
        except Exception as e:
            logger.error("Error %s initialising DS18B20 instance", e)
            raise e
        return 0, 0 # No pauses required to make this sensor work
    
    # SubClass data collection function implementation
    def _collectData(self, state):
        logger.debug(const("_collectData from DS18B20"))
        pause = 0.100
        if state == 0:
            # first time through
            state = 1
            self.ds.convert_temp()
            return pause, state
        elif state == 1:
            dev = 0
            for rom in self.roms:
                temp = self.ds.read_temp(rom)
                self.values["DS18B20_temp_"+str(dev)] = temp
                dev += 1
            logger.debug(const("Values: %s"), str(self.values))
            return 0, 0 # All done
        
        
# main coroutine to boot async tasks
async def main():
    print("fred: creating...")
    fred = DS18B20()
    print("fred: running...")
    await asyncio.sleep(1)  # Let things settle down before we get values
    
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