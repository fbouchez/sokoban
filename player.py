import pygame
from pygame.locals import *
import constants as SOKOBAN

class Player:
    def __init__(self, level):
        self.level = level
        self.direction = SOKOBAN.DOWN

    def move(self, direction):
        if direction == K_LEFT or direction == K_q:
            self.direction = SOKOBAN.LEFT
            move_x = -1
            move_y = 0
        elif direction == K_RIGHT or direction == K_d:
            self.direction = SOKOBAN.RIGHT
            move_x = 1
            move_y = 0
        elif direction == K_UP or direction == K_z:
            self.direction = SOKOBAN.UP
            move_x = 0
            move_y = -1
        elif direction == K_DOWN or direction == K_s:
            self.direction = SOKOBAN.DOWN
            move_x = 0
            move_y = 1
        else:
            raise ValueError("Unknown direction", direction)

        changed = self.level.movePlayer((move_x, move_y))

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

        x,y = self.level.position_player

        areaPlayer = pygame.Rect((0, top), (32, 32))
        window.blit(textures[SOKOBAN.PLAYER], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE), area=areaPlayer)
