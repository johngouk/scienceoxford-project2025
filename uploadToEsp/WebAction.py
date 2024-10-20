"""

    WebAction
    Class to handle actions reuslting from various HTTP command/URL/query params/POST body combinations

    My thinking here is:
    Cmd		URL					QPs		Body			Action
    GET		/<pathToFile>								Serve the file, Content-Type according to file suffix
    GET		/file/<pathToFile>							Serve the file as a binary object
    GET		/data/										Return all current data values as JSON k/v list
    GET		/config/									Return current server config values
    POST	/cmd/<action>				JSON k/v list	Perform the requested action with supplied values

"""
# Handy script for checking target implementation
import sys
if sys.implementation.name == "micropython":
    print("micropython")
    from micropython import const
    #     Do something     
elif sys.implementation.name == "cpython":
    print("lappie")
    def const(x):
        return x
        
import os
if "ESP32" in os.uname().machine:
    print("ESP32")
#     Do something     
    if "S3" in os.uname().machine:
        print("S3")
#     Do something     
elif "ESP8266" in os.uname().machine:
    print ("ESP8266")
#     Do something     



import asyncio, time, random, logging
from micropython import const

logger = logging.getLogger(__name__)
from ESPLogRecord import ESPLogRecord
logger.record = ESPLogRecord()

class WebAction():
    
    actionCmds = ["file", "data", "cmd", "config"]
    
    def __init__(self):
        
    def handleRequest(self, command, url, qParams, bodyParams):
        # URL has already had the docroot added to it if applicable
        # Analyse URL first
        
        urlParts = url.split("/")
        if urlParts[0] in actionCmds and len(urlParts) == 1:
            action = actionCmds.index(urlParts[0])
            print("Found verb %s %d" % (urlParts[0], action))
        else: # Let's pretend it's a file for now
            print("Found file %s" % url)
            
        match command:
            case "GET":
                print("Found GET")
                
                
            case "POST":
                print("Found POST")
            