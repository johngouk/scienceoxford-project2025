from micropython import const
import gc
def mem():
    gc.collect()
    return gc.mem_free()
start = mem()

class test:
    
    # States
    ST_ILLEGAL = -1
    ST_WP = 0
    ST_WR = 1
    ST_WDP = 2
    ST_WDLR = 3
    ST_MAX = ST_WDLR+1
    """
    stStr = [const("ST_ILLEGAL"),
             const("ST_WP"),
             const("ST_WR"),
             const("ST_WDP"),
             const("ST_WDLR"),
             ]
    """
    #Events
    EV_F2T = 0
    EV_T2F = 1
    EV_DT = 2
    EV_LT = 3
    """
    evStr = [const("EV_F2T"),
             const("EV_T2F"),
             const("EV_DT"),
             const("EV_LT"),
             ]
    """
    def emitR(self):
        pass
    """
    FSM = [
        (ST_WR,emitR),(ST_ILLEGAL,), 					(ST_WDLR,emitR,emitR), (ST_ILLEGAL,),	# F2T
        (ST_ILLEGAL,), 	(ST_WDP,emitR,emitR,emitR),	(ST_ILLEGAL,), 			(ST_WP,emitR),	# T2F
        (ST_ILLEGAL,), 	(ST_ILLEGAL,), 					(ST_WP,emitR), 			(ST_ILLEGAL,),	# DT
        (ST_ILLEGAL,), 	(ST_WDLR,emitR), 				(ST_ILLEGAL,), 			(ST_ILLEGAL,)	# LT
        ]
    """
begin = mem()
t = test()
done = mem()
print("define:",start - begin)
print("init:",start - done)
