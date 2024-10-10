# class to handle WiFi connection, and update the RTC!
from micropython import const
import time
import network
import ntptime
import logging
import os
if "ESP32" in os.uname().machine:
    ESP32 = True
else:
    ESP32 = False

logger = logging.getLogger(__name__)
from ESP32LogRecord import ESP32LogRecord
logger.record = ESP32LogRecord()

from NetworkCredentials import NetworkCredentials

# Taken from ESP32 Micropython network module
statusCodes = {
    network.STAT_IDLE:const("IDLE"),
    network.STAT_CONNECTING:const("CONNECTING"),
    network.STAT_GOT_IP:const("GOT_IP"),
    network.STAT_IDLE:const("IDLE"),
    network.STAT_NO_AP_FOUND:const("NO_AP_FOUND - check SSID"),
    network.STAT_WRONG_PASSWORD:const("WRONG_PASSWORD"),
    }
if ESP32:
    statusCodes.update ({network.STAT_ASSOC_FAIL:const("ASSOC_FAIL"),
                        network.STAT_BEACON_TIMEOUT:const("BEACON_TIMEOUT"),
                        network.STAT_HANDSHAKE_TIMEOUT:const("HANDSHAKE_TIMEOUT")
                        })
  
class WiFiConnection:
    # class level vars accessible to all code
    #status = network.STAT_IDLE
    statusText = "NO_STATUS_MSG"
    ssid = ""
    st_ip = ""
    ap_ip = ""
    subnet_mask = ""
    gateway = ""
    dns_server = ""
    hostname = "Not set"
    st = None
    ap = None

    def __init__(self):
        pass
    
    def status():
        if self.st != None:
            return self.st.status()
        else:
            return None
    
    def _startInterfaces(self, hostname=""):
        self.setHostname(hostname)
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.st = network.WLAN(network.STA_IF)
        self.st.active(True)
        
    
    @classmethod
    def setHostname (self, hostname=""):
        if hostname != "":
            self.hostname = hostname
            network.hostname(self.hostname)

    @classmethod
    def start_ap_mode(self, hostname=""):
        self._startInterfaces(self, hostname)
        self.ap_ip = self.ap.ifconfig()[0]
        self.ap_ssid = self.ap.config('ssid')
        logger.info(const("WiFi AP: SSID: %s IP: %s"), self.ap_ssid, self.ap_ip)
        return True #, const("AP SSID:")+self.ap.config('ssid')+const( " IP:")+self.ap_ip
        
    @classmethod
    def start_station_mode(self, hostname=""):
        self._startInterfaces(self, hostname)
        # connect to wifi network
        if not (self.st.isconnected()):
            logger.debug(const("WiFi connecting: Credentials: SSID: %s Pwd: %s"), NetworkCredentials.ssid, NetworkCredentials.password)
            self.st.connect(NetworkCredentials.ssid, NetworkCredentials.password)
            max_wait = 10
            # wait for connection - poll every 0.5 secs
            while max_wait > 0:
                if self.st.isconnected():
                    # connection attempt finished
                    break
                max_wait -= 1
                time.sleep(0.5)

        # check connection
        status = self.st.status()
        self.statusText = "NO_STATUS_MSG"
        if status in statusCodes:
            self.statusText = statusCodes[status]
        if not self.st.isconnected():                    
            logger.error(const("WiFi can't connect: Status %d: Reason: %s"), status, self.statusText)
            return False,self.statusText
        else:
            # connection successful
            config = self.st.ifconfig()
            self.st_ip = config[0]
            self.subnet_mask = config[1]
            self.gateway = config[2]
            self.dns_server = config[3]
            self.hostname = network.hostname() # May as well use the actual value!
            self.st_ssid = self.st.config('ssid')
            logger.info(const("WiFi STA connected: SSID: %s Hostname: %s.local IP: %s"), self.st.config('ssid'), self.hostname, self.st_ip)
            logger.debug('Setting time...')
            ntptime.settime()
            t = time.localtime() # 8-tuple of date/time values
            logger.info(const("Time set: {0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}").format(t[0],t[1],t[2],t[3],t[4],t[5], t[6], t[7]))
            return True #, {'msg':self.statusText,'ssid':self.st.config('ssid'),'IP':self.st_ip,'hostname':self.hostname,'status':self.st.status()}
            #const("{'STA':('ssid':'")+self.st.config('ssid')+const("','IP':'")+self.st_ip+const("','hostname':'")+self.hostname+const(".local')}") 

if __name__ == "__main__":
    from ESP32LogRecord import ESP32LogRecord
    logger.record = ESP32LogRecord()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
    print("****** Starting STA mode ******")
    #ok, info = WiFiConnection.start_station_mode() # Use default hostname
    ok = WiFiConnection.start_station_mode() # Use default hostname
    w = WiFiConnection()
    print("Result:", ok, "Info:", w.st_ssid, w.st_ip, w.hostname)
    print("****** Starting STA mode ******")
    #ok, errorMsg = WiFiConnection.start_ap_mode()
    ok = WiFiConnection.start_ap_mode()
    w = WiFiConnection()
    print("Result:", ok, "Info:", w.ap_ssid, w.ap_ip, w.hostname)