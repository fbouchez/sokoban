"""
Generic graphic methods to display text messages.
"""

import pygame
import os
from pygame.locals import *
import common as C
from utils import *


class Text:
    """
    Class for a text displayed on screen.
    Set the message ("text"), the font to use, the color, and either
    - the position relative to current window, using xalign and yalign
    - the absolute position, using x and y
    - a mix of the above two (e.g., yalign at TOP, and absolute x)
    - the relative position, using below or above, refering to another Text
      object
    - a function to be called to compute y when resizing

    Also set the callback: function to be called if text is clicked.
    or 'retval': a value to return if text is clicked.
    """

    def __init__(self, text, font, color, xalign, yalign, x=0, y=0,
                 below=None, above=None, yfun=None, callback=None, retval=None):
        self.font = font
        self.color = color
        self.xalign = xalign
        self.yalign = yalign
        self.yfun = yfun
        self.below = below
        self.above = above
        self.callback = callback
        self.pos = (x, y)
        self.update(text)

    def change_color(self, color):
        self.color = color
        self.make_surface(self.text)

    def make_surface(self, text):
        self.surf = self.font.render(text, True, self.color, C.WHITE)

    def update(self, text=None):
        if text is not None:
            self.text = text
            self.make_surface(self.text)

        if self.xalign == C.ALEFT:
            xpos = C.BORDER
        elif self.xalign == C.ACENTER:
            xpos = C.WINDOW_WIDTH // 2 - self.surf.get_width() // 2
        elif self.xalign == C.ARIGHT:
            xpos = C.WINDOW_WIDTH - self.surf.get_width() - C.BORDER
        elif self.xalign == C.ACUSTOM:
            xpos = self.pos[0]
        else:
            raise ValueError("Horizontal alignment")

        if self.yalign == C.ATOP:
            ypos = C.BORDER
        elif self.yalign == C.AMID:
            ypos = C.WINDOW_HEIGHT // 2 - self.surf.get_height() // 2
        elif self.yalign == C.ABOTTOM:
            ypos = C.WINDOW_HEIGHT - self.surf.get_height() - C.BORDER
        elif self.yalign == C.ACUSTOM:
            self.set_pos(
                below=self.below,
                above=self.above,
                yfun=self.yfun)
            _, ypos = self.pos
        else:
            raise ValueError("Horizontal alignment" + str(self.yalign))

        self.pos = (xpos, ypos)

    def set_pos(self, x=None, y=None, below=None, above=None, yfun=None):
        if x is None:
            x = self.pos[0]
        if y is None:
            y = self.pos[1]
        if below is not None:
            y = below.pos[1] + below.surf.get_height()+C.BORDER
        elif above is not None:
            y = above.pos[1] - self.surf.get_height()-C.BORDER
        elif self.yfun is not None:
            y = self.yfun()

        self.pos = (x, y)

    def is_clicked(self, click, do_callback=True):
        cx, cy = click
        px, py = self.pos
        w = self.surf.get_width()
        h = self.surf.get_height()

        verbose(self.text, "clicked:", click,
                "and position:", self.pos, "with wh:", w, h)

        cl = px < cx and cx < px+w and \
            py < cy and cy < py+h

        if not cl:
            return False

        if do_callback and self.callback is not None:
            self.callback()
            return True

        if self.retval is not None:
            return self.retval

        return True

    def render(self, window, text=None):
        if text:
            self.update(text)
        window.blit(self.surf, self.pos)


class Paragraph(Text):
    """
    Similar to Text class, but handles multiline paragraphs passed as
    a list of lines.
    """

    def __init__(self, max_width, max_height, *args, **kwargs):
        self.max_width = max_width
        self.max_height = max_height
        self.surf = pygame.Surface((self.max_width, self.max_height))
        super().__init__(*args, **kwargs)

    def make_surface(self, text):
        self.surf.fill(C.WHITE)
        pos = (0, 0)
        # 2D array where each row is a list of words.
        words = [line.split(' ') for line in text]
        # The width and height of a space.
        space, line_height = self.font.size(' ')
        x, y = pos

        for line in words:
            for word in line:
                word_surface = self.font.render(
                    word, True, self.color, C.WHITE)
                word_width, _ = word_surface.get_size()
                if x + word_width >= self.max_width:
                    x = pos[0]  # Reset the x.
                    y += line_height  # Start on new row.
                    if y > self.max_height:
                        return
                self.surf.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += line_height  # Start on new row.
            if y > self.max_height:
                return


