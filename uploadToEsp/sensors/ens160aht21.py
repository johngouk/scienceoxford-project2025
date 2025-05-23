import asyncio, time, random # Required for testing
from machine import Pin
from machine import I2C
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from sensors.Sensor import Sensor
from sensors.ens160 import ENS160
from sensors.ahtx0 import AHT20  # Assuming AHT20 is compatible with AHT21 and supported by ahtx0 library

class ENS160AHT21(Sensor):

    def __init__( self, i2c=1, sclPin=25, sdaPin=26,freq=100000, interval = 30, name = "ENS160AHT21"):
        #print(type(i2c),type(sclPin),type(sdaPin),type(freq))
        logger.info(const("initialising ENS160AHT21: I2CUnit: %d SCL: %d SDA: %d freq: %d"), i2c, sclPin, sdaPin, freq)
        self.temperature_offset = -10.0  # Adjust this value as needed - no idea why we might!
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
        # Need to do this after all init completed!
        super().__init__(interval=interval, name=name)

    async def _init(self):
        # Initialize the ENS160 sensor
        logger.info(const("initialising ENS160"))
        self.sensor_ens160 = ENS160(self.i2c)

        # Initialize the AHT21 sensor
        logger.info(const("initialising AHT20"))
        self.sensor_aht21 = AHT20(self.i2c)
        return True

    # SubClass data collection function implementation
    async def _collectData(self):
        logger.debug(const("_collectData from ENS160ATH21"))
        temp_aht21 = self.sensor_aht21.temperature
        rh_aht21 = self.sensor_aht21.relative_humidity
        self.values['Temp'] = round(temp_aht21, 1)
        self.values['RH'] = round(rh_aht21, 1)
        self.sensor_ens160.set_envdata(temp_aht21,rh_aht21)
        validity, aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating = self.sensor_ens160.read_air_quality()
        self.values['Validity'] = validity
        self.values['AQI'] = aqi
        self.values['VOC'] = tvoc
        self.values['ENS_Temp'] = temp
        self.values['ENS_RH'] = rh
        self.values['CO2'] = eco2
        self.values['CO2_Rating'] = eco2_rating
        self.values['VOC_Rating'] = tvoc_rating
        # Read temperature and humidity from AHT21
        logger.debug(const("Values: %s"), self.values)
        return True # All done
        
        
# main coroutine to boot async tasks
async def main():
    print("fred: creating...")
    fred = ENS160AHT21(name="ENS160AHT21", interval=10)
    print("fred: running...")
    #fred.run(interval=5)
    await asyncio.sleep(10)  # Let things settle down before we get values
    
    # main task control loop pulses board led
    while True:
        print("ENS160AHT21 Values:", fred.getValues())
        await asyncio.sleep(30)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
    
    # start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
