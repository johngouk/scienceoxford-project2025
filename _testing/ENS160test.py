import ens160
from machine import Pin
from machine import I2C
scl = Pin(25, Pin.PULL_UP)
sda = Pin(26, Pin.PULL_UP)
i2c = I2C(1, scl=scl, sda=sda, freq=100000)
e = ens160.ENS160(i2c)
e.part_id
e.get_id()
e.get_status()
e.get_aqi()
e.get_tvoc()
e.get_temperature()
e.get_humidity()
e.read_air_quality()
e.ENS160_REG_PART_ID
