from enum import Enum # only works n real Python

class State(Enum):
    ST_ILLEGAL = -1
    ST_WP = 0
    ST_WR = 1
    ST_WDP = 2
    ST_WDLR = 3
    ST_MAX = ST_WDLR+1
    