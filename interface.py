"""
Graphical menus for sokoban
"""

import os
import pygame
from pygame.locals import *
import common as C
from graphics import *
from game import Game
from utils import *

class GenericMenu:

    def __init__(self):
        self.quit_menu = False

        self.keys_events = {
            K_ESCAPE: self.set_quit,
        }
        pass

    def set_quit(self):
        self.quit_menu = True

    def run(self):
        while not self.quit_menu:
            self.handle_event()
            self.window.fill(C.WHITE)
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
            w, h = event.dict['size']
            C.WINDOW_WIDTH = w
            C.WINDOW_HEIGHT = h
            window = pygame.display.set_mode(
                (C.WINDOW_WIDTH, C.WINDOW_HEIGHT),
                RESIZABLE)
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
        cpack = PackChoice(self.window)
        cpack.render()



    def quit(self):
        pygame.quit()

    def load(self):
        self.txtCont = Text(
            "Continuer (C)",
            self.font_menu, C.BLACK, C.ACENTER, C.AMID,
            callback=self.continue_game
        )

        self.txtNew = Text(
            "Nouvelle partie (N)",
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            above=self.txtCont,
            callback=self.new_game
        )

        self.txtChoose = Text(
            "Choisir pack de niveau (P)",
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            below=self.txtCont,
            callback=self.choose_pack
        )


        self.txtQuit = Text(
            "Quitter partie (Q)",
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            below=self.txtChoose,
            callback=self.set_quit
        )

        self.clickableTexts = [
            self.txtNew,
            self.txtCont,
            self.txtChoose,
            self.txtQuit,
        ]




    def click(self, pos_click):
        self.reset_click()
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                verbose('clicked on', t.text)
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
            s.render(self.window)


class PackChoice(GenericMenu):
    """
    Menu when choosing a pack of Sokoban levels
    """

    def __init__(self, window):
        super().__init__()
        self.window = window
        # with open(os.path.join('assets', 'levels', self.filename)) as level_file:
        self.font_menu = pygame.font.Font(os.path.join('assets', 'fonts', 'FreeSansBold.ttf'), 30)
        self.load()
        self.run()

    def load(self):
        self.txtDesc = Text(
            "Description",
            self.font_menu, C.BLACK, C.ACENTER, C.AMID,
        )

        self.txtTitle = Text(
            "Title",
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            above=self.txtDesc
        )

        self.txtChoose = Text(
            "Choisir ce pack",
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            below=self.txtDesc,
            retval='choose'
        )

        self.txtNext = Text(
            "Suivant",
            self.font_menu, C.BLACK, C.ARIGHT, C.AMID,
            retval='next'
        )

        self.txtPrev = Text(
            "Précédent",
            self.font_menu, C.BLACK, C.ALEFT, C.AMID,
            retval='pred'
        )

        self.txtReturn = Text(
            "Revenir au menu",
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




    def render(self):
        for s in self.renderTexts:
            s.update()
            s.render(self.window)




