
"""
    actionHandler() - likely to be moved to a separate Controller object, which will also process
        the button presses in a MVC-type model
"""

import logging
from micropython import const

# Note that you can't use the module name "network" for your own stuff - Python has already used it! 
from networking.WiFiConnection import WiFiConnection
from web.url_parse import url_parse
from web.MOTD import MOTD

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()


# Handler for web "action" page accesses
def actionHandler(action, params):
    #global MOTD # Don't like this but needs must...
    actions = {"network":("hostname","ssid","password"), "message":("MOTD",)}
    logger.debug(const("actionHandler: actions: %s"), actions)
    logger.debug(const("actionHandler: action: %s:type:%s, params:%s"), action, type(action), params)
    # Check required params
    if action in actions: # Legal action
        for x in actions[action]: # Check for param 
            if x not in params:
                logger.debug(const("actionHandler: param:%s not in params %s for action %s, "), x, params, action)
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
                WiFiConnection.setNetCreds(ssid, password)
                logger.info(const("Network config updated: hostname: %s SSID: %s Pwd: %s"), hostname, ssid, "********")
        elif action == "message":
            # MOTD
            logger.debug("actionHandler: MOTD type:%s, value:%s", type(params['MOTD']), params['MOTD'])
            logger.debug("actionHandler: MOTD parsed:%s", url_parse(params['MOTD']))
            MOTD.setMessage(url_parse(params['MOTD']))
            logger.info(const("actionHandler: MOTD set: %s "), MOTD.getMessage() )
    
        return("thanks.html")
    else: # Action not in actions!
        logger.error(const("actionHandler: Action '%s' requested, not implemented"), action)
        
    # Fall through to here
    logger.error(const("actionHandler: action: %s not implemented - returning default page"), action)
    return "index.html" # Not implemented
