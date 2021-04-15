import pygame
from pygame.locals import *
import constants as SOKOBAN

class Player:
    def __init__(self, level):
        self.level = level
        self.direction = SOKOBAN.DOWN

    def move(self, direction):
        self.direction = direction
        d = SOKOBAN.DIRS[self.direction]
        changed = self.level.move_player(d)

        return changed


    def render(self, window, textures):
        if self.direction == SOKOBAN.DOWN:
            top = 0
        elif self.direction == SOKOBAN.LEFT:
            top = SOKOBAN.SPRITESIZE
        elif self.direction == SOKOBAN.RIGHT:
            top = SOKOBAN.SPRITESIZE * 2
        elif self.direction == SOKOBAN.UP:
            top = SOKOBAN.SPRITESIZE * 3

        x,y = self.level.player_position

        areaPlayer = pygame.Rect((0, top), (32, 32))
        window.blit(textures[SOKOBAN.PLAYER], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE), area=areaPlayer)
