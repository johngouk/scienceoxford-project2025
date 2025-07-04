import time # Used for sleep()

from RGBLed import RGBLed # get a copy of the RGBLed code

'''
    RGBLed things you can do:
    on() - turns it on, with whatever colour it has been set to
    off() - yeh, off
    toggle() - if it's on, go off, if it's off, go on
    setRGBColour(colourList) - set the colour (0-255)using a list e.g [255,255,255] is all on
    setRawColour(rawList) - set the colour using the raw duty cycle value (0-65535) e.g. [500,500,500]
'''

# If this is run from the Run button, it's "__main__"

if __name__ == "__main__":
    
    # Set up the values for the colours - you can adjust these!
    # These are lists of the right values (0-255) for each RGB colour
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
                 
    # clist is a list of colour values and their names
    # e.g. ['red',red] - 'red' is the string with the name 'red', and red
    #		is the list of settings to get red
    clist = [['red',red],
             ['green',green],
             ['blue',blue],
             ['coral',coral],
             ['orange',orange],
             ['darkgreen',darkgreen],
             ['cyan',cyan],
             ['aquamarine',aquamarine],
             ['dodgerblue',dodgerblue],
             ['fuchsia',fuchsia],
             ['deeppink',deeppink],
             ['lightgray',lightgray],
             ['chocolate',chocolate] 
            ]
    
    # The pins wired into the AQM
    Red_pin = 14
    Green_pin = 13
    Blue_pin = 4
    
    # Make an RGBLed object with the right pin values
    led = RGBLed(Red_pin,Green_pin,Blue_pin)
    
    # Go through the list of colours, turning on/off with a 1 sec delay
    # and demonstrating the toggle() function
    
    for c in clist:
        #print(c)
        led.setRGBColour(c[1])
        print(f"{c[0]} *** on ***")
        led.on()
        time.sleep(1)
        print(f"{c[0]} *** off ***")
        led.off()
        time.sleep(1)
        print(f"{c[0]} *** toggle on ***")
        led.toggle()
        time.sleep(1)
        print(f"{c[0]} *** toggle off ***")
        led.toggle()
        time.sleep(1)
    

    # You can also change the colour gradually, without turning the led on/off
    # The overall relative brightness on the AQM of R G, and B is set by the values of the
    # the resistors soldered on the board for each value, so they should be about the same
    # brightness at full on.
    led.on()
    g = 10 # You can adjust this
    b = 10 # and this... and probably should, my AQM board has different resistor values
    # Since Red starts off, and goes to full on, you should see some interesting colours
    # It's surprising how little of a colour you need to change the overall colour
    # The loop just leaves G & B the same, and gradually adds more R
    for r in range (0,256,10):
        led.setRGBColour([r,g,b])
        time.sleep(0.2)
