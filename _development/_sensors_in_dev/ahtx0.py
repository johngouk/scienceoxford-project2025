# The MIT License (MIT)
#
# Copyright (c) 2020 Kattni Rembor for Adafruit Industries
# Copyright (c) 2020 Andreas Bühl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""

MicroPython driver for the AHT10 and AHT20 Humidity and Temperature Sensor

Author(s): Andreas Bühl, Kattni Rembor

Modified: John Gouk
    Now includes asyncio-based waits to be compatible with an asyncio-based framework

"""

import time
import asyncio
from micropython import const
import logging

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

from sensors.Sensor import Sensor

class AHT10(Sensor):
    """Interface library for AHT10/AHT20 temperature+humidity sensors"""

    AHTX0_I2CADDR_DEFAULT = const(0x38)  # Default I2C address
    AHTX0_CMD_INITIALIZE = 0xE1  # Initialization command
    AHTX0_CMD_TRIGGER = const(0xAC)  # Trigger reading command
    AHTX0_CMD_SOFTRESET = const(0xBA)  # Soft reset command
    AHTX0_STATUS_BUSY = const(0x80)  # Status bit for busy
    AHTX0_STATUS_CALIBRATED = const(0x08)  # Status bit for calibrated

    def __init__(self, i2c, address=AHTX0_I2CADDR_DEFAULT, interval = 30, name = "AHT21"):
        logger.info(const("_init_: address 0x%02x"), address)
        self._i2c = i2c
        self._address = address
        self._buf = bytearray(6)
        self._temp = None
        self._humidity = None
        super().__init__(interval=interval, name=name)

    async def _init(self):
        '''
            AHT20/21 specific _init function
            This is essentially the code from https://github.com/JustDr00py/ens160-aht21/blob/main/lib/ahtx0.py
            rewritten to use asyncio tasks
        
        '''
        await asyncio.sleep_ms(20) # Initial pause to give it time to start
        
        logger.debug(const("_init calling _reset()"))
        task = asyncio.create_task(self._reset())
        asyncio.wait_for(task, None)
        
        logger.debug(const("_init calling _initialize()"))
        task = asyncio.create_task(self._initialize())
        result = asyncio.wait_for(task, None)

    async def _collectData(self):
        """
            _collectData - collects data from the sensor
                            Runs as a Task until complete from _taskToRun
        """
        logger.debug(const("_collectData executing: values: %s"), self.values)
        self.values = {}
        self._trigger_measurement()
        while self.status & self.AHTX0_STATUS_BUSY:
            await asyncio.sleep_ms(5)
        self._read_to_buffer()
        
        self._humidity = ((self._buf[1] << 12) | (self._buf[2] << 4) | (self._buf[3] >> 4))
        self._humidity = (self._humidity * 100) / 0x100000

        self._temp = ((self._buf[3] & 0xF) << 16) | (self._buf[4] << 8) | self._buf[5]
        self._temp = ((self._temp * 200.0) / 0x100000) - 50
        
        self.values = {"temp":self._temp, "rh":self._humidity}        
        logger.info(const("_collectData values: %s"), self.values)

        return True

    async def _reset(self):
        """
            Perform a soft-reset of the AH
            Returns 20ms delay value
        T"""
        self._buf[0] = self.AHTX0_CMD_SOFTRESET
        self._i2c.writeto(self._address, self._buf[0:1])
        await asyncio.sleep_ms(20)  # 20ms delay to wake up

    async def _initialize(self):
        """Ask the sensor to self-initialize. Returns True on success, False otherwise"""
        self._buf[0] = self.AHTX0_CMD_INITIALIZE
        self._buf[1] = 0x08
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])
        while self.status & self.AHTX0_STATUS_BUSY:
            await asyncio.sleep_ms(5)
        return (self.status & self.AHTX0_STATUS_CALIBRATED)

    @property
    def status(self):
        """The status byte initially returned from the sensor, see datasheet for details"""
        self._read_to_buffer()
        return self._buf[0]

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        return self._humidity

    @property
    def temperature(self):
        """The measured temperature in degrees Celsius."""
        return self._temp

    def _read_to_buffer(self):
        """Read sensor data to buffer"""
        self._i2c.readfrom_into(self._address, self._buf)

    def _trigger_measurement(self):
        """Internal function for triggering the AHT to read temp/humidity"""
        self._buf[0] = self.AHTX0_CMD_TRIGGER
        self._buf[1] = 0x33
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])

class AHT20(AHT10):
    AHTX0_CMD_INITIALIZE = 0xBE  # Calibration command
    
# main coroutine to boot async tasks
async def main():
    from machine import I2C, Pin
    logger.info(const("initialising I2C"))
    sclPin = 25
    sdaPin = 26
    freq = 100000
    i2cPort = 1
    try:
        i2c = I2C(i2cPort, scl=sclPin, sda=sdaPin, freq=freq)
    except Exception as e:
        logger.error("Exception %s initialising ENS160AHT21; check pin numbers, connections: I2C Unit: %d Pins - SCL: %d SDA: %d",  
                     e, i2c, sclPin, sdaPin)
    # Initialize the AHT21 sensor
    logger.info(const("initialising AHT20"))
    fred = AHT20(i2c)
    await asyncio.sleep(1)  # Let things settle down before we get values
    
    # main task control loop pulses board led
    while True:
        print("TestSensor values:", fred.getValues())
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
