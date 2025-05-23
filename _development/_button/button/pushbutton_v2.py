# pushbutton.py

# Copyright (c) 2018-2023 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

import asyncio
import utime as time
from . import launch, Delay_ms

try:
    from machine import TouchPad
except ImportError:
    pass


class Pushbutton:
    debounce_ms = 50
    long_press_ms = 1000
    double_click_ms = 400

    def __init__(self, pin, suppress=False, sense=None):
        self._pin = pin  # Initialise for input
        self._supp = suppress
        self._dblpend = False  # Doubleclick waiting for 2nd click
        self._dblran = False  # Doubleclick executed user function
        self._tf = False
        self._ff = False
        self._df = False
        self._ld = False  # Delay_ms instance for long press
        self._dd = False  # Ditto for doubleclick
        self._lf = False  # JG ld callback function
        
        self._press_pending = False
        # Convert from electrical to logical value
        self._sense = pin.value() if sense is None else sense
        self._state = self.rawstate()  # Initial state
        self._run = asyncio.create_task(self._go())  # Thread runs forever

    async def _go(self):
        while True:
            self._check(self.rawstate())
            # Ignore state changes until switch has settled. Also avoid hogging CPU.
            # See https://github.com/peterhinch/micropython-async/issues/69
            await asyncio.sleep_ms(Pushbutton.debounce_ms)

    def _check(self, state):
        if state == self._state:
            return
        # State has changed: act on it now.
        self._state = state
        if state:  # Button pressed: launch pressed func
            # JG We only want a definite press, not the first of a double or
            # JG a long start...
            if self._tf:
            #     launch(self._tf, self._ta)
                self._press_pending = True # JG
            # If there's a long func: start long press delay if no double click running
            # (case where a short click is rapidly followed by a long one, iss 101).
            if self._ld and not self._dblpend: # JG (self._df and self._dd()):
                self._long_pending = True  # JG
                self._ld.trigger(Pushbutton.long_press_ms)
            if self._df:
                if self._dd():  # Second click: timer running
                    self._dd.stop()
                    self._dblpend = False
                    self._dblran = True  # Prevent suppressed launch on release
                    self._press_pending = False # JG
                    launch(self._df, self._da)
                else:
                    # First click: start doubleclick timer
                    self._dd.trigger(Pushbutton.double_click_ms)
                    self._dblpend = True  # Prevent suppressed launch on release
        else:  # Button release. Is there a release func?
            if self._ff:
                if self._supp:
                    d = self._ld
                    # If long delay exists, is running and doubleclick status is OK
                    if not self._dblpend and not self._dblran:
                        if (d and d()) or not d:
                            launch(self._ff, self._fa)
                else:
                    launch(self._ff, self._fa)
            if self._ld:
                self._ld.stop()  # Avoid interpreting a second click as a long push
                # JG Long press wasn't, because button released before timer went
                # JG If we started a press, and the timer goes, it was a long press!
                self._long_pending = False
                if self._tf and self._press_pending and not self._dblpend: # JG
                    self._press_pending = False # JG
                    # print("press from release") # JG
                    launch(self._tf, self._ta) # JG
                # JG end
            self._dblran = False

    def _ddto(self):  # Doubleclick timeout: no doubleclick occurred
        self._dblpend = False
        # JG If we had first press, and there's no second, it was a single press,
        # JG but only if we aren't also waiting for a long press
        if self._tf and self._press_pending and not self._long_pending: # JG
            self._press_pending = False # JG
            # print("press from ddto") # JG
            launch(self._tf, self._ta) # JG
        # JG end
        if self._ff and self._supp and not self._state:
            if not self._ld or (self._ld and not self._ld()):
                launch(self._ff, self._fa)
    
    # JG New function to enable indirection of the Delay_ms callback for _ld timeout
    # JG need to turn off the Press Pending flag!
    def _ldcb (self):
        self._press_pending = False
        self._long_pending = False
        launch(self._lf, self._la)
    

    # ****** API ******
    def press_func(self, func=False, args=()):
        if func is None:
            self.press = asyncio.Event()
        self._tf = self.press.set if func is None else func
        self._ta = args

    def release_func(self, func=False, args=()):
        if func is None:
            self.release = asyncio.Event()
        self._ff = self.release.set if func is None else func
        self._fa = args

    def double_func(self, func=False, args=()):
        if func is None:
            self.double = asyncio.Event()
            func = self.double.set
        self._df = func
        self._da = args
        if func:  # If double timer already in place, leave it
            if not self._dd:
                self._dd = Delay_ms(self._ddto)
        else:
            self._dd = False  # Clearing down double func

    def long_func(self, func=False, args=()):
        if func is None: # Caller wants to use Event
            self.long = asyncio.Event() # Create an Event...
            func = self.long.set # and make the action function Event.set()
        if func: # Function was provided, or is the Event.set()
            self._lf = func
            self._la = args
            if self._ld: # False at __init__, so True => we already have a _ld function (Delay_ms)
                # JG self._ld.callback(func, args) # Set the callback of the delay timeout to func
                self._ld.callback(self._ldcb) # JG
            else: # Otherwise set up the Delay with this function
                # JG self._ld = Delay_ms(func, args)
                self._ld = Delay_ms(self._ldcb) # JG
        else:
            self._ld = False

    # Current non-debounced logical button state: True == pressed
    def rawstate(self):
        return bool(self._pin() ^ self._sense)

    # Current debounced state of button (True == pressed)
    def __call__(self):
        return self._state

    def deinit(self):
        self._run.cancel()


class ESP32Touch(Pushbutton):
    thresh = (80 << 8) // 100

    @classmethod
    def threshold(cls, val):
        if not (isinstance(val, int) and 0 < val < 100):
            raise ValueError("Threshold must be in range 1-99")
        cls.thresh = (val << 8) // 100

    def __init__(self, pin, suppress=False):
        self._thresh = 0  # Detection threshold
        self._rawval = 0
        try:
            self._pad = TouchPad(pin)
        except ValueError:
            raise ValueError(pin)  # Let's have a bit of information :)
        super().__init__(pin, suppress, False)

    # Current logical button state: True == touched
    def rawstate(self):
        rv = self._pad.read()  # ~220μs
        if rv > self._rawval:  # Either initialisation or pad was touched
            self._rawval = rv  # when initialised and has now been released
            self._thresh = (rv * ESP32Touch.thresh) >> 8
            return False  # Untouched
        return rv < self._thresh
