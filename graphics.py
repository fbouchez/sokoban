"""
Generic graphic methods to display text messages.
"""

import pygame
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

    def __init__(self,text,font,color,xalign,yalign,x=0,y=0,below=None,above=None,yfun=None,callback=None,retval=None):
        self.font  = font
        self.color = color
        self.xalign = xalign
        self.yalign = yalign
        self.yfun = yfun
        self.below = below
        self.above = above
        self.callback = callback
        self.pos  = (x,y)
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
            xpos= C.WINDOW_WIDTH // 2 - self.surf.get_width() // 2
        elif self.xalign == C.ARIGHT:
            xpos= C.WINDOW_WIDTH - self.surf.get_width() - C.BORDER
        elif self.xalign == C.ACUSTOM:
            xpos=self.pos[0]
        else:
            raise ValueError("Horizontal alignment")

        if self.yalign == C.ATOP:
            ypos = C.BORDER
        elif self.yalign == C.AMID:
            ypos= C.WINDOW_HEIGHT // 2 - self.surf.get_height() // 2
        elif self.yalign == C.ABOTTOM:
            ypos= C.WINDOW_HEIGHT - self.surf.get_height() - C.BORDER
        elif self.yalign == C.ACUSTOM:
            self.set_pos(
                    below=self.below,
                    above=self.above,
                    yfun=self.yfun)
            _,ypos = self.pos
        else:
            raise ValueError("Horizontal alignment" + str(self.yalign))

        self.pos= (xpos,ypos)

    def set_pos (self, x=None,y=None,below=None,above=None,yfun=None):
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

        self.pos = (x,y)

    def is_clicked(self,click, do_callback=True):
        cx,cy = click
        px,py = self.pos
        w=self.surf.get_width()
        h=self.surf.get_height()

        verbose (self.text, "clicked:", click, "and position:", self.pos, "with wh:", w,h)

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
        words = [line.split(' ') for line in text]  # 2D array where each row is a list of words.
        space, line_height = self.font.size(' ')  # The width and height of a space.
        x, y = pos

        for line in words:
            for word in line:
                word_surface = self.font.render(word, True, self.color, C.WHITE)
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



