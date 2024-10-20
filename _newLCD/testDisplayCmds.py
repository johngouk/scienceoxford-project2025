'''
    lay Data RAM
    CGRAM - Character Generator RAM
    Commands:
    0x
    0x01 - clear (clears display, sets DDRAM addr=0)
    0x02 - return home (set DDRAM addr=0, set display to original position, DDRAM unchanged)


'''
from machine import I2C, Pin
from i2c_lcd1602 import I2C_LCD1602
import time

def printTicks(text, ticks):
    print(text % ticks)

t0 = time.ticks_us()
i2c = I2C(0, scl=Pin(18), sda=Pin(19))
t1 = time.ticks_us()
printTicks("I2C init: %d usec", time.ticks_diff(t1, t0))

t0 = time.ticks_us()
lcd = I2C_LCD1602(i2c)
t1 = time.ticks_us()
printTicks("LCD init: %d usec", time.ticks_diff(t1, t0))

t0 = time.ticks_us()
lcd.clear()
t1 = time.ticks_us()
printTicks("LCD clear: %d usec", time.ticks_diff(t1, t0))
"""
print("test write 40 chars to DDRAM")
start = 0x30
end = start+40
xLen = 16
print("start: %2x %s end %2x %s" % (start, chr(start), end, chr(end)))
for i in range (start, end):
    print("%2x " % i, end='')
    lcd.char(i)
print()

scroll = end - start - xLen
print("scrolling left %d chars" % scroll)
for i in range(0,scroll):
    lcd.shl()
    time.sleep_ms(400)

time.sleep_ms(2000)

print("scrolling right %d chars" % scroll)
for i in range(0,scroll):
    lcd.shr()
    time.sleep_ms(400)

lcd.clear()
lcd.print("Try a scroll")
time.sleep_ms(400)
lcd.clear()

#longStr = "0123456789ABCDEF0123456789abcdef01234567"
longStr = "0123456789ABCDEF0123456789abcdef01234567"
maxLen = 16
if len(longStr) <= maxLen:
    print("Str <= %d: print" % maxLen)
    lcd.puts(longStr, x=0, y=0)
else:
    print("Str > %d: scroll" % maxLen)
    lcd.puts(longStr[0:maxLen], x=0, y=0)
    for i in range(maxLen,len(longStr)):
        lcd.shl()
        lcd.char(ord(longStr[i]))
        time.sleep_ms(400)
       
print("Scroll a short msg")
lcd.clear()
lcd.puts("Starting... IP:192.168.100.100", x=0, y=0)
for i in range (0,100):
    print("%d " % i, end='')
    time.sleep_ms(400)    
    lcd.shl()
""" 
maxLen = 16
longStr = "0123456789ABCDEF0123456789abcdef01234567"
line1 = "0123456789ABCDEF0123456789abcdef01234567"

lcd.clear()
lcd.puts(line1, x=0, y=0)
if len(longStr) <= maxLen:
    print("Str <= %d: print" % maxLen)
    lcd.puts(longStr, x=0, y=0)
else:
    print("Str > %d: scroll" % maxLen)
    start = 0
    end = maxLen
    for i in range(0,len(longStr)-(maxLen-1)):
        lcd.puts(longStr[start:end], x=0, y=1)
        start += 1
        end += 1
        time.sleep_ms(400)
