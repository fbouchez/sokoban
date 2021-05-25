import pygame
from pygame.locals import *
import common as C
from utils import *

class Player:
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.direction = C.DOWN
        self.load_textures()
        self.frames=0
        self.status=C.ST_IDLE
        self.move_from=None
        self.sprite_idx=0 # which sprite to use for animation
        self.anim_frame_num=0

    def load_textures(self):
        ss = C.CHARACTER_SPRITESIZE
        sheet = self.game.textures[C.ORIG_SPRITESIZE][C.PLAYER]
        st = []
        self.textures = {C.ORIG_SPRITESIZE: st}
        for d in range(C.NUMDIRS):
            st.append([])

        for yoffset, direction in enumerate([
            C.DOWN,
            C.LEFT,
            C.RIGHT,
            C.UP
            ]):
            for xoffset in range(C.SPRITE_PLAYER_NUM):
                st[direction].append(
                        sheet.subsurface((
                            xoffset*ss,
                            yoffset*ss+C.CHARACTER_YSTART,
                            ss,
                            ss)))


    def update_textures(self):
        if C.SPRITESIZE not in self.textures:
            sp = C.SPRITESIZE
            self.textures[sp] = []
            for direct in self.textures[C.ORIG_SPRITESIZE]:
                l = []
                self.textures[sp].append(l)
                for texture in direct:
                    sc = pygame.transform.smoothscale(texture, (sp, sp))
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
            d = C.DIRS[self.direction]
            self.status = self.level.move_player(d)

            if self.status != C.ST_IDLE:
                self.move_to=C.DIRS[self.direction]
                self.move_from=C.DIRS[opposite(self.direction)]
                self.frames = C.MOVE_FRAMES

                if self.status == C.ST_PUSHING:
                    # for better visual effect
                    self.level.hide_pushed_box()

        else:
            self.frames -= 1

        if self.frames == 0 and self.status == C.ST_PUSHING:
            # arrived at tile, put back box in matrix of boxes
            self.level.show_pushed_box()

        return self.frames == 0


    def stop_move(self):
        self.status = C.ST_IDLE
        assert(self.frames == 0)




    def render(self, window, textures):
        x,y = self.level.player_position

        self.anim_frame_num += 1
        if self.anim_frame_num >= C.FRAMES_PER_ANIM:
            self.anim_frame_num = 0
            self.sprite_idx += 1
            self.sprite_idx %= C.SPRITE_PLAYER_NUM

        if self.frames == 0:
            xpos = x * C.SPRITESIZE
            ypos = y * C.SPRITESIZE
            frame = 0
        else:
            mx,my = self.move_from
            mrx = mx * self.frames / C.MOVE_FRAMES
            mry = my * self.frames / C.MOVE_FRAMES

            xpos = int((x+mrx) * C.SPRITESIZE)
            ypos = int((y+mry) * C.SPRITESIZE)

            # draw the box in front of the character
            mbx,mby = self.move_to


            if self.status == C.ST_PUSHING:
                window.blit(self.game.textures[C.SPRITESIZE][C.BOX], 
                        (xpos+mbx*C.SPRITESIZE, ypos+mby*C.SPRITESIZE))

        window.blit(self.textures[C.SPRITESIZE][self.direction][self.sprite_idx], (xpos, ypos))

