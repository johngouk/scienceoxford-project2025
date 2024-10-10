import time
import network
import ntptime
import logging
from micropython import const

logger = logging.getLogger(__name__)

from WiFiConnection import WiFiConnection



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