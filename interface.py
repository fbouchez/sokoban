import pygame
import constants as SOKOBAN

BORDER = 10

class Text:
    def __init__(self,text,font,color,xalign,yalign,x=0,y=0,below=None,above=None,yfun=None,callback=None):
        self.font  = font
        self.color = color
        self.xalign = xalign
        self.yalign = yalign
        self.yfun = yfun
        self.below = below
        self.above = above
        self.callback = callback
        self.pos  = (x,y)
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
            y = below.pos[1] + below.surf.get_height()+BORDER
        elif above is not None:
            y = above.pos[1] - self.surf.get_height()-BORDER
        elif self.yfun is not None:
            y = self.yfun()

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


class Menu:
    def __init__(self):
        self.image = pygame.image.load('assets/images/menu.png').convert_alpha()
        self.font_menu = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 30)

        self.new_game = False
        self.continue_game = False
        self.quit = False

        self.load()

    def set_new_game(self):
        self.new_game = True
    def set_continue_game(self):
        self.continue_game = True
    def set_quit(self):
        self.quit = True

    def load(self):
        self.txtCont = Text("Continuer",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.AMID,
                callback=self.set_continue_game
                )

        self.txtNew = Text("Nouvelle partie",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                above=self.txtCont,
                callback=self.set_new_game
                )

        self.txtQuit = Text("Quitter partie",
                self.font_menu, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                below=self.txtCont,
                callback=self.set_quit
                )

        self.clickableTexts = [
                self.txtNew,
                self.txtCont,
                self.txtQuit
                ]




    def click(self, pos_click):
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                return True
        return False

    def render(self, window):
        xpos = (SOKOBAN.WINDOW_WIDTH - self.image.get_width())//2
        ypos = (SOKOBAN.WINDOW_HEIGHT - self.image.get_height())//2
        sc = pygame.transform.scale(self.image, (SOKOBAN.WINDOW_WIDTH, SOKOBAN.WINDOW_HEIGHT))
        # window.blit(self.image, (xpos,ypos))
        window.blit(sc, (0, 0))

        for s in self.clickableTexts:
            s.update()
            s.render(window)


