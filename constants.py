# SINGLE_FILE = 'Original.txt'
SINGLE_FILE = 'Tests.txt'
# SINGLE_FILE = 'Large Test Suite Sets/Aymeric_Du_Peloux_282.xsb'
# SINGLE_FILE = 'Large Test Suite Sets/Grigr2001_100.xsb'
# SINGLE_FILE = 'haikemono/Haikemono collection.txt'
# SINGLE_FILE = 'pufiban/Pufiban.txt'
# SINGLE_FILE = 'microban.txt'


# Normally, no need to modify anything below

MAPWIDTH    = 25
MAPHEIGHT   = 15
SPRITESIZE  = 32
SPRITE_PLAYER_NUM = 3 # number of sprites in a player animation

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
PLAYER_ON_TARGET= 8
TARGETOVER      = 9 # just for the texture overlay

SYMBOLS_ORIGINALS = ['','#','$','.','*','@',' ','','+']
SYMBOLS_MODERN    = ['','X','*','.','&','@',' ','','+']



UP      = 0
DOWN    = 1
LEFT    = 2
RIGHT   = 3
NUMDIRS = 4


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
RED             = (150,0,0)
GREEN           = (0,150,0)

HOFF  = 0
HATT  = 1
HSUCC = 2
HSELECT = 3
HERROR  = 4


# Time delays
MOVE_DELAY  = 3  # milliseconds
SOLVE_DELAY = 100 # milliseconds
FLASH_DELAY = 100 # milliseconds

FRAMES_PER_ANIM = 3 # number of identical successif frames for animations
MOVE_FRAMES = 9 # number of frames for a move
TARGET_FPS  = 40 # number of frames for a move


# Player states
ST_IDLE = 0
ST_MOVING = 1
ST_PUSHING = 2 # moving and pushing a box
