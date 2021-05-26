"""
Common definitions for the whole project.
"""


# List of level packs available for in-game selection
PACKS = [
      'Original.txt'
    , 'Minicosmos.txt'
    , 'Simple Sokoban.txt'
    , 'Tests.txt'

    , 'Original_remixed.txt'
    , 'XSokoban.txt'
    , 'Pufiban.txt'
    , 'microban.txt'
    , 'Haikemono collection.txt'
    , 'Large Test Suite Sets/Aymeric_Du_Peloux_282.xsb'
    , 'Large Test Suite Sets/Grigr2001_100.xsb'
]

# Normally, no need to modify anything below

ORIG_SPRITESIZE  = 32
SPRITESIZE       = 32
CHARACTER_SPRITESIZE = 32
# CHARACTER_SPRITESIZE = 75
# CHARACTER_YSTART = 230  # pixels above this rows are for whole head
CHARACTER_YSTART = 0  # pixels above this rows are for whole head
SPRITE_PLAYER_NUM = 3   # number of sprites in a player animation

SPRITESIZES  = [16,20,24,28,32,36,40,44,48,52,56,60,64] #,75]

WINDOW_WIDTH  = 1024
WINDOW_HEIGHT = 768

BORDER = 10 # blank space around the main window

MAP_BORDER = 80 # blank space around the level map



# sound parameters
WITH_SOUND = True
SND_FOOTSTEP_NUM = 10
SND_WOODFRIC_NUM = 5


# Text alignment
# vertical
ATOP    = 0
AMID    = 1
ABOTTOM = 2
# horizontal
ALEFT   = 3
ACENTER = 4
ARIGHT  = 5
# horizontal or vertical
ACUSTOM = 6



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

# Highlights
HOFF  = 0
HATT  = 1
HSUCC = 2
HSELECT = 3
HERROR  = 4


# Time delays
MOVE_DELAY  = 3  # milliseconds
SOLVE_DELAY = 100 # milliseconds
FLASH_DELAY = 100 # milliseconds


# number of identical successive frames for animations
FRAMES_PER_ANIM = 6

# number of frames for a move: less makes character move faster but not enough
# makes movement 'jerky'
# better to make it a fraction of SPRITESIZE
MOVE_FRAMES = 8
# MOVE_FRAMES = 1


# number of frames for a move: more makes character move faster but consumes 
# more CPU
TARGET_FPS  = 40


# Character states
ST_IDLE = 0
ST_MOVING = 1
ST_PUSHING = 2 # moving and pushing a box
