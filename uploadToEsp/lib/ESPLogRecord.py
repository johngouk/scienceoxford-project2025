"""

    ESPLogRecord
    Modified logging.LogRecord for MicroPython that does the right thing to calculate the msecs :-)

"""

import time
import logging
from logging import LogRecord

class ESPLogRecord(LogRecord):
    def set(self, name, level, message):
        super().set(name, level, message)
        # Modified to account for not having a network connection!
        self.ct = time.time()
        ct_ns = time.time_ns()
        strNs = str(ct_ns)
        # time_ns is  ssssmmmuuu000 with microSec resolution in fact
        #             0123456789ABCD
        #                 ^^^         want these 3 for ms
        #print(strNs)
        msOffset = len(strNs)-9
        self.msecs = int(strNs[msOffset:msOffset+3])
        #print(strNs, self.msecs)
        
if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')

    logger = logging.getLogger(__name__)
    print("Logger before:", logger)
    print("LogRecord:", type(logger.record))
    logger.info("before ESPLogRecord")

    logger.record = ESPLogRecord()
    print("Logger after:", logger)
    print("LogRecord:",type(logger.record))
    logger.info("after ESPLogRecord")

    logger.info("test the new module")
    was = time.ticks_ms()
    for i in range(1,21):
        now = time.ticks_ms()
        logger.info("%02d %05d Compare the msec times", i, time.ticks_diff(now, was))
        was = now
        
