# This will be a new Class that has an async update action
# built in, and will return the last accessed temp on demand
import onewire, ds18x20, asyncio, time
from machine import Pin

class DS18B20():

    def __init__(self, pin=26, debugOn=False):
        self.debugOn = debugOn
        if self.debugOn:
            print('Initialising DS18B20')
        ow = onewire.OneWire(Pin(26)) # create a OneWire bus on GPIO12
        self.ds = ds18x20.DS18X20(ow)
        self.roms = self.ds.scan()
        self.values = {}
        self.sa = ""
        

    async def monitorTemp(self, interval):
        convert_time = 100
        converting = False
        while True:
            if not converting:
                converting = True
                self.ds.convert_temp()
                await asyncio.sleep_ms(convert_time)
            else:
                converting = False
                dev = 0
                for rom in self.roms:
                    temp = self.ds.read_temp(rom)
                    self.values["temp"+str(dev)] = temp
                    dev += 1
                self.sa = []
                for k in self.values.keys():
                    self.sa.append(k+':'+str("{:2.2f}").format(self.values[k]))
                if self.debugOn:
                    print ("Time:", time.time(),":Values:", self.values)
                await asyncio.sleep_ms((interval*1000)-convert_time)

    def getValues(self):
        return self.values
    
    def getValuesStr(self):
        return self.sa
        