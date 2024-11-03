"""
    Script to detect the various operations on a Pushbutton using a FSM
    to represent the ongoing state of the button, and raise events appropriately.
    Currently doesn't do Release, only Press, Double and Long
    
    Derived from the work of Peter Hinch - pushbutton.py 
    
# pushbutton.py

# Copyright (c) 2018-2023 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

    FSM States:
    
    ST_WP	Waiting for a first press
    ST_WR	Waiting for release after first press
    ST_WDP	Waiting for second press of a Double
    ST_WDLR	Waiting for Long release or a Double release
    
    Events:
    F2T	False to True = Press
    T2F	True to False = Release
    DT	Double press wait timer expires
    LT	Long press wait timer expires
    
    State-Event Table s - next state; x - action
    State	WP			WR					WDP				WDLR
    Event
    F2T		x:startLT	--					x:killDT;emitD	--
            s:WR		--					s:WDLR			--

    T2F		--			x:killLT;startDT	--				x:
            --			s:WDP				--				s:WP

    DTimer	--			--					x:emitP			--
            --			--					s:WP			--
            
    LTimer	--			x:emitL				--				--
            --			s:WDLR				--				--
"""

import asyncio
import time
try:
    from micropython import const
    print("micropython const imported")
except ImportError:
    print("micropython const not imported - substitute")
    def const(item):
        return item
    
from . import launch, Delay_ms

class FSMButton:
    debounce_ms = 50
    long_press_ms = 700
    double_click_ms = 300
    
    # States
    ST_ILLEGAL = -1
    ST_WP = 0
    ST_WR = 1
    ST_WDP = 2
    ST_WDLR = 3
    ST_MAX = ST_WDLR+1
    
    stStr = [const("ST_ILLEGAL"),
             const("ST_WP"),
             const("ST_WR"),
             const("ST_WDP"),
             const("ST_WDLR"),
             ]
    
    #Events
    EV_F2T = 0
    EV_T2F = 1
    EV_DT = 2
    EV_LT = 3
    
    evStr = [const("EV_F2T"),
             const("EV_T2F"),
             const("EV_DT"),
             const("EV_LT"),
             ]
    
    def startLT(self):
        """Called to start the Long press timer"""
        #print("startLT")
        self._lt.trigger(self.long_press_ms)
        
    def startDT(self):
        """Called to start the Double press timer"""
        #print("startDT")
        self._dt.trigger(self.double_click_ms)
        
    def LTOut(self):
        """Called on Long press timer expired"""
        #print("LTOut")
        self.executeFSM(self.EV_LT)

    def DTOut(self):
        """Called on Double press timer expired"""
        #print("DTOut")
        self.executeFSM(self.EV_DT)
        
    def killDT(self):
        #print("killDT")
        self._dt.stop()
    
    def killLT(self):
        #print("killLT")
        self._lt.stop()
    
    def emitP(self):
        """Called when we find a Press happened"""
        if self._pf:
            #print("emitP")
            launch(self._pf, self._pa)
        
    def emitD(self):
        """Called when we find a Double happened"""
        if self._df:
            #print("emitD")
            launch(self._df, self._da)
    
    def emitL(self):
        """Called when we find a Long happened"""
        if self._lf:
            #print("emitL")
            launch(self._lf, self._la)
        
    def emitR(self):
        """Called when we find a Release happened"""
        if self._rf:
            #print("emitR")
            launch(self._rf, self._ra)
        
    # Format is (nextState, action, action... )
    #        WP				WR								WDP						WDLR
    FSM = [
        (ST_WR,startLT),(ST_ILLEGAL,), 					(ST_WDLR,killDT,emitD), (ST_ILLEGAL,),	# F2T
        (ST_ILLEGAL,), 	(ST_WDP,killLT,emitR,startDT),	(ST_ILLEGAL,), 			(ST_WP,emitR),	# T2F
        (ST_ILLEGAL,), 	(ST_ILLEGAL,), 					(ST_WP,emitP), 			(ST_ILLEGAL,),	# DT
        (ST_ILLEGAL,), 	(ST_WDLR,emitL), 				(ST_ILLEGAL,), 			(ST_ILLEGAL,)	# LT
        ]

    def __init__(self, pin, sense=None):
        self._pin = pin  # Initialise for input
        self._fsmState = self.ST_WP
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

    async def _go(self):
        while True:
            self._check(self.rawstate())
            # Ignore state changes until switch has settled. Also avoid hogging CPU.
            # See https://github.com/peterhinch/micropython-async/issues/69
            await asyncio.sleep_ms(FSMButton.debounce_ms)

    def executeFSM(self, evt):
        """Called when an event has been identified"""
        #print("exFSM: current: %s evt: %s"%(self.stStr[self._fsmState+1], self.evStr[evt]))
        tblEntry = self.FSM[(self.ST_MAX * evt) + self._fsmState]
        #print("exFSM: tblEntry: %s # %d" % (tblEntry, (self.ST_MAX * evt)+self._fsmState))
        for x in tblEntry[1:len(tblEntry)]:
            x(self)
        # Only change state if event valid for state
        if tblEntry[0] > -1:
            self._fsmState = tblEntry[0]
        else:
            print("Unexpected event %d in state %d!"%(evt, self._fsmState))      

    def _check(self, state):
        if state == self._state:
            return
        #print("_check: transition: was: %s now: %s"%(self._state, state))
        # State has changed: act on it now.
        self._state = state
        # Determine which transition
        if state: # Press
            #print("F2T")
            evt = self.EV_F2T
        else: # Release
            #print("T2F")
            evt = self.EV_T2F
        self.executeFSM(evt)

    # ****** API ******
    def press_func(self, func=False, args=()):
        if func is None:
            self.press = asyncio.Event()
        self._pf = self.press.set if func is None else func
        self._pa = args
        #print("FSM: press_func:",self._pf, self._pa) 

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