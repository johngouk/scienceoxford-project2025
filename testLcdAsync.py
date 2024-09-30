# test LCD and stuff with asyncio

import time
import os, gc
import asyncio
from WiFiConnection import WiFiConnection
from LCD import LCD
from micropython import const
from machine import Pin, Signal
from flashLed import flashLed
import urequests
import onewire, ds18x20


def init_DS18B20():
    print('Initialising DS18B20')
    ow = onewire.OneWire(Pin(26)) # create a OneWire bus on GPIO12
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    #print (roms)
    return ds, roms

async def updateArray(interval):
    global mem, bigArray, bigThing
    
    while True:
        bigArray.append(bigThing)
        mem = gc.mem_free()
        print("Time:", str(time.time()),"Array:", str(mem), ":Size:",len(bigArray))
        await asyncio.sleep(interval)
    

async def updateLCD(interval):

    global mem
    
    while True:
        print("Time:", str(time.time()),'LCD:', str(mem))
        lcd.move_to(0,0) # use first row
        lcd.putstr(const('            '))
        lcd.move_to(0,0) # use first row
        lcd.putstr(str(mem))
        await asyncio.sleep(interval)

async def showTime(interval):
        
    while True:
        r = urequests.get('https://timeapi.io/api/Time/current/zone?timeZone=Europe/London')
        t = r.json()['time']
        print("Time:", str(time.time()),'Clock:', t)
        lcd.move_to(0,1) # use second row
        lcd.putstr(const('            '))
        lcd.move_to(0,1) # use second row
        lcd.putstr(t)
        await asyncio.sleep(interval) # Sleep for 1 Second

async def updateTemp(interval):
    global rom, ds, values
    convert_time = 100
    converting = False
    while True:
        if not converting:
            converting = True
            ds.convert_temp()
            await asyncio.sleep_ms(convert_time)
        else:
            converting = False
            dev = 0
            for rom in roms:
                temp = ds.read_temp(rom)
                #print (type(temp))
                #print (rom, temp)
                values["temp"+str(dev)] = temp
                #print (values)
                dev += 1
            #lcd.clear()
            # Make a string for LCD
            sa = []
            for k in values.keys():
                sa.append(k+':'+str("{:2.2f}").format(values[k]))
            print ("Time:", time.time(),":Values:",sa)
            await asyncio.sleep_ms((interval*1000)-convert_time)


async def main():
    gc.collect()
    asyncio.create_task(showTime(60))
    asyncio.create_task(updateLCD(5))
    asyncio.create_task(updateArray(1))
    asyncio.create_task(updateTemp(60))
    
    # main task control loop pulses red led
    #counter = 0
    while True:
        #if counter % 1000 == 0:
        #    flashLed.toggle_red_led()
        #counter += 1
        # 0 second pause to allow other tasks to run
        #gc.collect()
        flashLed.toggle_red_led()
        await asyncio.sleep(1)




print('Program starting...')

# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')

lcd = LCD()
mem = gc.mem_free()
ds, roms = init_DS18B20()
values = {}
#lcdText = [bytearray('                '),bytearray('                ')]


bigThing = const('0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
0123456789\
')
bigArray = []

# start asyncio task and loop
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
