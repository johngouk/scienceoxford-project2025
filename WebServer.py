import asyncio, time, random, logging
from micropython import const

logger = logging.getLogger(__name__)
from ESP32LogRecord import ESP32LogRecord
logger.record = ESP32LogRecord()


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
    
    def __init__(self, dataSources, docroot="/html"):
        logger.info(const("initialising: Data Sources: %s"), dataSources)
        self.dataSources = dataSources
        self.docroot = docroot

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
            
            logger.debug(const("Request Info: t: %d client: %s method: %s action: %s URL: %s"),
                         time.time(), peerInfo, request.method, request.get_action(),
                         request.full_url)
            
            response_builder = ResponseBuilder(self.docroot)

            # filter out api request
            if request.url_match("/api"):
                action = request.get_action()
                if action == 'readData':
                    # ajax request for data
                    response_obj = {
                        'status': 0
                        }
                    for d in self.dataSources:
                        values = d()
                        response_obj.update(values)
                    response_builder.set_body_from_dict(response_obj)
                    logger.debug(const("Response Body: %s"), response_builder.body)
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
            try/except/finally to handle running out of Heap Memory error,
            largely alleviated now by the loop with a fixed length buffer read
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
                logger.error(const("Exception building/writing response: %s err: %s"), str(e), str(e.errno))
            finally:
                await writer.drain()
                del response_builder
                await writer.wait_closed()
                
        except Exception as e:
            logger.error(const("Exception processing request: Client: %s Ex: %s err: %s"), peerInfo, str(e), str(e.errno))

def getValues():
    return {"temp0":random.uniform(40,65), "temp1":random.uniform(40,65)}


# Code to test as free-standing program
async def main():
    from flashLed import flashLed
    from WiFiConnection import WiFiConnection
    logger.debug(const('WiFiConnection starting...'))
    if not WiFiConnection.start_station_mode(hostname = "john"):
        raise RuntimeError('network connection failed')

    logger.debug(const("Starting WebServer"))
    ws = WebServer([getValues])
    # start web server task
    ws.run()
    
    logger.debug(const("Entering main loop"))

    # main task control loop pulses board led
    while True:
        flashLed.toggle_red_led()
        
        await asyncio.sleep(1)

if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)06d %(levelname)s - %(name)s - %(message)s')
    # start asyncio task and loop
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
