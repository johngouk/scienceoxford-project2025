# RGB LED test code - uses PWM to adjust colours
'''
    This uses Pulse Width Modulation to adjust the perceived brightness of the LEDs
    The LEDs get pulsed on and off at a specified frequency, but the width of the pulse (the Duty Cycle)
    makes the LED look dimmer or brighter, as the pulse is narrower or wider - the LED is effectively on
    for less or more time.
    To turn the LEDs full on, the Duty Cycle is 100%; off it's 0%
    THe only tricky bit is the PWM class uses 0-65535 (16 bits) as the min/max Duty Cycle value,
    so 0 is off, and 65535 is full on.
    
    https://docs.micropython.org/en/latest/library/machine.PWM.html
    
'''

# Workaround for use of micropython machine library for Pin and PWM
# so it can be tested in CPython
try:
    from machine import Pin, PWM
    #print("machine Pin, PWM imported")
    mpy_host = True
except ImportError:
    print("machine Pin, PWM not imported - substitute")
    mpy_host = False
    # Dummy Pin class
    class Pin:
        _pin = None
        def __init__(self, pin):
            self._pin = pin
            print(f"\tPin init - {pin}")
    # dummy PWM class
    class PWM:
        def __init__(self, pin,freq=2000,duty_u16=0):
            print(f"\tPWM init - {pin}")
            self._pin = pin
            self._freq = freq
            self._dc = duty_u16
        def freq(self, f):
            print(f"\tPWM {self._pin._pin} freq - {f}")
            self._freq = f
        def duty_u16(self, dc):
            print(f"\tPWM {self._pin._pin} dc - {dc}")
            self._dc = dc

import time



class RGBLed:
    
    _debug = False
        
    def _print(self, s):
        if self._debug:
            print(s)
            
    def __init__(self, RPin, GPin, BPin): # Constructor
        self._print(f'init: pins {RPin}, {GPin}, {BPin}')
        self._last = [0, 0, 0] # Stores native u16 duty cycle value
        self._on = False
        self._freq = 2000

        # Critical to initialise PWM objects with required frew and 0% duty cycle!!
        self._pwms = [PWM(Pin(RPin),freq=self._freq,duty_u16=0),
                      PWM(Pin(GPin),freq=self._freq,duty_u16=0),
                      PWM(Pin(BPin),freq=self._freq,duty_u16=0)]
        
    # Turns LEDs off
    def off(self):
        [pwm.duty_u16(0) for pwm in self._pwms]
        self._on = False
    
    # Turns LEDs on to last setting, white if none previously
    # pwm.duty_u16() defines the duty cycle - 0% is off, 100% is full on.
    # Duty cycle is expressed as 0-65535 or all 0s to all 1s in 16 bits
    # 50% is thus 65535/2, for example, or the required number is 65535 * %age
    def on(self):
        for i in range(0,3):
            self._pwms[i].duty_u16(self._last[i]) 
        self._on = True

    # Toggle: does the other thing, returns previous on/off state
    def toggle(self):
        if self._on:
            self.off()
        else:
            self.on()
        return not self._on

    # Takes R/G/B values 0-255, as in HTML-style colour definitions and scales for PWM
    def setRGBColour(self, RGB): # RGB = [n, n, n] 0 <= n <= 255 rescaled for 65536 max
        for i in range(0,3):
            #               prevent anything but 0<=n<=255
            self._last[i] = max(0,min(RGB[i],255))*256
        if self._on:
            # print('LED was on, re-displaying')
            self.on()
    
    # Takes "native" DC values 0-65536 for finest colour graduation
    def setRawColour(self, raw): #x raw = [n, n, n] 0 <= n < 65536
        for i in range(0,3):
            self._last[i] = max(0,min(raw[i],65535))
        if self._on:
            # print('LED was on, re-displaying')
            self.on()
        


if __name__ == "__main__":
    red = [255,0,0]
    green = [0,255,0]
    blue = [0,0,255]
    coral = [255,127,80]
    orange = [255,165,0]
    darkgreen = [0,100,0]
    cyan = [0,255,255]
    aquamarine = [127,255,212]
    dodgerblue = [30,144,255]
    fuchsia = [255,0,255]
    deeppink = [255,20,147]
    lightgray = [211,211,211]
    chocolate = [210,105,30]
                 
    #            ['red',red],
    clist = [['red',red],['green',green],['blue',blue],
            ['coral',coral],['orange',orange],['darkgreen',darkgreen],['cyan',cyan],['aquamarine',aquamarine],
            ['dodgerblue',dodgerblue], ['fuchsia',fuchsia],['deeppink',deeppink],['lightgray',lightgray],
            ['chocolate',chocolate] 
            ]
    
    Red_pin = 14
    Green_pin = 13
    Blue_pin = 4
    
    led = RGBLed(Red_pin,Green_pin,Blue_pin)
    
    for c in clist:
        #print(c)
        led.setRGBColour(c[1])
        print(f"{c[0]} *** on ***")
        led.on()
        time.sleep(1)
        print(f"{c[0]} *** off ***")
        led.off()
        time.sleep(1)
        led.toggle()
        time.sleep(1)
        led.toggle()
        time.sleep(1)
        
    '''
    for c in clist:
        print(f"{c[0]} *** on ***")
        led.setRGBColour(c[1])
        led.on()
        time.sleep(1)
    
    led.on()
    for r in range(0,256,10):
        for g in range(256,0,-10):
            for b in range(256,0,-10):
                led.setRGBColour([r,g,b])
                time.sleep(0.1)
    '''  