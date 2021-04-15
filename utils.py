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
