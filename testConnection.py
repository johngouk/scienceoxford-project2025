import network

from NetworkCredentials import NetworkCredentials

print_progress = True

def startNetwork():
    network.WLAN(network.AP_IF).active(False)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not (wlan.isconnected()):
        print('Connecting to network...')
        wlan.connect("norcot", "nor265cot")
        while not (wlan.isconnected()):
            pass
    ipaddr = wlan.ifconfig()[0]
    print('Connected! IP: ' + ipaddr)   # Need this to connect!!

#startNetwork()
network.WLAN(network.AP_IF).active(False)
# set WiFi to station interface
wlan = network.WLAN(network.STA_IF)
# activate the network interface
wlan.active(True)
# connect to wifi network
if print_progress:
    print("WiFi Credentials:", NetworkCredentials.ssid, NetworkCredentials.password)

if not (wlan.isconnected()):
    status = network.STAT_CONNECTING
    if print_progress:
        print("Connecting to Wi-Fi - please wait testing")
    wlan.connect(NetworkCredentials.ssid, NetworkCredentials.password)
    print('wlan connected:',wlan.isconnected())

    while not (wlan.isconnected()):
        max_wait = 5
        # wait for connection - poll every 0.5 secs
        while max_wait > 0:
            """
                0   STAT_IDLE -- no connection and no activity,
                1   STAT_CONNECTING -- connecting in progress,
                -3  STAT_WRONG_PASSWORD -- failed due to incorrect password,
                -2  STAT_NO_AP_FOUND -- failed because no access point replied,
                -1  STAT_CONNECT_FAIL -- failed due to other problems,
                3   STAT_GOT_IP -- connection successful.
            """
            #print('wlan.status=',str(wlan.status()))
            if wlan.status() < 0 or wlan.status() >= 3:
                # connection attempt finished
                break
            max_wait -= 1
            utime.sleep(0.5)

# check connection
print('wlan.status=',str(wlan.status()))
status = wlan.status()
if wlan.status() != 3:
    # No connection
    if print_progress:
        print("Connection Failed")
else:
    # connection successful
    config = wlan.ifconfig()
    ip = config[0]
    subnet_mask = config[1]
    gateway = config[2]
    dns_server = config[3]
    if print_progress:
        print('ip = ' + str(ip))
    '''