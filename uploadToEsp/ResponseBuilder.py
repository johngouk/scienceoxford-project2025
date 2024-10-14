"""
    ResponseBuilder
    
    Class to build a HTTP response, based on the values provided.
    
    __init__
        Provide a doc root or default to "/html"; if it doesn't include a
        "/" at the beginnign it gets added anyway!
    
    serve_static_file
        Serves the specified static file, if url = "/" then either the specified
        default file, or if not specified, "index.html"
        Sets content-type depending on the file suffix
        Sets HTTP response:
            200 - file exists
            404 - file doesn't exist
            
    set_body_from_dict
        Sets text to JSON stringify of the provided dictionary object
        Sets content-type to "application/json"
        
    build_response
        Creates response message using stored values etc.
        Files are opened, the fd stored in the ResponseBuilder object, and the caller
        then iterates reading/writing the file. Should really be passed the write stream
        so this class can do the iteration!

"""


import json
import os
import logging

from micropython import const
from ESPLogRecord import ESPLogRecord
logger = logging.getLogger(__name__)

# List of handled file types and returned content-type
# Based on iana.org/assignments/media-types/media-types.xhtml
fileToContentType = {
    const("htm"):	const("text/html"),
    const("html"):	const("text/html"),
    const("css"):	const("text/css"),
    const("csv"):	const("text/csv"),
    const("md"):	const("text/markdown"),
    const("rtf"):	const("text/richtext"),
    const("xml"):	const("text/xml"),
    const("unknown"):const("text/plain"),
    }

class ResponseBuilder:
    protocol = "HTTP/1.1"
    server = "ESP Micropython"

    def __init__(self, root="/"):
        # set default values
        # Better check it... and fix because I can't be bothered to
        # sort out everything after it's wrong
        if root[0] != "/":
            root = "/" + root
        self.docroot = root
        self.status = 200
        self.content_type = "text/html"
        self.body = ""
        self.response = ""
        # Added
        self.contentLen = 0
        self.fd = None
        self.isFile = False

    def set_content_type(self, content_type):
        self.content_type = content_type

    def set_status(self, status):
        self.status = status

    def set_body(self, body):
        self.body = body

    def serve_static_file(self, req_filename, default_file="/index.html"):
        # make sure filename starts with /
        if req_filename.find("/") == -1:
            req_filename = "/" + req_filename
        # remove query string
        if req_filename.find("?") != -1:
            req_filename, qs = req_filename.split("?", 1)
        # remove bookmark
        if req_filename.find("#") != -1:
            req_filename, qs = req_filename.split("#", 1)
        # filter out default file
        if req_filename == "/":
            req_filename = default_file
        # break filename into path and filename
        path, filename = req_filename.rsplit("/", 1)
        # reinstate root path for listdir
        if len(path) == 0:
            path = "/"
        # Add docroot
        path = path + self.docroot
        logger.debug("Path: %s Filename: %s", path, filename)
        #print(path, filename)
        # make sure working from root directory
        os.chdir("/")
        # get directory listing
        try:
            dir_contents = os.listdir(path)
        except Exception as e:
            logger.warning("Exception: %s Path: %s Filename: %s", e, path, filename)
            dir_contents = []
        # check if file exists
        if filename in dir_contents:
            # file found
            # get file type
            name, file_type = filename.rsplit(".", 1)
            if file_type in fileToContentType:
                self.content_type = fileToContentType[file_type]
            else:
                self.content_type = fileToContentType['unknown']
            """
            # load content
            file = open(path + "/" + filename)
            self.set_body(file.read())
            """
            # set up content
            filenameFull = path + "/" + filename
            self.contentLen = os.stat(filenameFull)[6]
            self.fd = open(filenameFull, 'rb') # Read as a proper bytes file
            self.isFile = True
            self.set_status(200)
        else:
            # file not found
            self.set_status(404)

    def set_body_from_dict(self, dictionary):
        self.body = json.dumps(dictionary)
        self.set_content_type("application/json")
        # added
        self.contentLen = len(self.body)

    def build_response(self):
        self.response = ""
        # status line
        self.response += self.__class__.protocol \
                         + " " \
                         + str(self.status) \
                         + " " \
                         + self.get_status_message() \
                         + "\r\n"
        # Headers
        self.response += "Server: " + self.server + "\r\n"
        self.response += "Content-Type: " + self.content_type + "\r\n"
        #self.response += "Content-Length: " + str(len(self.body)) + "\r\n"
        self.response += "Content-Length: " + str(self.contentLen) + "\r\n"
        self.response += "Connection: Closed\r\n"
        self.response += "\r\n"
        # body
        #if len(self.body) > 0:
        #    self.response += self.body
        """
            Body now handled using self.fd, passed to something that has
            the output stream handler as well
        """
        if not self.isFile:
            self.response += self.body

    def get_status_message(self):
        status_messages = {
            200: "OK",
            400: "Bad Request",
            403: "Forbidden",
            404: "Not Found"
        }
        if self.status in status_messages:
            return status_messages[self.status]
        else:
            return "Invalid Status"


if __name__ == "__main__":
    """
        Testing code: requires "index.html" in the current runtime directory
        Prints out the non-method attributes of the created ResponseBuilder object instance
    """
    # Dummy class and bound method so we can check for and ignore the object bound methods
    class dummyClass():
        def dummyFunc():
            pass
    dummy = dummyClass()
    logging.basicConfig(level=logging.DEBUG)
    from RequestParser import RequestParser
    request = const("GET /index.html?param1=1&param2=2 HTTP/1.1\r\nHost: localhost:80\r\nUser-Agent: SillyName\r\nAccept: text/html,*/*\r\n\r\n")
    rp = RequestParser(request)
    fullUrl = rp.full_url
    url = rp.url
    docroot = "/"
    rb = ResponseBuilder(docroot)
    logger.debug("Response Header: %s",rb.build_response())
    rb.serve_static_file(url)
    for attrName in dir(rb):
        attr = getattr(rb, attrName)
        if not isinstance(attr, type(dummy.dummyFunc)):
            logger.debug("Attr: %s Value: %s", attrName, attr)
     
    