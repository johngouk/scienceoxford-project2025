# Button class
# uses interrupts

from machine import Pin
import time

buttonPressed = False

def handle_interrupt(pin):
    global buttonPressed
    buttonPressed = True
    
pir = Pin(17, Pin.IN, Pin.PULL_DOWN)
pir.irq(trigger=Pin.IRQ_RISING, handler = handle_interrupt)
    
while True:
    if buttonPressed:
        print("Button pressed!")
        buttonPressed = False
    time.sleep_ms(100)