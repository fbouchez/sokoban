#!/usr/bin/env python3
"""

 Yet another Sokoban clone

"""

import sys
import os
# Hide welcome message from pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from pygame.locals import *
import common as C
from utils import *
from game import Game
from interface import Menu
import time

def parse_options():
    for o in sys.argv:
        if o == "-v" or o == "--verbose":
            set_verbose()
        elif o == "--no-sound":
            C.WITH_SOUND = False




def general_menu(window):
    # Game menu
    menu = Menu(window)

    while True:
        # Check user inputs (mouse or keyboard)
        event = pygame.event.wait()
        if event.type == QUIT:
            # window was closed
            break

        elif event.type == KEYDOWN:
            # keyboard interactions
            if event.key == K_n:
                new_game(window)
            elif event.key == K_c:
                continue_game(window)
            elif event.key == K_p:
                choose_pack(window)
            elif event.key == K_ESCAPE or event.key == K_q:
                break

        elif event.type == MOUSEBUTTONDOWN:
            # mouse interactions
            if menu.click(event.pos):
                if menu.quit:
                    return
                elif menu.new_game:
                    new_game(window)
                elif menu.continue_game:
                    continue_game(window)
                else:
                    raise ValueError("Click problem on menu")
        elif event.type == VIDEORESIZE:
            w, h = event.dict['size']
            C.WINDOW_WIDTH = w
            C.WINDOW_HEIGHT = h
            window = pygame.display.set_mode(
                (C.WINDOW_WIDTH, C.WINDOW_HEIGHT),
                RESIZABLE)

        # else:
            # print('uncatched event:', event)

        # Redraws menu, as a game might have been played
        window.fill(C.WHITE)
        menu.render(window)
        pygame.display.flip()




def main():

    parse_options()
    verbose("Verbose mode activated") # will only print if option was set

    if C.WITH_SOUND:
        pygame.mixer.pre_init(44100, 16, 2, 4096) # setup mixer to avoid sound lag

    # Window creation
    pygame.init()

    # Key repetition to allow  fast cancels
    pygame.key.set_repeat(100, 60)
    pygame.display.set_caption("Sokoban Game")
    window = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT), RESIZABLE)

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
