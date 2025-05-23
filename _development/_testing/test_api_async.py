# using asyncio for non blocking web server

import time
from micropython import const
import asyncio
import random
import os, gc
from machine import Pin
from RequestParser import RequestParser
from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from flashLed import flashLed

    
print('Program starting...')
print_progress = True
mem = gc.mem_free()
t = time.time()
print("0:Start:GC Free is:", str(mem))

def printMem(loc, action):
    global mem, t
    if loc == "L":
        m = gc.mem_free()
        if m != mem:
            lt = time.time()
            print(str(lt), str(lt-t), loc,":", ":",action,":GC Free was:", str(mem), "is", str(m), "diff", str(m-mem))
            mem = m
            t = lt

# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')

# coroutine to handle HTTP request
# coroutine to handle HTTP request
async def handle_request(reader, writer):
    global mem
    gcColl = False
    peerInfo = ()
    try:
        peerInfo = reader.get_extra_info('peername')
        if gcColl: gc.collect()
        if print_progress:
            printMem("1","Before Read")

        raw_request = await reader.read(2048)
        
        if print_progress:
            printMem("2","After Read")

        request = RequestParser(raw_request)
        
        if print_progress:
            printMem("3","After Parse")

        if print_progress:
            print(str(time.time()), peerInfo, request.method, request.get_action(), request.full_url) #, request.protocol, request.headers)
        
        response_builder = ResponseBuilder()
        if print_progress:
            printMem("4","After RspInit")

        # filter out api request
        if request.url_match("/api"):
            action = request.get_action()
            if action == 'readData':
                # ajax request for data
                response_obj = {
                    'status': 0,
                    #'pot_value': IoHandler.get_pot_reading(),
                    'pot_value': random.randint(40,60),
                    #'temp_value': temp_value,
                    #'temp_value': IoHandler.get_temp_reading(),
                    'temp_value': random.randint(20,40),
                    }
                response_builder.set_body_from_dict(response_obj)
                del response_obj
            elif False:
                pass
            else:
                # unknown action
                response_builder.set_status(404)

            # response_builder.serve_static_file(request.url, "/api_index.html")
        # try to serve static file
        else:
            # ResponseBulider checks it all out...
            response_builder.serve_static_file(request.url, "/api_index.html")

        """
            Need to set up a try/except construct around the response build and send
            back, because we get a MemoryError if there are too many clients
            Maybe shoot request, response, write.drain and do gc.collect()?

        """
        try:
            del request
            # build response message
            response_builder.build_response()
            #if request.url_match("/api"):
            #    print("API:",response_builder.response)
            # Finished with request!
            #gc.collect()
            #if print_progress:
            #    print("GC Free postbuild:", gc.mem_free())
            # send response back to client
            writer.write(response_builder.response)
            await writer.drain()
            if response_builder.isFile: # It was a file...
                writeLen = response_builder.contentLen
                buf = bytearray(2048)
                with response_builder.fd as fd:
                    while writeLen > 0:
                        readLen = fd.readinto(buf)
                        writeLen = writeLen - readLen
                        writer.write(buf[0:readLen])
                        await writer.drain()
                    fd.close()
                        
            #gc.collect()
            # allow other tasks to run while data being sent
        except Exception as e:
            print("Exception:", type(e), str(e), str(e.errno))
        finally:
            await writer.drain()
            del response_builder
            if gcColl: gc.collect()
            await writer.wait_closed()
            
        if gcColl: gc.collect()
        if print_progress:
            printMem("5","After Resp")
            #print()

    except Exception as e:
        print('Exception:', type(e), str(e), str(e.errno), peerInfo)

# main coroutine to boot async tasks
async def main():
    gc.collect()
    # start web server task
    print('Setting up webserver...')
    server = asyncio.start_server(handle_request, "0.0.0.0", 80)
    asyncio.create_task(server)
    #asyncio.create_task(log(10))

    #asyncio.create_task(updateLCD(5))
    #asyncio.create_task(updateTemp(60))
    
    # main task control loop pulses board led
    while True:
        gc.collect()
        printMem("L", "LedLoop")
        flashLed.toggle_red_led()
        await asyncio.sleep(1)

async def log(interval):
    print("log:",time.time())
    await asyncio.sleep(interval)


# start asyncio task and loop
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
