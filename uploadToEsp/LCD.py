"""
    LCD - script to provide access to a LCD1602 SPI-attached display

    LCD Operations
    
    The most useful operation is setting one of the n (in this case n in range(0,2)) rows of the display
    e.g. lcd[0] = "Hello world!"
    which will set the current line[n] of the display until you set it differently.

    def clear()        Clears the LCD display and moves the cursor to the top left corner.
    def show_cursor()       Causes the cursor to be made visible.
    def hide_cursor()       Causes the cursor to be hidden.
    def blink_cursor_on()       Turns on the cursor, and makes it blink.
    def blink_cursor_off()       Turns on the cursor, and makes it no blink (i.e. be solid).
    def display_on()       Turns on (i.e. unblanks) the LCD.
    def display_off()       Turns off (i.e. blanks) the LCD.
    def backlight_on()       Turns the backlight on. This isn't really an LCD command, but some modules have backlight controls.
    def backlight_off()       Turns the backlight off. This isn't really an LCD command, but some modules have backlight controls.
    def move_to(cursor_x, cursor_y)       Moves the cursor position to the indicated position. The cursor position is zero based (i.e. cursor_x == 0 indicates first column).
    def putchar(char)       Writes the indicated character to the LCD at the current cursor position, and advances the cursor by one position.
    def putstr(string)       Write the indicated string to the LCD at the current cursor position and advances the cursor position appropriately.
    def shr()             Shift (entire) display right
    def shl()             Shift (entire) display left

"""
from micropython import const
from machine import Pin
from machine import I2C

# LCD Libraries need to be copied to Flash
import time, asyncio
import logging

logger = logging.getLogger(__name__)
try:
    from ESPLogRecord import ESPLogRecord
    logger.record = ESPLogRecord()
except ImportError:
    pass

from esp8266_i2c_lcd import I2cLcd

class LCD(I2cLcd):

    DEFAULT_I2C_ADDR = 0x27
    DEFAULT_I2C_FREQ = 100000

    def __init__(self, i2c=0, sclPin=18, sdaPin=19, cols=16, rows=2):
        logger.info(const("initialising LCD: I2C: %d SCL: %d SDA: %d freq: %d cols: %d rows: %d"),
                    i2c, sclPin, sdaPin, LCD.DEFAULT_I2C_FREQ, cols, rows)
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.i2cUnit = i2c
        self.scl = Pin(self.sclPin, Pin.PULL_UP)
        self.sda = Pin(self.sdaPin, Pin.PULL_UP)
        self.rows = rows
        self.cols = cols
        # Set up the local internal display buffer (not the LCD RAM buffer!)
        self.lines = [""] * self.rows
        self.dirty = [False] * self.rows

        try:
            super().__init__(I2C(self.i2cUnit, scl=self.scl, sda=self.sda, freq=LCD.DEFAULT_I2C_FREQ),
                                 LCD.DEFAULT_I2C_ADDR, rows, cols)
        except Exception as e:
            logger.error("Exception %s initialising LCD; check pin numbers, connections: I2C Unit: %d Pins - SCL: %d SDA: %d",  
                         e, self.i2cUnit, self.sclPin, self.sdaPin)
            raise e

        asyncio.create_task(self.runlcd())

    async def runlcd(self):  # Periodically check for changed text and update LCD if so
        while True:
            for row in range(self.rows):
                if self.dirty[row]:
                    msg = self[row]
                    self.move_to(0,row)
                    # Write each char of msg to the relevant row
                    for thisbyte in msg:
                        self.putchar(thisbyte)
                        await asyncio.sleep_ms(0)  # Reshedule ASAP
                    self.dirty[row] = False
            await asyncio.sleep_ms(20)  # Give other coros a look-in

    def __setitem__(self, line, message):  # Send string to display line 0 or 1
        """Set the indicated line buffer to 'message'"""
        message = "{0:{1}.{1}}".format(message, self.cols)
        if message != self.lines[line]:  # Only update LCD if data has changed
            self.lines[line] = message  # Update stored line
            self.dirty[line] = True  # Flag its non-correspondence with the LCD device

    def __getitem__(self, line):
        """Get the indicated line buffer contents"""
        return self.lines[line]

if __name__ == "__main__":
    """"Test LCD driver:
        Write init msg, then a string that is too long
        Then writes every 5 sec:
        row 0 - "nnnnn" incrementing counter
        row 1 - "UUUUUUUUUUUUUUUU" nanosecs tick
    """
    async def main():
        lcd[0] = "Starting..."
        await asyncio.sleep(2)
        lcd[1] = "This string should be cut short"
        await asyncio.sleep(2)
        i = 0
        while True:
            i += 1
            lcd[0] = "%05d"%i
            lcd[1] = "%016d"%time.ticks_us()
            await asyncio.sleep(5)
    try:
        lcd = LCD() # Default values
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()
