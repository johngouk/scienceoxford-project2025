import time
s = 0
ns = 1
ct = (time.time(), time.time_ns())
print(ct, ct[ns]/1000, ct[ns]/1000000, ct[ns]/1000000000)
nanosec = int(ct[ns] - (ct[s]*1000000000))
print("Using time and time_ns: ct:",ct, "ns:", nanosec)

ctns = ct[ns]
ct = int(ctns/1000000000)
ns = int(ctns - (ct*1000000000))
stringCtns = str(ctns)
print(stringCtns, stringCtns[0:9], int(stringCtns[0:9])*1000000000, ctns-int(stringCtns[0:9])*1000000000)
print("Using time_ns only: ctns:",ctns,"ct:",ct, "ns:", ns)

ctnsUp = ctns*1000
ctUp = int(ctnsUp/1000000000)
nsUp = int(ctnsUp - (ctUp*1000000000))
print (ctnsUp, ctUp, nsUp)

