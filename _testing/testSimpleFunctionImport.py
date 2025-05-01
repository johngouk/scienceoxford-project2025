from _modules.simpleFunction import simpleFunction

MOTD = 'the message'
SSID = 'old'
pwd = 'oldPwd'

def setMotd(newMotd):
    global MOTD
    MOTD = newMotd
    
def setNetwork(newSsid, newPwd):
    global SSID, pwd
    SSID = newSsid
    pwd = newPwd
    
print(MOTD, SSID, pwd)
print('SimpleFunction:',simpleFunction(setMotd, setNetwork))
print(MOTD, SSID, pwd)
