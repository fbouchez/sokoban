import os
import pygame
import common as C
from game import Game
from utils import *

BORDER = 10

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
        self.surf = None
        self.update(text)


    def change_color(self, color):
        self.color = color
        self.update()

    def update(self, text=None):
        if text:
            self.text = text
        self.surf= self.font.render(self.text, True, self.color, C.WHITE)

        if self.xalign == C.ALEFT:
            xpos = BORDER
        elif self.xalign == C.ACENTER:
            xpos= C.WINDOW_WIDTH // 2 - self.surf.get_width() // 2
        elif self.xalign == C.ARIGHT:
            xpos= C.WINDOW_WIDTH - self.surf.get_width() - BORDER
        elif self.xalign == C.ACUSTOM:
            xpos=self.pos[0]
        else:
            raise ValueError("Horizontal alignment")

        if self.yalign == C.ATOP:
            ypos = BORDER
        elif self.yalign == C.AMID:
            ypos= C.WINDOW_HEIGHT // 2 - self.surf.get_height() // 2
        elif self.yalign == C.ABOTTOM:
            ypos= C.WINDOW_HEIGHT - self.surf.get_height() - BORDER
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


class GenericMenu:

    def __init__(self):
        self.quit_menu = False

        self.keys_events = {
                K_ESCAPE: self.set_quit
        }
        pass

    def set_quit(self):
        self.quit_menu = True

    def run(self):
        while not self.quit_menu:
            handle_event()
            window.fill(C.WHITE)
            self.render()
            pygame.display.flip()

    def render(self):
        pass


    def handle_event(self):
        """
        Check user inputs: mouse, keyboard, window resizing, etc.
        Return None, if event has been handled, the event itself
        if not.
        """

        event = pygame.event.wait()
        if event.type == QUIT:
            # window was closed
            pygame.quit()

        if event.type == VIDEORESIZE:
            w,h = event.dict['size']
            C.WINDOW_WIDTH = w
            C.WINDOW_HEIGHT = h
            window = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT),RESIZABLE)
            return None

        if event.type == KEYDOWN:
            # keyboard interactions
            #      sokoban = Game(window, continueGame = False)
 
            if event.key in self.keys_events:
                cb = self.keys_events[event.key]
                cb()
                return None

        elif event.type == MOUSEBUTTONDOWN:
            # mouse interactions
            if self.click(event.pos):
                # clickable area
                return None
            else:
                # event was handled anyway
                return None

        # event was not processed
        return event



