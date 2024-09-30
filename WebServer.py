import asyncio, time, gc, random
from RequestParser import RequestParser
from ResponseBuilder import ResponseBuilder

"""

    asyncio Server based web server
        Init'd with an array of data source function callbacks, which provide an
        dict of Key/Value pairs, which the server will stick into a "/api" readData
        response, to be used by the JavaScript as required
        Otherwise attempts to serve files from the "/" directory/subdirectories

"""

class WebServer:
    
    def __init__(self, dataSources, print_progress=False):
        self.print_progress = print_progress
        self.dataSources = dataSources
        if print_progress:
            print("DS:",dataSources)

    def run(self):
        server = asyncio.start_server(self.handle_request, "0.0.0.0", 80)        
        asyncio.create_task(server)


    # coroutine to handle HTTP request
    async def handle_request(self, reader, writer):
        peerInfo = ()
        try:
            peerInfo = reader.get_extra_info('peername')

            raw_request = await reader.read(2048)
            
            request = RequestParser(raw_request)
            
            if self.print_progress:
                print(str(time.time()), peerInfo, request.method, request.get_action(), request.full_url) #, request.protocol, request.headers)
            
            response_builder = ResponseBuilder()

            # filter out api request
            if request.url_match("/api"):
                action = request.get_action()
                if action == 'readData':
                    # ajax request for data
                    response_obj = {
                        'status': 0
                        }
                    if self.print_progress:
                        print("RspObjInit:",response_obj)
                    for d in self.dataSources:
                        values = d()
                        if self.print_progress:
                            print("Vals:", values)
                        response_obj.update(values)
                    if self.print_progress:
                        print("RspObj:",response_obj)
                    response_builder.set_body_from_dict(response_obj)
                    if self.print_progress:
                        print("Rsp:",response_builder.body)
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
                            
            except Exception as e:
                print("Exception:", type(e), str(e), str(e.errno))
            finally:
                await writer.drain()
                del response_builder
                await writer.wait_closed()
                
        except Exception as e:
            print('Exception:', type(e), str(e), str(e.errno), peerInfo)

def getValues():
    return {"temp":45.3, "RH":65}

# main coroutine to boot async tasks
async def main():
    print("Running WebServer")
    # start web server task
    ws.run()
    #server = asyncio.start_server(ws.handle_request, "0.0.0.0", 80)        
    #asyncio.create_task(server)
    
    print("Entering main loop")

    # main task control loop pulses board led
    while True:
        flashLed.toggle_red_led()
        
        await asyncio.sleep(1)

"""
from flashLed import flashLed
from WiFiConnection import WiFiConnection


print('WebServer starting...')
if not WiFiConnection.start_station_mode(hostname = "john", print_progress=True):
    raise RuntimeError('network connection failed')

print("Creating WebServer")
ws = WebServer([getValues], print_progress=True)

# start asyncio task and loop
try:
    # start the main async tasks
    asyncio.run(main())
finally:
    # reset and start a new event loop for the task scheduler
    asyncio.new_event_loop()
"""