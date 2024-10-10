"""

    ESP32LogRecord
    Modified logging.LogRecord for MicroPython that does the right thing to calculate the msecs :-)

"""

import time
import logging
from logging import LogRecord

class ESP32LogRecord(LogRecord):
    def set(self, name, level, message):
        super().set(name, level, message)
        ct_ns = time.time_ns()
        stringCtns = str(ct_ns)
        self.ct = int(stringCtns[0:9])
        self.msecs = int(stringCtns[9:15])

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')

    logger = logging.getLogger(__name__)
    print("Logger before:", logger)
    print("LogRecord:", type(logger.record))
    logger.info("before ESP32LogRecord")

    logger.record = ESP32LogRecord()
    print("Logger after:", logger)
    print("LogRecord:",type(logger.record))
    logger.info("after ESP32LogRecord")

    logger.info("test the new module")
    was = time.ticks_ms()
    for i in range(1,21):
        now = time.ticks_ms()
        logger.info("%02d %05d Compare the msec times", i, time.ticks_diff(now, was))
        was = now
        
