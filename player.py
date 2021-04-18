import pygame
from pygame.locals import *
import constants as S
from utils import *

class Player:
    def __init__(self, level):
        self.level = level
        self.direction = S.DOWN
        self.load_textures()
        self.frames=0
        self.status=S.ST_IDLE
        self.move_from=None

    def load_textures(self):
        sheet = pygame.image.load('assets/images/player_sprites.png').convert_alpha()
        self.textures = []
        for d in range(S.NUMDIRS):
            self.textures.append([])

        for yoffset, direction in enumerate([
            S.DOWN,
            S.LEFT,
            S.RIGHT,
            S.UP
            ]):
            for xoffset in range(S.SPRITE_PLAYER_NUM):
                self.textures[direction].append(
                        sheet.subsurface((
                            xoffset*S.SPRITESIZE,
                            yoffset*S.SPRITESIZE,
                            S.SPRITESIZE,
                            S.SPRITESIZE)))

    def start_move(self, direction):
        self.direction = direction
        self.continue_move()
        return self.status


    def continue_move(self):
        """
        Returns True if arriving fully on a tile,
        False if character is on the way between two tiles.
        """
        if self.frames == 0:
            # ask level if allowed to continue moving
            d = S.DIRS[self.direction]
            self.status = self.level.move_player(d)

            if self.status != S.ST_IDLE:
                self.move_from=S.DIRS[opposite(self.direction)]
                self.frames = S.MOVE_FRAMES
        else:
            self.frames -= 1

        return self.frames == 0


    def stop_move(self):
        self.status = S.ST_IDLE
        self.frames = 0




    def render(self, window, textures):
        x,y = self.level.player_position

        if self.frames == 0:
            xpos = x * S.SPRITESIZE
            ypos = y * S.SPRITESIZE
            frame = 0
        else:
            mx,my = self.move_from
            mx = mx * self.frames / S.MOVE_FRAMES
            my = my * self.frames / S.MOVE_FRAMES

            xpos = int((x+mx) * S.SPRITESIZE)
            ypos = int((y+my) * S.SPRITESIZE)

            frame = (self.frames // S.FRAMES_PER_ANIM) % S.SPRITE_PLAYER_NUM

        window.blit(self.textures[self.direction][frame], (xpos, ypos))
