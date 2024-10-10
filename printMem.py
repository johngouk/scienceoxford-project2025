import gc, time, logging
from ESP32LogRecord import ESP32LogRecord
logger = logging.getLogger(__name__)
logger.record = ESP32LogRecord()

mem = gc.mem_free()
t = time.time()

def printMem(loc, action):
    global mem, t
    m = gc.mem_free()
    if m != mem:
        lt = time.time()
        logger.debug("%d %d Heap info: Loc: %s Action: %s GC Free was: %d now %d diff %d)",
                     lt, lt-t, loc, action, mem, m, m-mem)
        mem = m
        t = lt
