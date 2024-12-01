from machine import Pin
from machine import I2C

sdaPin = 26
sclPin = 25
freq = 100000
i2c = I2C(1, scl=sclPin, sda=sdaPin, freq=freq)
i2c.scan()

from ahtx0 import AHT20
a = AHT20(i2c)
t = a.temperature
print(t)