class Character:
    """
    Handles the sprites and moving of the character.
    """

    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.direction = C.DOWN
        self.load_textures()
        self.frames = 0
        self.status = C.ST_IDLE
        self.move_from = None
        self.sprite_idx = 0  # which sprite to use for animation
        self.anim_frame_num = 0

    def load_textures(self):
        ss = C.CHARACTER_SPRITESIZE
        sheet = self.game.textures.get(C.ORIG_SPRITESIZE)[C.PLAYER]
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
                self.move_to = C.DIRS[self.direction]
                self.move_from = C.DIRS[opposite(self.direction)]
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
        assert self.frames == 0

    def render(self, window):
        x, y = self.level.player_position

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
            mx, my = self.move_from
            mrx = mx * self.frames / C.MOVE_FRAMES
            mry = my * self.frames / C.MOVE_FRAMES

            xpos = int((x+mrx) * C.SPRITESIZE)
            ypos = int((y+mry) * C.SPRITESIZE)

            # draw the box in front of the character when pushing
            mbx, mby = self.move_to
            if self.status == C.ST_PUSHING:
                window.blit(self.game.textures.get(C.SPRITESIZE)[C.BOX],
                            (xpos+mbx*C.SPRITESIZE, ypos+mby*C.SPRITESIZE))

        # draw the character itself
        window.blit(self.textures[C.SPRITESIZE][self.direction][self.sprite_idx],
                    (xpos, ypos))


class Textures:
    """
    Sprites for the level and character
    """

    def __init__(self):
        """
        loads the textures that will be drawn in the game
        (walls, boxes, character, etc.)
        """
        def fn(f):
            return os.path.join('assets', 'images', f)

        ground = pygame.image.load(fn('stoneCenter.png')).convert_alpha()

        self.textures = {
            C.ORIG_SPRITESIZE: {
                C.WALL: pygame.image.load(fn('wall.png')).convert_alpha(),
                # C.BOX: pygame.image.load(fn('crate.png')).convert_alpha(),
                C.BOX: pygame.image.load(fn('box.png')).convert_alpha(),
                C.TARGET: ground,
                # target overlay
                C.TARGETOVER: pygame.image.load(fn('target.png')).convert_alpha(),
                # C.TARGET_FILLED: pygame.image.load(fn('crate_correct.png')).convert_alpha(),
                C.TARGET_FILLED: pygame.image.load(fn('box_correct.png')).convert_alpha(),
                C.PLAYER: pygame.image.load(fn('player_sprites.png')).convert_alpha(),
                # C.PLAYER: pygame.image.load(fn('character-female-knight.png')).convert_alpha(),
                C.GROUND: ground}}

        def surfhigh(size, color, alpha):
            surf = pygame.Surface((size, size))
            surf.set_alpha(alpha)
            surf.fill(color)  # green highlight
            return surf

        # small surfaces to draw attention to a particular tile of the board
        # e.g., to highlight a tile
        # green highlight, for attainable tiles
        def surfAtt(s): return surfhigh(s, (0, 255, 0), 50)
        # blue highlight,  to show successors of boxes
        def surfSucc(s): return surfhigh(s, (0, 0, 255), 50)
        # yellow highlight, to show selection
        def surfSelect(s): return surfhigh(s, (255, 255, 0), 200)
        # red highlight, in case of an error
        def surfError(s): return surfhigh(s, (255, 0, 0), 200)

        self.highlights = {}
        for s in C.SPRITESIZES:
            self.highlights[s] = {
                C.HATT:   surfAtt(s),
                C.HSUCC:  surfSucc(s),
                C.HSELECT: surfSelect(s),
                C.HERROR: surfError(s)
            }


    def get(self, size):
        return self.textures[size]


    def compute_sprite_size(self, level_height, level_width):
        """
        deciding which size of sprites to use based on the
        size of the level and the size of the window
        """
        # determine size of level on screen
        max_height = C.WINDOW_HEIGHT - 2*C.MAP_BORDER
        max_width = C.WINDOW_WIDTH - 2*C.MAP_BORDER

        max_sprite_size = min(
            max_height / level_height,
            max_width / level_width)

        minss = C.SPRITESIZES[0]
        maxss = C.SPRITESIZES[-1]

        if max_sprite_size < minss:
            sp = minss
        elif max_sprite_size > maxss:
            sp = maxss
        else:
            sp = minss
            for size in C.SPRITESIZES:
                if size > max_sprite_size:
                    break
                sp = size

        verbose('will use sprite size', sp)
        C.SPRITESIZE = sp



    def update_textures(self):
        """
        Create sprites of the current size by scaling.
        """
        if C.SPRITESIZE not in self.textures:
            sp = C.SPRITESIZE
            self.textures[sp] = {}
            for key, texture in self.textures[C.ORIG_SPRITESIZE].items():
                sc = pygame.transform.smoothscale(texture, (sp, sp))
                self.textures[sp][key] = sc




