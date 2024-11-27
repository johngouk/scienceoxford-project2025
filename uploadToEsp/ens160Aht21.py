# This will be a new Class that has an async update action
# built in, and will return the last accessed temp on demand

import asyncio, time, random # Required for testing
from machine import Pin
from machine import I2C
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from sensors.Sensor import Sensor
from ens160 import ENS160
from ahtx0 import AHT20  # Assuming AHT20 is compatible with AHT21 and supported by ahtx0 library

class ENS160AHT21(Sensor):

    def __init__( self, i2c=1, sclPin=25, sdaPin=26,freq=100000, interval = 5, name = "ENS160AHT21"):
        super().__init__(interval=interval, name=name)
        print(type(i2c),type(sclPin),type(sdaPin),type(freq))
        logger.info(const("initialising ENS160AHT21: I2CUnit: %d SCL: %d SDA: %d freq: %d"), i2c, sclPin, sdaPin, freq)
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.scl = Pin(self.sclPin, Pin.PULL_UP)
        self.sda = Pin(self.sdaPin, Pin.PULL_UP)
        try:
            self.i2c = I2C(i2c, scl=sclPin, sda=sdaPin, freq=freq)
        except Exception as e:
            logger.error("Exception %s initialising ENS160AHT21; check pin numbers, connections: I2C Unit: %d Pins - SCL: %d SDA: %d",  
                         e, i2c, self.sclPin, self.sdaPin)
            raise e

        self.temperature_offset = -10.0  # Adjust this value as needed - no idea why we might!

        # Initialize the ENS160 sensor
        self.sensor_ens160 = ENS160(self.i2c)

        # Initialize the AHT21 sensor
        self.sensor_aht21 = AHT20(self.i2c)

        # Need to do this after all init completed!
        self.run()

    # SubClass data collection function implementation
    def _collectData(self, state):
        logger.debug(const("_collectData from ENS160ATH21"))
        # This is a simple sensor - no setup commands
        aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating, temp_raw = self.sensor_ens160.read_air_quality()
        self.values['AQI'] = aqi
        self.values['TVOC'] = tvoc
        self.values['ENS_Temp'] = temp
        self.values['ENS_RH'] = rh
        self.values['ECO2_Rating'] = eco2_rating
        self.values['TVOC_Rating'] = tvoc_rating
        # Read temperature and humidity from AHT21
        temp_aht21 = self.sensor_aht21.temperature  # Apply offset
        rh_aht21 = self.sensor_aht21.relative_humidity
        self.values['AHT_Temp'] = temp_aht21
        self.values['AHT_RH'] = rh_aht21
        logger.debug(const("Values: %s"), self.values)
        return 0, 0 # All done
        
        
# main coroutine to boot async tasks
async def main():
    print("fred: creating...")
    fred = ENS160AHT21(name="1 TestSensor")
    print("fred: running...")
    #fred.run(interval=5)
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