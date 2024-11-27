import os, json

class NetworkCredentials:
    creds = ('ssid', 'password')
    fname = 'NetCreds.json'
    
    @classmethod
    def setNetCreds(self, ssid, password):
        self.creds = (ssid, password)
        with open(self.fname, "w") as f:
            json.dump(self.creds, f)
        # All done
    
    @classmethod
    def getNetCreds(self):
        try:
            fs = os.stat(self.fname)
            with open(self.fname, "r") as f:
                self.creds = json.load(f)
        except OSError:
            pass
        return self.creds
    
if __name__ == "__main__":
    print (NetworkCredentials.getNetCreds())
    NetworkCredentials.setNetCreds('hurray', 'fibs')
    print (NetworkCredentials.getNetCreds())
    
    