# test for most efficient/least costly text scrolling mechanism
# Simple slice from message => appears to use no additional memory once running on a scroll?!

from micropython import const

# LCD Libraries need to be copied to Flash
import time, asyncio, gc

class LCD():
    
    def __init__(self, cols=16, rows=2):
        self.rows = rows
        self.cols = cols
        # Set up the local internal display buffer (not the LCD RAM buffer!)
        self.lines = [""] * self.rows
        self.dirty = [False] * self.rows
        self._scrolling = [False] * self.rows
        self._scrollTask = [None] * self.rows
        self._displayingList = [False] * self.rows
        self._displayListTask = [None] * self.rows
        #print("init: _scrollTask: %s _scrolling: %s " % (self._scrollTask, self._scrolling))

        asyncio.create_task(self.runlcd())

    def putchar(self, c):
        print(c,end='')
        pass

    async def runlcd(self):  # Periodically check for changed text and update LCD if so
        while True:
            for row in range(self.rows):
                if self.dirty[row]:
                    msg = self[row]
                    #self.move_to(0,row)
                    # Write each char of msg to the relevant row
                    for thisbyte in msg:
                        self.putchar(thisbyte)
                        await asyncio.sleep_ms(0)  # Reshedule ASAP
                    self.dirty[row] = False
                    print()
            await asyncio.sleep_ms(20)  # Give other coros a look-in
            
    def _checkKillScroll(self, line):
        #print("cKS: line: %d" % line)
        if self._scrolling[line] and self._scrollTask[line] != None:
            # Kill the existing task
            self._scrollTask[line].cancel()
            self._scrollTask[line] = None
            self._scrolling[line] = False
        if self._displayingList[line] and self._displayListTask[line] != None:
            self._displayListTask[line].cancel()
            self._displayListTask[line] = None # Keep things tidy!
            self._displayingList[line] = False            
                   
    async def run_scroll(self, line, message, speed, times):
        # Speed - delay in msec; times - number of scroll repeats, -1 forever
        while times != 0:
            if not self._scrolling[line]: # Someone jumped in with a direct write to the line
                break
            print("Scroll cnt: ", times)
            if times > 0:
                times = times-1
            start = 0
            end = self.cols
            for i in range(0,len(message)-(self.cols-1)):
                if not self._scrolling[line]: # Someone jumped in with a direct write to the line
                    break
                # slice is probably a memory nightmare
                #self._setline(line, message[start:end])
                start += 1
                end += 1
                await asyncio.sleep_ms(speed)
            
    def scroll(self, line, message, speed=500, times=-1):
        """Scrolls a message on the specified line"""
        print("scroll: line: %d msg: %s" % (line, message))
        self._checkKillScroll(line)
        if len(message) <= self.cols:
            #print("Str <= %d: print" % maxLen)
            self.__setitem__(line, message) # No need to scroll!
            self._scrolling[line] = False
            self._scrollTask[line] = None
        else:
            self._scrolling[line] = True
            self._scrollTask[line] = asyncio.create_task(self.run_scroll(line, message, speed, times))

    async def run_scroll_wrap(self, line, message, speed, times):
        # Speed - delay in msec; times - number of scroll repeats, -1 forever
        while times != 0:
            if not self._scrolling[line]: # Someone jumped in with a direct write to the line
                break
            print("wrap scroll cnt: ", times)
            if times > 0:
                times = times-1
            mlen = len(message)
            if times <= 0:
                mlen = mlen - self.cols
            for i in range(mlen):
                if not self._scrolling[line]: # Someone jumped in with a direct write to the line
                    break
                #print("ws msg:",message)
                self._setline(line, message[0:self.cols])
                message = message[1:]+ message[0]
                await asyncio.sleep_ms(speed)
            
    def scroll_wrap(self, line, message, speed=500, times=-1):
        """Scrolls a message on the specified line"""
        print("wrap scroll: line: %d msg: %s" % (line, message))
        self._checkKillScroll(line)
        if message[len(message)-1] != " ": # Increase legibility
            message = message + " "
        if len(message) <= self.cols:
            #print("Str <= %d: print" % maxLen)
            self.__setitem__(line, message) # No need to scroll!
            self._scrolling[line] = False
            self._scrollTask[line] = None
        else:
            self._scrolling[line] = True
            self._scrollTask[line] = asyncio.create_task(self.run_scroll_wrap(line, message, speed, times))

    def _setline(self, line, message): # message <=16 chars
        """Actually sets the line of the display"""
        self.lines[line] = message  # Update stored line
        self.dirty[line] = True  # Flag its non-correspondence with the LCD device
        
    def __setitem__(self, line, message):  # Send string to display line 0 or 1
        """Set the indicated line buffer to 'message'"""
        print("_setitem: line: %d msg: %s" % (line, message))
        message = "{0:{1}.{1}}".format(message, self.cols)
        if message != self.lines[line]:  # Only update LCD if data has changed
            self._checkKillScroll(line) # Get rid of the scroll() if doing one
            self._setline(line, message)

    def __getitem__(self, line):
        """Get the indicated line buffer contents"""
        return self.lines[line]

    def displayList(self, line, itemList, interval):
        """Displays the list items in rotation, at interval rate, on the specified line; list items can
            be type str (strings!) or a function that returns strings
        """
        if line >= self.rows:
            logger.error("displayList: line %d specified, only %d rows!", line, self.rows)
            return
        if len(itemList) <= 0:
            logger.warning("displayList: Empty itemlist!")
            return
        self._checkKillScroll(line)
        self._displayingList[line] = True
        self._displayListTask[line] = asyncio.create_task(self._runDisplayList(line, itemList, interval))

    async def _runDisplayList(self, line, itemList, interval):
        while True and self._displayingList[line]:
            for i in range(len(itemList)):
                if not self._displayingList[line]:
                    break
                if not isinstance(itemList[i], str):
                    # Assumes function that returns str; assumes function takes index parameter
                    s = itemList[i](i)
                else:
                    s = itemList[i]
                self._setline(line, s) # Avoid the call to checkKillScroll!
                await asyncio.sleep(interval)
        