class Menu(GenericMenu):
    """
    Initial menu when launching the game, with main choices (new game, 
    continue, choose pack, or quit).
    """
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.image = pygame.image.load(os.path.join('assets', 'images', 'menu.png')).convert_alpha()
        self.font_menu = pygame.font.Font(os.path.join('assets', 'fonts', 'FreeSansBold.ttf'), 30)

        self.keys_events.update ( {
            K_n: self.new_game,
            K_c: self.continue_game,
            K_p: self.choose_pack,
            K_q: self.set_quit
        } )

        self.load()
        self.run()

    def new_game(self):
        sokoban = Game(self.window, continueGame=False)
        sokoban.start()

    def continue_game(self):
        sokoban = Game(self.window, continueGame=True)
        sokoban.start()

    def choose_pack(self):
        # choosing a level pack
        cpack = PackChoice()
        cpack.render()



    def quit(self):
        pygame.quit()

    def load(self):
        self.txtCont = Text(
            "Continuer (C)",
            self.font_menu, C.BLACK, C.ACENTER, C.AMID,
            callback=self.set_continue_game
            )

        self.txtNew = Text("Nouvelle partie (N)",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                above=self.txtCont,
                callback=self.set_new_game
                )

        self.txtChoose = Text("Choisir pack de niveau (P)",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                below=self.txtCont,
                callback=self.set_new_game
                )


        self.txtQuit = Text("Quitter partie (Q)",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                below=self.txtChoose,
                callback=self.set_quit
                )

        self.clickableTexts = [
                self.txtNew,
                self.txtCont,
                self.txtChoose,
                self.txtQuit
                ]




    def click(self, pos_click):
        self.reset_click()
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                verbose('clicked on',t.text)
                return True
        return False


    def render(self):
        xpos = (C.WINDOW_WIDTH - self.image.get_width())//2
        ypos = (C.WINDOW_HEIGHT - self.image.get_height())//2
        sc = pygame.transform.scale(self.image, (C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        # window.blit(self.image, (xpos,ypos))
        self.window.blit(sc, (0, 0))

        for s in self.clickableTexts:
            s.update()
            s.render(window)


class PackChoice(GenericMenu):
    """
    Menu when choosing a pack of Sokoban levels
    """

    def __init__(self):
        # with open(os.path.join('assets', 'levels', self.filename)) as level_file:
        self.font_menu = pygame.font.Font(os.path.join('assets','fonts','FreeSansBold.ttf'), 30)
        self.load()

    def load(self):
        self.txtTitle = Text("Title",
                self.font_menu, C.BLACK, C.ACENTER, C.AMID
                )

        self.txtDesc = Text("Description",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                above=self.txtCont,
                )

        self.txtChoose = Text("Choisir ce pack",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                below=self.txtCont,
                retval='choose'
                )

        self.txtNext = Text("Suivant",
                self.font_menu, C.BLACK, C.ARIGHT, C.AMID,
                retval='next'
                )

        self.txtPrev = Text("Précédent",
                self.font_menu, C.BLACK, C.ALEFT, C.AMID,
                retval='pred'
                )

        self.txtReturn = Text("Revenir au menu",
                self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
                below=self.txtChoose,
                retval='return'
                )

        self.clickableTexts = [
                self.txtChoose,
                self.txtReturn,
                self.txtNext,
                self.txtPrev,
                ]

        self.renderTexts = [
                self.txtTitle,
                self.txtDesc,
                ] + self.clickableTexts


    def click(self, pos_click):
        self.reset_click()
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                verbose('clicked on',t.text)
                return True
        return False




    def render(self, window):
        for s in self.renderTexts:
            s.update()
            s.render(window)




class Interface:
    """
    Interface when playing the sokoban levels, with level title, number of 
    moves, possibility to cancel. etc.
    """
    def __init__(self, game):
        self.game = game
        self.level = None
        self.mouse_pos = (-1,-1)
        self.font_messages = pygame.font.Font(os.path.join('assets','fonts','FreeSansBold.ttf'), 18)
        self.font_win  = pygame.font.Font(os.path.join('assets','fonts','FreeSansBold.ttf'), 32)
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
        self.txtCancel.change_color(C.GREY)
        self.is_lost=False
        self.has_info=False
        self.is_solving=False

    def load_assets(self):

        self.txtLevel = Text("Niveau 1",
                self.font_messages, C.BLUE, C.ALEFT, C.ATOP,
                callback=None)

        self.txtTitle = Text(" ",
                self.font_messages, C.BLUE, C.ALEFT, C.ACUSTOM,
                callback=None)

        self.txtTitle.set_pos(below=self.txtLevel)



        self.txtCancel = Text("Annuler le dernier coup (C)",
                self.font_messages, C.GREY, C.ARIGHT, C.ATOP,
                callback=self.game.cancel_move)

        self.txtReset = Text("Recommencer le niveau (R)",
                self.font_messages, C.BLACK, C.ACENTER, C.ATOP,
                callback=self.game.load_level)

        self.txtVisu = Text("Aide visuelle (V)",
                self.font_messages, C.BLACK, C.ALEFT, C.ABOTTOM,
                callback=self.game.toggle_visualize)

        self.txtHelp = Text("Aide sokoban (H) / Résolution complète (A)",
                self.font_messages, C.BLACK, C.ACENTER, C.ABOTTOM,
                callback=None)

        self.txtMoves = Text("Coups : 0",
                self.font_messages, C.BLACK, C.ARIGHT, C.ABOTTOM,
                callback=None)

        self.txtBestMoves = Text("Meilleur : infini",
                self.font_messages, C.BLACK, C.ARIGHT, C.ACUSTOM,
                above=self.txtMoves,
                callback=None)



        self.txtWin = Text ("Félicitations, niveau 1 terminé",
                self.font_win, C.BLACK, C.ACENTER, C.ACUSTOM,
                callback=None)
        self.txtWin.set_pos(below=self.txtReset)

        self.ymessages=210

        self.txtPress = Text ("(appuyez sur une touche pour continuer)",
                self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
                callback=None)
        self.txtPress.set_pos(below=self.txtWin)

        self.txtLost = Text ("Résolution impossible (certaines boîtes sont définitivement coincées)",
                self.font_messages, C.RED, C.ACENTER, C.ACUSTOM,
                yfun=self.compute_ymessages,
                callback=None)

        self.txtResol = Text ("Résolution en cours (Esc pour annuler)",
                self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
                yfun=lambda: self.compute_ymessages() - 30,
                callback=None)


        self.txtInfo = Text (" ",
                self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
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
                self.txtBestMoves,
                self.txtPress,
                self.txtInfo,
                self.txtResol,
                self.txtLost
                ]

    def compute_ymessages(self):
        return C.WINDOW_HEIGHT - 80

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

            bx = (x - origx) // C.SPRITESIZE
            by = (y - origy) // C.SPRITESIZE

            return bx, by


    def show_win(self, window, levelNum):
        self.txtWin.render(window, "Félicitations, niveau " + str(levelNum) + " terminé")

    def show_press_key(self, window):
        self.txtPress.render(window)

    def set_lost_state(self, lost):
        self.is_lost = lost

    def activate_cancel(self):
        self.txtCancel.change_color(C.BLACK)

    def deactivate_cancel(self):
        self.txtCancel.change_color(C.GREY)

    def best_moves(self, best):
        if best is None:
            self.txtBestMoves.update("Meilleur : infini")
        else:
            self.txtBestMoves.update("Meilleur : "+str(best))

    def display_info(self, message=None, error=False):
        if message is not None:
            self.txtInfo.update(message)
        self.txtInfo.update(message)
        if error:
            self.txtInfo.change_color(C.RED)
        else:
            self.txtInfo.change_color(C.BLACK)


    def set_solving(self, flag, num=None, message=None, error=False):
        self.has_info = flag
        self.is_solving = flag
        if num is not None:
            message = "Résolution en cours, " + str(num) + " états explorés (Esc pour annuler)"
        self.display_info(message, error)


    def flash_screen (self, pos=None, color=C.RED):
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
                self.game.level.highlight([pos], C.HERROR)
                self.game.update_screen()
            else:
                self.game.window.blit(surf, self.game.origin_board)
                pygame.display.flip()
            pygame.time.wait(C.FLASH_DELAY)

            if pos is not None:
                self.game.level.reset_highlight()
            self.game.update_screen()
            pygame.time.wait(C.FLASH_DELAY)


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
        self.txtBestMoves.render(window)
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
