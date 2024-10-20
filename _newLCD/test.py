'''
    I2C LCD1602 demo

    Author: shaoziyang
    Date:   2018.2

    http://www.micropython.org.cn


    LCD1602 Behaviour
    It looks like the LCD has a buffer which can be written to at any time, and a view on which is displayed
    in the 16x2 display starting at whatever position the display window has been shifted L or R to.
    So to make this work properly you probably have to keep track of the buffer and display window and their
    relative positions.
    https://www.sparkfun.com/datasheets/LCD/HD44780.pdf
    From test on the displayed values, looks like we have A00 ROM code
    DDRAM - Display Data RAM
    CGRAM - Character Generator RAM
    Commands:
    0x
    0x01 - clear (clears display, sets DDRAM addr=0)
    0x02 - return home (set DDRAM addr=0, set display to original position, DDRAM unchanged)


'''
from machine import I2C, Pin
from i2c_lcd1602 import I2C_LCD1602
from time import sleep_ms

DEFAULT_I2C_ADDR = 0x27

#i2c = I2C(1, sda=Pin(9), scl=Pin(10))
i2c = I2C(0, scl=Pin(18), sda=Pin(19))

lcd = I2C_LCD1602(i2c)

lcd.clear()

for i in (0,3):
  lcd.clear(); 
  lcd.puts("Welcome to",i,0); 
  sleep_ms(500); 
lcd.puts("ElectroniClinic", 0,1); 
 
"""
print("lcd.print()")
#          0000000000111111111122222222223333333333
#          0123456789012345678901234567890123456789
lcd.print("0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF")
sleep_ms(5000)

print("lcd.puts()")
lcd.puts("This is a long string, what will happen?", 0,0)
sleep_ms(5000)


n = 0
while 1:
    lcd.puts(n, 0, 1)
    n += 1
    sleep_ms(1000)
"""