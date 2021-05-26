#!/usr/bin/env python3
"""

 Yet another Sokoban clone

"""

import scores
from interface import Menu
from game import Game
from utils import *
import common as C
from pygame.locals import *
import pygame
import time
import sys
import os
# Hide welcome message from pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


def display_help():
    print("Usage: ./Sokoban.py [-h] [-v] [--no-sound]")
    print("List of options:")
    print("    --help")
    print("    -h  display this help message")
    print("    --verbose")
    print("    -v  verbose mode")
    print("    --no-sound")
    print("        disable sound effects")


def parse_options():
    for o in sys.argv:
        if o == "-v" or o == "--verbose":
            set_verbose()
        elif o == "--no-sound":
            C.WITH_SOUND = False
        elif o == "-h" or o == "--help":
            display_help()
            exit(0)


def main():

    parse_options()
    verbose("Verbose mode activated")  # will only print if option was set

    # read scores and current pack / last level information
    scores.load_scores()

    # Window creation
    pygame.init()

    # Key repetition to allow  fast cancels
    pygame.key.set_repeat(400, 60)
    pygame.display.set_caption("Sokoban Game")
    window = pygame.display.set_mode(
        (C.WINDOW_WIDTH, C.WINDOW_HEIGHT), RESIZABLE)

    menu = Menu(window)
    pygame.quit()


# a function to ease enter into debug mode using C-c "a la gdb"
def debug_signal_handler(signal, frame):
    import pdb
    pdb.set_trace()


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, debug_signal_handler)
    main()
