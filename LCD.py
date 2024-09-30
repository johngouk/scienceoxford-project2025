"""
    LCD - script to provide access to a LCD1602 SPI-attached display

    LCD Operations

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

"""

from machine import Pin
from machine import I2C
# LCD Libraries need to be copied to Flash
from esp8266_i2c_lcd import I2cLcd
import time, asyncio



class LCD(I2cLcd):

    DEFAULT_I2C_ADDR = 0x27

    def __init__(self, i2c=0, sclPin=18, sdaPin=19, columns=16, lines=2):
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.i2cUnit = i2c
        self.scl = Pin(self.sclPin, Pin.PULL_UP)
        self.sda = Pin(self.sdaPin, Pin.PULL_UP)
        #self.i2c = I2C(self.i2cUnit, scl=self.scl, sda=self.sda, freq=100000)
        I2cLcd.__init__(self, I2C(self.i2cUnit, scl=self.scl, sda=self.sda, freq=100000), LCD.DEFAULT_I2C_ADDR, lines, columns)

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
        
