# Get the bloody WiFiConnection working!!

from WiFiConnection import WiFiConnection

print('Program starting...')
# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')

