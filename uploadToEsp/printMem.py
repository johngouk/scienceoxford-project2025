import gc, time, logging
from ESPLogRecord import ESPLogRecord
logger = logging.getLogger(__name__)
logger.record = ESPLogRecord()

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
