import network
import time
from micropython import const
import binascii
import os
if "ESP32" in os.uname().machine:
    ESP32 = True
else:
    ESP32 = False

ipconfig_names = ['dhcp4',
                  'gw4',
                  #'dhcp6',
                  #'autoconf6',
                  #'has_autoconf6',
                  'addr4',
                  #'addr6',
                  ]

wlan_codes = {'IF_STA': 0
     , 'IF_AP': 1
     , 'SEC_OPEN': 0
     , 'SEC_WEP': 1
     , 'SEC_WPA': 2
     , 'SEC_WPA2': 3
     , 'SEC_WPA_WPA2': 4
     , 'SEC_WPA2_ENT': 5
     , 'SEC_WPA3': 6
     , 'SEC_WPA2_WPA3': 7
     , 'SEC_WAPI': 8
     , 'SEC_OWE': 9
     , 'SEC_WPA3_ENT_192': 10
     , 'SEC_WPA3_EXT_PSK': 11
     , 'SEC_WPA3_EXT_PSK_MIXED_MODE': 12
     , 'PM_NONE': 0
     , 'PM_PERFORMANCE': 1
     , 'PM_POWERSAVE': 2}

network_codes = {'AUTH_OPEN': 0
     , 'AUTH_WEP': 1
     , 'AUTH_WPA_PSK': 2
     , 'AUTH_WPA2_PSK': 3
     , 'AUTH_WPA_WPA2_PSK': 4
     , 'AUTH_WPA2_ENTERPRISE': 5
     , 'AUTH_WPA3_PSK': 6
     , 'AUTH_WPA2_WPA3_PSK': 7
     , 'AUTH_WAPI_PSK': 8
     , 'AUTH_OWE': 9
     , 'AUTH_WPA3_ENT_192': 10
     , 'AUTH_WPA3_EXT_PSK': 11
     , 'AUTH_WPA3_EXT_PSK_MIXED_MODE': 12
     , 'AUTH_MAX': 13
     , 'PHY_LAN8710': 0
     , 'PHY_LAN8720': 1
     , 'PHY_IP101': 2
     , 'PHY_RTL8201': 3
     , 'PHY_DP83848': 4
     , 'PHY_KSZ8041': 5
     , 'PHY_KSZ8081': 6
     , 'PHY_KSZ8851SNL': 100
     , 'PHY_DM9051': 101
     , 'PHY_W5500': 102
     , 'ETH_INITIALIZED': 0
     , 'ETH_STARTED': 1
     , 'ETH_STOPPED': 2
     , 'ETH_CONNECTED': 3
     , 'ETH_DISCONNECTED': 4
     , 'ETH_GOT_IP': 5
     , 'STAT_IDLE': 1000
     , 'STAT_CONNECTING': 1001
     , 'STAT_GOT_IP': 1010
     , 'STAT_NO_AP_FOUND': 201
     , 'STAT_NO_AP_FOUND_IN_RSSI_THRESHOLD': 212
     , 'STAT_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD': 211
     , 'STAT_NO_AP_FOUND_W_COMPATIBLE_SECURITY': 210
     , 'STAT_WRONG_PASSWORD': 202
     , 'STAT_BEACON_TIMEOUT': 200
     , 'STAT_ASSOC_FAIL': 203
     , 'STAT_CONNECT_FAIL': 203
     , 'STAT_HANDSHAKE_TIMEOUT': 204}

valid_config_names = ['mac','ssid','channel','hidden','security','key','hostname','reconnects','txpower','pm']

security_types = ['open','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK']

# Taken from ESP32 Micropython network module
statusCodes = {
    network.STAT_IDLE:const("IDLE"),
    network.STAT_CONNECTING:const("CONNECTING"),
    network.STAT_GOT_IP:const("GOT_IP"),
    network.STAT_NO_AP_FOUND:const("NO_AP_FOUND - check SSID or AP Password requirement"),
    network.STAT_WRONG_PASSWORD:const("WRONG_PASSWORD"),
    }
if ESP32:
    statusCodes.update ({network.STAT_ASSOC_FAIL:const("ASSOC_FAIL"),
                        network.STAT_BEACON_TIMEOUT:const("BEACON_TIMEOUT"),
                        network.STAT_HANDSHAKE_TIMEOUT:const("HANDSHAKE_TIMEOUT"),
                        network.STAT_NO_AP_FOUND_IN_RSSI_THRESHOLD:'AP_OUT_OF_RANGE',
                        network.STAT_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD:'AP_OUT_OF_RANGE',
                        network.STAT_NO_AP_FOUND_W_COMPATIBLE_SECURITY:'NO_AP_FOUND_W_COMPATIBLE_SECURITY',
                        15:const("ENCRYPTED_AP_WRONG_PASSWORD")
                        })


#from NetworkCredentials import NetworkCredentials
creds = ['norcot','nor265cot']

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
# Look for APs
local_aps = wlan.scan()
for a in local_aps:
    print(a)
    print('SSID:',a[0],'BSSID:',binascii.hexlify(a[1]),'Chan:',a[2],'RSSI:',a[3],'Sec:',security_types[a[4]],'Hidden:',a[5], sep='\t')
# connect to wifi network
if print_progress:
    #print("WiFi Credentials:", NetworkCredentials.ssid, NetworkCredentials.password)
    print("WiFi Credentials:", creds[0], creds[1])

wlan.config(reconnects=0)

if (wlan.isconnected()):
    print('Already connected')
else:
    status = network.STAT_CONNECTING
    if print_progress:
        print("Connecting to Wi-Fi - please wait testing")
    wlan.connect(creds[0], creds[1])
    print('wlan connected:',wlan.isconnected())

    #while not (wlan.isconnected()):
    wait_limit = 30
    max_wait = wait_limit
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
        print('wlan.status=',str(wlan.status()), 'try:',wait_limit-max_wait+1)
        if wlan.status() != network.STAT_CONNECTING:
            # connection attempt finished
            break
        max_wait -= 1
        time.sleep(0.5)

# check connection
print('wlan.status=',str(wlan.status()))
status = wlan.status()
if not wlan.isconnected():
    # No connection
    if print_progress:
        print("Connection Failed:", statusCodes[status])
else:
    # connection successful
    config = wlan.ifconfig()
    ip = config[0]
    subnet_mask = config[1]
    gateway = config[2]
    dns_server = config[3]
    if print_progress:
        print('ip = ' + str(ip))
    for n in ipconfig_names:
        print(n, '= ', end='')
        r = wlan.ipconfig(n)
        print(r)