class Interface:
    def __init__(self, game):
        self.game = game
        self.level = None
        self.mouse_pos = (-1,-1)
        self.font_messages = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 18)
        self.font_win  = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 32)
        self.is_lost=False
        self.has_info=False
        self.is_solving=False
        self.load_assets()

    def set_level(self, level, level_num, title=None):
        self.reset()
        self.level = level
        self.txtLevel.update("Niveau " + str(level_num))
        if title:
            self.txtTitle.update(title)
        else:
            self.txtTitle.update(" ")



    def reset(self):
        self.txtCancel.change_color(SOKOBAN.GREY)
        self.is_lost=False
        self.has_info=False
        self.is_solving=False

    def load_assets(self):

        self.txtLevel = Text("Niveau 1",
                self.font_messages, SOKOBAN.BLUE, SOKOBAN.ALEFT, SOKOBAN.ATOP,
                callback=None)

        self.txtTitle = Text(" ",
                self.font_messages, SOKOBAN.BLUE, SOKOBAN.ALEFT, SOKOBAN.ACUSTOM,
                callback=None)

        self.txtTitle.set_pos(below=self.txtLevel)



        self.txtCancel = Text("Annuler le dernier coup (C)",
                self.font_messages, SOKOBAN.GREY, SOKOBAN.ARIGHT, SOKOBAN.ATOP,
                callback=self.game.cancel_move)

        self.txtReset = Text("Recommencer le niveau (R)",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ATOP,
                callback=self.game.load_level)

        self.txtVisu = Text("Aide visuelle (V)",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ALEFT, SOKOBAN.ABOTTOM,
                callback=self.game.toggle_visualize)

        self.txtHelp = Text("Aide sokoban (H) / Résolution complète (A)",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ABOTTOM,
                callback=None)

        self.txtMoves = Text("Coups : 0",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ARIGHT, SOKOBAN.ABOTTOM,
                callback=None)


        self.txtWin = Text ("Félicitations, niveau 1 terminé",
                self.font_win, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                callback=None)
        self.txtWin.set_pos(below=self.txtReset)

        self.ymessages=210

        self.txtPress = Text ("(appuyez sur une touche pour continuer)",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                callback=None)
        self.txtPress.set_pos(below=self.txtWin)

        self.txtLost = Text ("Résolution impossible (certaines boîtes sont définitivement coincées)",
                self.font_messages, SOKOBAN.RED, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                yfun=self.compute_ymessages,
                callback=None)

        self.txtResol = Text ("Résolution en cours (Esc pour annuler)",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                yfun=lambda: self.compute_ymessages() - 30,
                callback=None)


        self.txtInfo = Text (" ",
                self.font_messages, SOKOBAN.BLACK, SOKOBAN.ACENTER, SOKOBAN.ACUSTOM,
                yfun=self.compute_ymessages,
                callback=None)


        self.clickableTexts = [
                self.txtCancel,
                self.txtReset,
                self.txtVisu,
                self.txtHelp,
                ]

        self.all_texts = self.clickableTexts + \
                [
                self.txtLevel,
                self.txtMoves,
                self.txtPress,
                self.txtInfo,
                self.txtResol,
                self.txtLost
                ]

    def compute_ymessages(self):
        return SOKOBAN.WINDOW_HEIGHT - 80

    def click(self, pos_click, level):
        # check if some text has been clicked
        for t in self.clickableTexts:
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

    def show_press_key(self, window):
        self.txtPress.render(window)

    def set_lost_state(self, lost):
        self.is_lost = lost

    def activate_cancel(self):
        self.txtCancel.change_color(SOKOBAN.BLACK)

    def deactivate_cancel(self):
        self.txtCancel.change_color(SOKOBAN.GREY)


    def display_info(self, message=None, error=False):
        if message is not None:
            self.txtInfo.update(message)
        self.txtInfo.update(message)
        if error:
            self.txtInfo.change_color(SOKOBAN.RED)
        else:
            self.txtInfo.change_color(SOKOBAN.BLACK)


    def set_solving(self, flag, num=None, message=None, error=False):
        self.has_info = flag
        self.is_solving = flag
        if num is not None:
            message = "Résolution en cours, " + str(num) + " états explorés (Esc pour annuler)"
        self.display_info(message, error)


    def flash_screen (self, pos=None, color=SOKOBAN.RED):
        """
        Briefly flash a given tile at 'pos', or the whole board.
        """
        if pos is None:
            surf = pygame.Surface((self.game.board.get_width(),
                                   self.game.board.get_height()))
            surf.set_alpha(50)
            surf.fill(color)

        for x in range(4):
            if pos is not None:
                self.game.level.highlight([pos], SOKOBAN.HERROR)
                self.game.update_screen()
            else:
                self.game.window.blit(surf, self.game.origin_board)
                pygame.display.flip()
            pygame.time.wait(SOKOBAN.FLASH_DELAY)

            if pos is not None:
                self.game.level.reset_highlight()
            self.game.update_screen()
            pygame.time.wait(SOKOBAN.FLASH_DELAY)


    def update_positions(self):
        """
        Update all alignments after a window resizing
        """
        for s in self.all_texts:
            s.update()


    def render(self, window, level_num, level):

        self.txtLevel.render(window)
        self.txtTitle.render(window)
        self.txtMoves.render(window, "Coups : " + str(level.num_moves))
        self.txtCancel.render(window)
        self.txtReset.render(window)
        self.txtVisu.render(window)
        self.txtHelp.render(window)
        if self.is_lost:
            self.txtLost.render(window)

        if self.has_info:
            self.txtInfo.render(window)
        if self.is_solving:
            self.txtResol.render(window)
