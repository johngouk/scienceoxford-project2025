import time, machine, ntptime
# uses modified logging module!!
import logging
from logging import LogRecord
from micropython import const

"""
class ESP32LogRecord(LogRecord):
    def set(self, name, level, message):
        super().set(name, level, message)
        print("ESP32LogRecord - setting asctime")
        self.msecs = time.ticks_ms()
        #self.ct = time.time_ns()
        t = time.localtime(self.ct)
        self.asctime = const("{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}.{6:03d}{7:03d}").format(t[0],t[1],t[2],t[3],t[4],t[5], t[6], t[7])
        print("ESP32LogRecord - asctime", self.asctime)
"""

"""     From LogRecord   
        self.ct = time.time()
        self.msecs = int((self.ct - int(self.ct)) * 1000)
        self.asctime = None
"""        
import network
# Check out the RTC
print("before WiFi", time.localtime())
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect("norcot", "nor265cot")
while not (w.isconnected()):
    pass
ipaddr = w.ifconfig()[0]
print('Connected! IP: ' + ipaddr)   # Need this to connect!!

ntptime.settime()
print("after NTP", time.localtime())

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    #datefmt=const("{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}"), #.{6:03d}{7:03d}")
    #format='%(asctime)s %(name)s:%(levelname)s:%(message)s')
    format='%(asctime)s.%(msecs) %(levelname)s - %(name)s - %(message)s')
    #format='No asctime: %(levelname)s - %(name)s - %(message)s')

logger = logging.getLogger("MyName")
print("Logger before:", logger)
print("LogRecord:", type(logger.record))
logger.info("before ESP32LogRecord")

logger.record = ESP32LogRecord()
print("Logger after:", logger)
print("LogRecord:",type(logger.record))
logger.info("after ESP32LogRecord")

logger.info("test the new module")

