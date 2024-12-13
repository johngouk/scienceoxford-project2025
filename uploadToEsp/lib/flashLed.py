import asyncio
from machine import Pin, Signal

class flashLed:
    #import gc
    # red led
    # Defaults
    ledPin = Pin(2, Pin.OUT, value=1)
    led = Signal(ledPin, invert=False)
    #led = Pin(28, Pin.OUT)
    led_state = 0


    def __init__(self, pin = 2, invert = False, interval=1):
        # get everything into a starting state
        # red led
        ledPin = Pin(pin, Pin.OUT, value=1)
        led = Signal(ledPin, invert=invert)
        led_state = 0
        self.show_red_led()
        asyncio.create_task(self.run(interval))

    async def run(self, interval):
        while True:
            self.toggle_red_led()
            await asyncio.sleep(interval)

    # red led handlers
    def show_red_led(cls):
        cls.led.value(cls.led_state)

    def toggle_red_led(cls):
        cls.led_state = 0 if cls.led_state == 1 else 1
        cls.show_red_led()

    def get_red_led(cls):
        return 0 if cls.led_state == 0 else 1

    def set_red_led(cls, state):
        cls.led_state = 0 if state == 0 else 1
        cls.show_red_led()

async def main():
        f = flashLed(invert=True)
        while True:
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
    