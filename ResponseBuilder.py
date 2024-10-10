"""
    ResponseBuilder
    
    Class to build a HTTP response, based on the values provided.
    
    __init__
        Provide a doc root or default to "/html"; if it doesn't include a
        "/" at the beginnign it gets added anyway!
    
    serve_static_file
        Serves the specified static file, if url = "/" then either the specified
        default file, or if not specified, "index.html"
        File is read into a variable, so don't go big!
        Sets content-type depending on the file suffix
        Sets HTTP response:
            200 - file exists
            404 - file doesn't exist
            
    set_body_from_dict
        Sets text to JSON stringify of the provided dictionary object
        Sets content-type to "application/json"
        
    build_response
        Creates response message using stored values etc.
        Note that files are stored in memory, and attached.

"""


import json
import os


class ResponseBuilder:
    protocol = "HTTP/1.1"
    server = "ESP Micropython"

    def __init__(self, root="/html"):
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
        #print(path, filename)
        # make sure working from root directory
        os.chdir("/")
        # get directory listing
        dir_contents = os.listdir(path)
        # check if file exists
        if filename in dir_contents:
            # file found
            # get file type
            name, file_type = filename.rsplit(".", 1)
            if file_type == "htm" or file_type == "html":
                self.content_type = "text/html"
            elif file_type == "js":
                self.content_type = "text/javascript"
            elif file_type == "css":
                self.content_type = "text/css"
            else:
                # let browser work it out
                self.content_type = "text/html"
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
