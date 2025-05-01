# Comedy Class to hold the MOTD so we can refer to it from anywhere >face palm<

class MOTD:
    _message = 'Message of the Day'
    
    @classmethod
    def setMessage(self, message):
        self._message = message
            
    @classmethod
    def getMessage(self):
        return self._message
