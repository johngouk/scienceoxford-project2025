import gc, time

mem = gc.mem_free()
t = time.time()

def printMem(yes, loc, action):
    global mem, t
    # if loc == "L":
    m = gc.mem_free()
    if m != mem and yes:
        lt = time.time()
        print(str(lt), str(lt-t), loc,":", ":",action,":GC Free was:", str(mem), "is", str(m), "diff", str(m-mem))
        mem = m
        t = lt
