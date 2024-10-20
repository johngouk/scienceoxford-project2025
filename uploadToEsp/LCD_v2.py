"""
    LCD - script to provide access to a LCD1602 SPI-attached display

    LCD Operations

    def clear()        Clears the LCD display and moves the cursor to the top left corner.
    def on()       Turns on (i.e. unblanks) the LCD.
    def off()       Turns off (i.e. blanks) the LCD.
    def backlight(T|F)       Turns the backlight on. This isn't really an LCD command, but some modules have backlight controls.
    def shr()   Shift display right (Actually shifts display window on buffer left) 
    def shl()   Shift display left  (v.v.)
    def char(ch, x=-1, y=0)  Write char at buffer location (0:x:15, 0:y:1), moves cursor on in buffer
    def puts(s, x=0, y=0) Write string into buffer at location (x,y); uses char() to do that
    def print(s) Writes string s at current buffer location, accounting for \n chars
    def show_cursor()       Causes the cursor to be made visible.
    def hide_cursor()       Causes the cursor to be hidden.
    def blink_cursor_on()       Turns on the cursor, and makes it blink.
    def blink_cursor_off()       Turns on the cursor, and makes it no blink (i.e. be solid).
    def move_to(cursor_x, cursor_y)       Moves the cursor position to the indicated position. The cursor position is zero based (i.e. cursor_x == 0 indicates first column).
    def putchar(char)       Writes the indicated character to the LCD at the current cursor position, and advances the cursor by one position.
    def putstr(string)       Write the indicated string to the LCD at the current cursor position and advances the cursor position appropriately.

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

from i2c_lcd1602 import I2C_LCD1602
#from esp8266_i2c_lcd import I2cLcd

class LCD(I2C_LCD1602):

    DEFAULT_I2C_ADDR = 0x27
    DEFAULT_I2C_FREQ = 100000

    def __init__(self, i2c=0, sclPin=18, sdaPin=19, columns=16, lines=2):
        logger.info(const("initialising LCD: I2C: %d SCL: %d SDA: %d freq: %d col: %d lines: %d"),
                    i2c, sclPin, sdaPin, LCD.DEFAULT_I2C_FREQ, columns, lines)
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.i2cUnit = i2c
        self.scl = Pin(self.sclPin, Pin.PULL_UP)
        self.sda = Pin(self.sdaPin, Pin.PULL_UP)
        self.l = lines
        self.c = columns
        try:
            super().__init__(I2C(self.i2cUnit, scl=self.scl, sda=self.sda, freq=LCD.DEFAULT_I2C_FREQ)
                             , LCD.DEFAULT_I2C_ADDR
                             #, lines, columns
                             )
        except Exception as e:
            logger.error("Exception %s initialising LCD; check pin numbers, connections: I2C Unit: %d Pins - SCL: %d SDA: %d",  
                         e, self.i2cUnit, self.sclPin, self.sdaPin)
            raise e

    # Horrible function that does something until I find a better I2C LCD implementation...
    async def updateLCD(self, interval, line0, line1):
        blank = const('                ')
        while True:
            self.move_to(0,0) # use first row
            self.putstr(blank)
            self.move_to(0,0) # use first row
            self.putstr(line0())
            
            self.move_to(0,1) # use second row
            self.putstr(blank)
            self.move_to(0,1) # use second row
            self.putstr(line1())
            await asyncio.sleep(interval)