import constants as SOKOBAN

# debug functions
VERBOSE=False

verbose= lambda *a, **k: None

def set_verbose(flag=True):
    global VERBOSE
    VERBOSE = flag

def verbose(*a,**k):
    if VERBOSE:
        print (*a,*k)



# tuple and list conversions
def listit(t):
    return list(map(listit, t)) if isinstance(t, (list, tuple)) else t

def tupleit(t):
    return tuple(map(tupleit, t)) if isinstance(t, (list, tuple)) else t


# direction helpers
def opposite(d):
    return SOKOBAN.OPPOSITE[d]

def in_dir(pos, d):
    mx,my = SOKOBAN.DIRS[d]
    x,y=pos
    return x+mx,y+my

def in_opp_dir(pos, d):
    return in_dir(pos, opposite(d))

def horizontal(d):
    return d == SOKOBAN.LEFT or d == SOKOBAN.RIGHT


# check if element is last of an iterator
def islast(o):
    it = o.__iter__()
    e = it.__next__()
    while True:
        try:
            nxt = it.__next__()
            yield (False, e)
            e = nxt
        except StopIteration:
            yield (True, e)
            break
