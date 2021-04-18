#!/usr/bin/env python3
#
# Yet another Sokoban clone
#

import sys
import os
# Hide welcome message from pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from pygame.locals import *
import constants as SOKOBAN
from utils import *
from game import Game
from interface import Menu
import time

def parse_options():
    for o in sys.argv:
        if o == "-v" or o == "--verbose":
            set_verbose()


def new_game(window):
    sokoban = Game(window, continueGame = False)
    sokoban.start()

def continue_game(window):
    sokoban = Game(window, continueGame = True)
    sokoban.start()


def main():

    parse_options()
    verbose("Verbose mode activated") # will only print if option was set

    # Window creation
    pygame.init()
    # now continuing is handled via keyup instead of repetition
    # pygame.key.set_repeat(100, 100)
    pygame.display.set_caption("Sokoban Game")
    window = pygame.display.set_mode((SOKOBAN.WINDOW_WIDTH, SOKOBAN.WINDOW_HEIGHT))

    # Game menu
    menu = Menu()

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
            elif event.key == K_ESCAPE or event.key == K_q:
                break

        elif event.type == MOUSEBUTTONDOWN:
            # mouse interactions
            if menu.click(event.pos):
                if menu.new_game:
                    new_game(window)
                elif menu.continue_game:
                    continue_game(window)
                elif menu.quit:
                    break
                else:
                    raise ValueError("Click problem on menu")

        # Redraws menu, as a game might have been played
        window.fill(SOKOBAN.WHITE)
        menu.render(window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
