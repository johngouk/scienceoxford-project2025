# class to handle WiFi conenction
import utime
import network
from NetworkCredentials import NetworkCredentials


class WiFiConnection:
    # class level vars accessible to all code
    status = network.STAT_IDLE
    ip = ""
    subnet_mask = ""
    gateway = ""
    dns_server = ""
    hostname = ""
    wlan = None

    def __init__(self):
        pass

    @classmethod
    def start_station_mode(self, hostname="", print_progress=False):
        # Set optional hostname
        if hostname != "":
            self.hostname = hostname
            network.hostname(self.hostname)
        # set WiFi to station interface
        self.wlan = network.WLAN(network.STA_IF)
        # activate the network interface
        self.wlan.active(True)
        # connect to wifi network
        if print_progress:
            print("WiFi Credentials:", NetworkCredentials.ssid, NetworkCredentials.password)
        if not (self.wlan.isconnected()):
            if print_progress:
                print('Connecting to network...')
            self.status = network.STAT_CONNECTING
            self.wlan.connect(NetworkCredentials.ssid, NetworkCredentials.password)
            max_wait = 10
            # wait for connection - poll every 0.5 secs
            while max_wait > 0:
                if self.wlan.isconnected():
                    # connection attempt finished
                    break
                max_wait -= 1
                utime.sleep(0.5)

        # check connection
        self.status = self.wlan.status()
        if not self.wlan.isconnected():
            # No connection
            if print_progress:
                print("Connection Failed")
            return False
        else:
            # connection successful
            config = self.wlan.ifconfig()
            self.ip = config[0]
            self.subnet_mask = config[1]
            self.gateway = config[2]
            self.dns_server = config[3]
            if print_progress:
                print('Hostname:', network.hostname(), 'ip:', str(self.ip))
            return True

