version = 1.1 # Now handles "action" URL using a provided actionHandler callback

import asyncio, time, random, logging
from micropython import const

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()


from web.RequestParser import RequestParser
from web.ResponseBuilder import ResponseBuilder
from web.url_parse import url_parse


class WebServer:

    def __init__(self, dataSources, actionHandler, docroot="/html", port=80):
        logger.info(const("initialising v%.2f: Data Sources: %s"), version, dataSources)
        if actionHandler == None:
            self.actionHandler = self._actionHandler
        else:
            self.actionHandler = actionHandler
        self.dataSources = dataSources
        self.docroot = docroot
        server = asyncio.start_server(self.handle_request, "0.0.0.0", port)        
        asyncio.create_task(server)
                
    @classmethod    
    def _actionHandler (self, action, params):
        logger.debug(const("actionHandler: action: %s params %s"), action, params)
        actions = {"network":("hostname","ssid","password"), "message":("MOTD",)}
        # Check required params
        if action in actions: # Legal action
            for x in actions[action]: # Check for param 
                if x not in params:
                    logger.debug(const("actionHandler: action %s - param %s not provided"),action, x)
                    return "" # Leave!
            # Don't really like hardcoded values here...
            if action == "network":
                # Network config
                # hostname, ssid, password
                hostname = url_parse(params['hostname'])
                ssid = url_parse(params['ssid'])
                password = url_parse(params['password'])
                # not sure what to do with the hostname for now! Would have to put in NetCreds...
                if ssid != "" and password != "":
                    logger.info(const("Network config updated: hostname: %s SSID: %s Pwd: %s"), hostname, ssid, "********")
            elif action == "message":
                # MOTD
                MOTD = url_parse(params['MOTD'])
                logger.info(const("MOTD updated: %s"), MOTD)
            return("thanks.html")
        else:
            logger.error(const("Action '%s' requested, not implemented"), action)
        
        # Fall through to here
        return "" # Not implemented

    # coroutine to handle HTTP request
    # Presumably instantiated for every individual client, so that we have to keep buffers etc.
    # unique and within the scope of this function
    async def handle_request(self, reader, writer):
        logger.debug(const("entering handle_request rd %s wr %s"), reader, writer)
        peerInfo = ()
        try:
            peerInfo = reader.get_extra_info('peername')
            # Horrible reading of large string object, but it works...
            raw_request = await reader.read(2048)
            request = RequestParser(raw_request)
            
            logger.info(const("Request Info: t: %d client: %s method: %s action: %s URL: %s"),
                         time.time(), peerInfo, request.method, request.get_action(),
                         request.full_url)
            
            response_builder = ResponseBuilder(self.docroot)

            # filter out api request
            if request.url_match("/data"):
                # JS Fetch request for data
                response_obj = [{'status': 0}]
                for d in self.dataSources:
                    values = d()
                    for k, v in values.items():
                        response_obj.append({k:v})
                response_builder.set_body_from_dict(response_obj)
                logger.debug(const("Response Body: %s"), response_builder.body)
                del response_obj
            elif request.url_match("/action"):
                # Time to do something...
                if "action" in request.post_data:
                    action = request.post_data["action"]
                    returnPage = self.actionHandler(action, request.post_data)
                    if returnPage == "": # Whoops, unknown action!
                        logger.error("Action '%s' not implemented or unknown! Fix HTML Form %s", action, request.url)
                        response_builder.status = 422
                    else:
                        response_builder.serve_static_file(returnPage, returnPage)
                else:
                    # Whoops - no action param in returned form values - fix HTML!
                    logger.error("No Action input element in Form - Fix HTML Form %s", request.url)
                    response_builder.status = 422
            else:
                # try to serve static file
                # ResponseBuilder checks it all out...
                response_builder.serve_static_file(request.url, "/index.html")
            
            if response_builder.status != 200:
                logger.warning(const("Error %d on Request %s"), response_builder.status, raw_request)

            """
            try/except/finally to handle running out of Heap Memory error,
            largely alleviated now by the loop with a fixed length buffer read
            and deleting local vars
            """
            try:
                del request
                del raw_request
                # build response message
                response_builder.build_response()
                writer.write(response_builder.response)
                await writer.drain()
                if response_builder.isFile: # It was a file...
                    writeLen = response_builder.contentLen
                    buf = bytearray(1024)
                    mv = memoryview(buf)
                    with response_builder.fd as fd:
                        while writeLen > 0:
                            readLen = fd.readinto(buf) # We have a handy 1024 byte buffer
                            writeLen = writeLen - readLen
                            writer.write(mv[0:readLen])
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
    from networking.WiFiConnection import WiFiConnection
    logger.debug(const('WiFiConnection starting...'))
    #if not WiFiConnection.start_station_mode(hostname = "john"):
    #    raise RuntimeError('network connection failed')

    ok = WiFiConnection.start_station_mode()
    mode = "?"
    if ok:
        # Set up as STA
        # Need to tell people SSID and password
        mode = "S"
    else:
        logger.warning("WiFi STA mode failed, cause %s : trying AP mode", WiFiConnection.statusText)
        password = 'password'
        if WiFiConnection.start_ap_mode(ssid="", password=password):
            logger.warning("WiFi AP mode started as network SSID %s Pwd: %s Server IP: %s", WiFiConnection.ap_ssid, password, WiFiConnection.ap_ip)
            mode = "A"
        else:
            raise RuntimeError('Unable to connect to network or start AP mode')

    logger.debug(const("Starting WebServer"))
    ws = WebServer([getValues], None, "/webdocs")
    # start web server task
    #ws.run()
    
    logger.debug(const("Entering main loop"))

    # main task control loop pulses board led
    while True:
        #flashLed.toggle_red_led()
        
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
