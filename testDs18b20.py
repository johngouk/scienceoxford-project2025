import asyncio, gc
from ds18b20 import DS18B20
from flashLed import flashLed

print("Starting...")

# main coroutine to boot async tasks
async def main():

    ds = DS18B20()

    asyncio.create_task(ds.monitorTemp(30))
    
    # main task control loop pulses board led
    while True:
        flashLed.toggle_red_led()
        await asyncio.sleep(1)


try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
