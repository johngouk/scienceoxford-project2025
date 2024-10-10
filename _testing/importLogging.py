# Uses mip to import mP logging module
import network, mip

# Connection
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect("norcot", "nor265cot")
while not (w.isconnected()):
    pass
ipaddr = w.ifconfig()[0]
print('Connected! IP: ' + ipaddr)   # Need this to connect!!

mip.install('logging')
