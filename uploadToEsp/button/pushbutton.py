"""
    Simple implementation of the GoF Design Pattern State
"""

import asyncio
    
from . import launch, Delay_ms

class Pushbutton:
    debounce_ms = 50
    long_press_ms = 700
    double_click_ms = 300

    _stateobj = None

    #Events
    EV_F2T = 0
    EV_T2F = 1
    EV_DT = 2
    EV_LT = 3

    def __init__(self, pin, sense=None):
        self._pin = pin  # Initialise for input
        self._stateobj = Pushbutton.WP
        self._pf = False # Press function (Event.set or other)
        self._df = False # Double function (Event.set or other)
        self._lf = False # Long function (Event.set or other)
        self._rf = False # Release function (Event.set or other)
        # _pa, _ra, _da, _la args set when user requests 
        self._lt = Delay_ms(self.LTOut)  # Delay_ms instance for long press
        self._dt = Delay_ms(self.DTOut)  # Ditto for doubleclick
        # Convert from electrical to logical value
        self._sense = pin.value() if sense is None else sense
        self._state = self.rawstate()  # Initial state
        #print("init state: %s sense: %s"%(self._state,bool(self._sense)))
        self._run = asyncio.create_task(self._go())  # Thread runs forever

    def startLT(self):
        self._lt.trigger(self.long_press_ms)
        
    def startDT(self):
        self._dt.trigger(self.double_click_ms)
        
    def LTOut(self):
        self._stateobj= self._stateobj.handleEvent(self, self.EV_LT)

    def DTOut(self):
        self._stateobj= self._stateobj.handleEvent(self, self.EV_DT)
        
    def killDT(self):
        self._dt.stop()
    
    def killLT(self):
        self._lt.stop()
    
    def emitP(self):
        if self._pf:
            launch(self._pf, self._pa)
        
    def emitD(self):
        if self._df:
            launch(self._df, self._da)
    
    def emitL(self):
        if self._lf:
            launch(self._lf, self._la)
        
    def emitR(self):
        if self._rf:
            #print("emitR")
            launch(self._rf, self._ra)

    async def _go(self):
        while True:
            self._check(self.rawstate())
            # Ignore state changes until switch has settled. Also avoid hogging CPU.
            # See https://github.com/peterhinch/micropython-async/issues/69
            await asyncio.sleep_ms(Pushbutton.debounce_ms)

    def _check(self, state):
        if state == self._state:
            return
        # Pushbutton state has changed: act on it now.
        self._state = state
        # Determine which transition
        if state: # Press
            evt = self.EV_F2T
        else: # Release
            evt = self.EV_T2F
        self._stateobj= self._stateobj.handleEvent(self, evt)

    # ****** API ******
    def press_func(self, func=False, args=()):
        if func is None:
            self.press = asyncio.Event()
        self._pf = self.press.set if func is None else func
        self._pa = args

    def release_func(self, func=False, args=()):
        if func is None:
            self.release = asyncio.Event()
        self._rf = self.release.set if func is None else func
        self._ra = args

    def double_func(self, func=False, args=()):
        if func is None:
            self.double = asyncio.Event()
        self._df = self.double.set if func is None else func
        self._da = args

    def long_func(self, func=False, args=()):
        if func is None:
            self.long = asyncio.Event()
        self._lf = self.long.set if func is None else func
        self._la = args

    # Current non-debounced logical button state: True == pressed
    def rawstate(self):
        return bool(self._pin() ^ self._sense)

    # Current debounced state of button (True == pressed)
    def __call__(self):
        return self._state

    def deinit(self):
        self._run.cancel()

    class WP():
        def handleEvent(self, event):
            if event == self.EV_F2T:
                self.startLT()
                return self.WR
            else:
                raise Exception("illegal event")

    class WR():
        def handleEvent(self, event):
            if event == self.EV_T2F:
                self.killLT()
                self.emitR()
                self.startDT()
                return self.WDP
            elif event == self.EV_LT:
                self.emitL()
                return self.WDLR
            else:
                raise Exception("illegal event")

    class WDP():
        def handleEvent(self, event):
            if event == self.EV_F2T:
                self.killDT()
                self.emitD()
                return self.WDLR
            elif event == self.EV_DT:
                self.emitP()
                return self.WP

    class WDLR():
        def handleEvent(self, event):
            if event == self.EV_T2F:
                self.emitR()
                return self.WP
            else:
                raise Exception("illegal event")