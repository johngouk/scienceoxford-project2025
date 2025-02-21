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
    print("machine Pin, PWM imported")
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
        _pin = None
        _freq = 0
        _dc = 0
        def __init__(self, pin):
            print(f"\tPWM init - {pin}")
            self._pin = pin
        def freq(self, f):
            print(f"\tPWM freq - {f}")
            self._freq = f
        def duty_u16(self, dc):
            print(f"\tPWM dt - {dc}")
            self._dc = dc

import time



class RGBLed:
    
    _pwms = []
    _last = [65535, 65535, 65535] # Stores native u16 duty cycle value
    _on = False
    
    def __init__(self, RPin, GPin, BPin): # Constructor
        self._pwms = [PWM(Pin(RPin)), PWM(Pin(GPin)), PWM(Pin(BPin))]
        [pwm.freq(1000) for pwm in self._pwms]
        
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
    def toggle():
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
    
    # Takes "native" DC values 0-65536 for finest coour graduation
    def setRawColour(self, raw): #x raw = [n, n, n] 0 <= n < 65536
        for i in range(0,3):
            self._last[i] = max(0,min(raw[i],65535))
        


if __name__ == "__main__":
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
                 
    clist = [coral,orange,darkgreen,cyan,aquamarine,dodgerblue,fuchsia,deeppink,lightgray,chocolate]
    
    Red_pin = 18
    Green_pin = 19
    Blue_pin = 20
    
    led = RGBLed(Red_pin,Green_pin,Blue_pin)
    for c in clist:
        led.setRGBColour(c)
        print("*** on ***")
        led.on()
        time.sleep(1)
        print("*** off ***")
        led.off()
        time.sleep(1)
        