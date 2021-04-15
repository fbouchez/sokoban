# SINGLE_FILE = 'Original'
SINGLE_FILE = 'Tests'


# Normally, no need to modify anything below

MAPWIDTH    = 25
MAPHEIGHT   = 15
SPRITESIZE  = 32

WINDOW_WIDTH  = 1024
WINDOW_HEIGHT = 768

# Text alignment
#vertical
ATOP =0
AMID =1
ABOTTOM=2
#horizontal
ALEFT=3
ACENTER=4
ARIGHT=5
ACUSTOM=6



# Blocks
NONE            = 0
WALL            = 1
BOX             = 2
TARGET          = 3
TARGET_FILLED   = 4
PLAYER          = 5
AIR             = 6
GROUND          = 7
TARGETOVER      = 8 # just for the texture overlay

SYMBOLS_ORIGINALS = ['','#','$','.','*','@',' ','']
SYMBOLS_MODERN    = ['','X','*','.','&','@',' ','']



UP      = 0
DOWN    = 1
LEFT    = 2
RIGHT   = 3


OPPOSITE = [DOWN,UP,RIGHT,LEFT] # opposite directions

AROUND = [UP,RIGHT,DOWN,LEFT,UP] # clock-wise directions

DIRS = [(0, -1),  # up
        (0, 1),   # down
        (-1, 0),  # left
        (1, 0),   # right
       ]

DNAMES = ["up","down","left","right"]

# Colors
WHITE           = (255,255,255)
BLACK           = (0,0,0)
BLUE            = (0,0,150)
GREY            = (200,200,200)

HOFF  = 0
HATT  = 1
HSUCC = 2
HSELECT = 3
HERROR  = 4


# Time delays
MOVE_DELAY = 3 # milliseconds
FLASH_DELAY = 100 # milliseconds


