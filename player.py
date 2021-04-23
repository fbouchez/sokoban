import pygame
from pygame.locals import *
import constants as S
from utils import *

class Player:
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.direction = S.DOWN
        self.load_textures()
        self.frames=0
        self.status=S.ST_IDLE
        self.move_from=None
        self.sprite_idx=0 # which sprite to use for animation
        self.anim_frame_num=0

    def load_textures(self):
        sheet = self.game.textures[S.ORIG_SPRITESIZE][S.PLAYER]
        st = []
        self.textures = {S.ORIG_SPRITESIZE: st}
        for d in range(S.NUMDIRS):
            st.append([])

        for yoffset, direction in enumerate([
            S.DOWN,
            S.LEFT,
            S.RIGHT,
            S.UP
            ]):
            for xoffset in range(S.SPRITE_PLAYER_NUM):
                st[direction].append(
                        sheet.subsurface((
                            xoffset*S.ORIG_SPRITESIZE,
                            yoffset*S.ORIG_SPRITESIZE,
                            S.ORIG_SPRITESIZE,
                            S.ORIG_SPRITESIZE)))


    def update_textures(self):
        if SOKOBAN.SPRITESIZE not in self.textures:
            sp = SOKOBAN.SPRITESIZE
            self.textures[sp] = []
            for direct in self.textures[SOKOBAN.ORIG_SPRITESIZE]:
                l = []
                self.textures[sp].append(l)
                for texture in direct:
                    sc = pygame.transform.scale(texture, (sp, sp))
                    l.append(sc)



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
                self.move_to=S.DIRS[self.direction]
                self.move_from=S.DIRS[opposite(self.direction)]
                self.frames = S.MOVE_FRAMES

                if self.status == S.ST_PUSHING:
                    # for better visual effect
                    self.level.hide_pushed_box()

        else:
            self.frames -= 1

        if self.frames == 0 and self.status == S.ST_PUSHING:
            # arrived at tile, put back box in matrix of boxes
            self.level.show_pushed_box()

        return self.frames == 0


    def stop_move(self):
        self.status = S.ST_IDLE
        assert(self.frames == 0)




    def render(self, window, textures):
        x,y = self.level.player_position

        self.anim_frame_num += 1
        if self.anim_frame_num >= S.FRAMES_PER_ANIM:
            self.anim_frame_num = 0
            self.sprite_idx += 1
            self.sprite_idx %= S.SPRITE_PLAYER_NUM

        if self.frames == 0:
            xpos = x * S.SPRITESIZE
            ypos = y * S.SPRITESIZE
            frame = 0
        else:
            mx,my = self.move_from
            mrx = mx * self.frames / S.MOVE_FRAMES
            mry = my * self.frames / S.MOVE_FRAMES

            xpos = int((x+mrx) * S.SPRITESIZE)
            ypos = int((y+mry) * S.SPRITESIZE)

            # draw the box in front of the character
            mbx,mby = self.move_to


            if self.status == S.ST_PUSHING:
                window.blit(self.game.textures[S.SPRITESIZE][S.BOX], 
                        (xpos+mbx*S.SPRITESIZE, ypos+mby*S.SPRITESIZE))

        window.blit(self.textures[S.SPRITESIZE][self.direction][self.sprite_idx], (xpos, ypos))