if __name__ == "__main__":
    """"Test LCD driver:
        Write init msg, then a string that is too long
        Then writes every 5 sec:
        row 0 - "nnnnn" incrementing counter
        row 1 - "UUUUUUUUUUUUUUUU" nanosecs tick
    """
        
    def item(i):
        v = ("item0str","item1str","item2str")
        return v[i]
    
    async def main():
        #lcd[0] = "Starting..."
        #await asyncio.sleep(2)
        #         123456789ABCDEF0<---HERE
        #lcd[1] = "This string should be cut short"
        #await asyncio.sleep(2)
        """
        gc.collect()
        start = gc.mem_free()
        lcd.scroll(0,"This is a very long message to scroll indefinitely", speed=500, times=100)
        await asyncio.sleep(0)
        #lcd.scroll(1,"0123456789ABCDEF0123456789abcdef") # Default scroll rate (400)
        #await asyncio.sleep(30)
        #lcd.scroll(0,"A long message that should be repeated") # Which is the new default!
        #await asyncio.sleep(10)
        #lcd.scroll(0,"This message should be overwritten and repeat")
        #await asyncio.sleep(10)
        for i in range(5):
            await asyncio.sleep(5)
            gc.collect()
            now = gc.mem_free()
            print("scroll: Used: %d" % (start - now))
        """

        gc.collect()
        start = gc.mem_free()
        lcd.scroll_wrap(0,"0123456789A123456789B123456789", speed=500, times=1)
        await asyncio.sleep(0)
        for i in range(4):
            await asyncio.sleep(5)
            gc.collect()
            now = gc.mem_free()
            print("wrap scroll: Used: %d" % (start - now))
            
        print("Testing string displayList")
        lcd.displayList(1, ("item0", "item1", "item2"), 1)
        await asyncio.sleep(30)

        lcd[1] = "Direct show value"
        await asyncio.sleep(3)

        print("Testing function displayList")
        lcd.displayList(1, (item, item, item), 1)
        await asyncio.sleep(10)

        lcd[1] = "Direct show value"
        await asyncio.sleep(3)
        
    try:
        lcd = LCD() # Default values
        # start the main async tasks
        asyncio.run(main())
    finally:
        # reset and start a new event loop for the task scheduler
        asyncio.new_event_loop()