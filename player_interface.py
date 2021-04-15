import pygame
import constants as SOKOBAN

BORDER = 10

class Text:
    def __init__(self,text,font,color,xalign,yalign,callback=None):
        self.font  = font
        self.color = color
        self.xalign = xalign
        self.yalign = yalign
        self.callback = callback
        self.pos  = (0,0)
        self.surf = None
        self.update(text)

    def change_color(self, color):
        self.color = color
        self.update()

    def update(self, text=None):
        if text:
            self.text = text
        self.surf= self.font.render(self.text, True, self.color, SOKOBAN.WHITE)

        if self.xalign == SOKOBAN.ALEFT:
            xpos = BORDER
        elif self.xalign == SOKOBAN.ACENTER:
            xpos= SOKOBAN.WINDOW_WIDTH // 2 - self.surf.get_width() // 2
        elif self.xalign == SOKOBAN.ARIGHT:
            xpos= SOKOBAN.WINDOW_WIDTH - self.surf.get_width() - BORDER
        elif self.xalign == SOKOBAN.ACUSTOM:
            xpos=self.pos[0]
        else:
            raise ValueError("Horizontal alignment")

        if self.yalign == SOKOBAN.ATOP:
            ypos = BORDER
        elif self.yalign == SOKOBAN.AMID:
            ypos= SOKOBAN.WINDOW_HEIGHT // 2 - self.surf.get_height() // 2
        elif self.yalign == SOKOBAN.ABOTTOM:
            ypos= SOKOBAN.WINDOW_HEIGHT - self.surf.get_height() - BORDER
        elif self.yalign == SOKOBAN.ACUSTOM:
            ypos=self.pos[1]
        else:
            raise ValueError("Horizontal alignment")

        self.pos= (xpos,ypos)

    def set_pos (self, x=None,y=None):
        if x is None:
            x = self.pos[0]
        if y is None:
            y = self.pos[1]
        self.pos = (x,y)

    def is_clicked(self,click, do_callback=True):
        cx,cy = click
        px,py = self.pos
        w=self.surf.get_width()
        h=self.surf.get_height()

        cl = px < cx and cx < px+w and \
             py < cy and cy < py+h

        if cl and do_callback and self.callback is not None:
            self.callback()
        return cl


    def render(self, window, text=None):
        if text:
            self.update(text)
        window.blit(self.surf, self.pos)


class PlayerInterface:
    def __init__(self, game, player, level):
        self.game = game
        self.player = player
        self.level = level
        self.mouse_pos = (-1,-1)
        self.font_menu = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 18)
        self.font_win  = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 32)

        self.load_texts()

    def load_texts(self):

        self.txtLevel = Text("Niveau 1",
                self.font_menu, SOKOBAN.BLUE, SOKOBAN.ALEFT, SOKOBAN.ATOP,
                callback=None)

        self.txtCancel = Text("Annuler le dernier coup (C)",
                self.font_menu, SOKOBAN.GREY, SOKOBAN.ARIGHT, SOKOBAN.ATOP,
                callback=self.cancel)

        self.txtReset = Text("Recommencer le niveau (R)",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ATOP,
                callback=self.game.load_level)

        self.txtVisu = Text("Aide visuelle (V)",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ALEFT, SOKOBAN.ABOTTOM,
                callback=self.game.toggle_visualize)

        self.txtHelp = Text("Aide sokoban (H)",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ABOTTOM,
                callback=None)

        self.txtMoves = Text("Coups : 0",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ARIGHT, SOKOBAN.ABOTTOM,
                callback=None)


        self.txtWin = Text ("Félicitations, niveau 1 terminé",
                self.font_win, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                callback=None)
        self.txtWin.set_pos(y=80)

        self.txtPress = Text ("(appuyez sur une touche pour continuer)",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                callback=None)

        y  = self.txtWin.pos[1]
        y += self.txtWin.surf.get_height()+40
        self.txtPress.set_pos(y=y)

        self.texts = [
                self.txtLevel,
                self.txtCancel,
                self.txtReset,
                self.txtVisu,
                self.txtHelp,
                self.txtMoves,
                self.txtPress
                ]


    def cancel(self):
        ret = self.level.cancel_last_change()
        if not ret:
            self.txtCancel.change_color(SOKOBAN.GREY)

    def click(self, pos_click, level):
        # check if some text has been clicked
        for t in self.texts:
            if t.is_clicked(pos_click, do_callback=True):
                return None

        x,y=pos_click
        # check if clicked in the game
        origx, origy = self.game.origin_board
        if x > origx and x < origx + self.game.board.get_width() \
        and y > origy and y < origy + self.game.board.get_height():

            bx = (x - origx) // SOKOBAN.SPRITESIZE
            by = (y - origy) // SOKOBAN.SPRITESIZE

            return bx, by


    def show_win(self, window, levelNum):
        self.txtWin.render(window, "Félicitations, niveau " + str(levelNum) + " terminé")
        self.txtPress.render(window)


    def lost_state(self):
        pass


    def render(self, window, levelNum, level):

        self.txtLevel.render(window, "Niveau " + str(levelNum))
        self.txtMoves.render(window, "Coups : " + str(level.num_moves))
        self.txtCancel.render(window)
        self.txtReset.render(window)
        self.txtVisu.render(window)
        self.txtHelp.render(window)
