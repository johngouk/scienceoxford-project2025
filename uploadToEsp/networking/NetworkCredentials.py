import os, json

class NetworkCredentials:
    creds = {"hostname":"", "ssid":"ssid", "password":"password"}
    fname = 'NetCreds.json'
    
    @classmethod
    def setNetCreds(self, ssid, password):
        # We already read the hostname, ssid and pwd on getNetCreds()
        self.creds["ssid"] = ssid
        self.creds["password"]= password
        self._writeCreds()
        # All done
    
    @classmethod
    def getNetCreds(self):
        try:
            fs = os.stat(self.fname)
            with open(self.fname, "r") as f:
                self.creds = json.load(f)
                if not 'ssid' in self.creds:
                    self.creds['ssid'] = 'ssid'
                if not 'password' in self.creds:
                    self.creds['password'] = 'password'
                if not 'hostname' in self.creds:
                    self.creds['hostname'] = '' # Leave this blank so we get default!
        except OSError: # There are no creds - write some
            pass
        finally: # Always write it out in case we fixed it up 
            self._writeCreds()
        return self.creds
    
    @classmethod
    def setHostname(self, hostname=""):
        if hostname != "":
            self.creds['hostname'] = hostname
            self._writeCreds()

    @classmethod
    def getHostname(self):
        return self.creds['hostname']

    @classmethod
    def _writeCreds(self):
        with open(self.fname, "w") as f:
            json.dump(self.creds, f)
    
if __name__ == "__main__":
    print (NetworkCredentials.getNetCreds())
    NetworkCredentials.setNetCreds('hurray', 'fibs')
    print (NetworkCredentials.getNetCreds())
    
    