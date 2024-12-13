# Uses mip to install MPy logging module
import network, mip
    
from NetworkCredentials import NetworkCredentials

# Connection
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect(NetworkCredentials.getNetCreds()[0], NetworkCredentials.getNetCreds()[1])
while not (w.isconnected()):
    pass
ipaddr = w.ifconfig()[0]
print('Connected! IP: ' + ipaddr)   # Need this to connect!!
#print('Installing logging')
#mip.install('logging')
#print('Installing time add-ins')
#mip.install('time')
# Only required for Weather RSS feed
#mip.install('xmltok')
mip.install('unittest')