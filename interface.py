"""
Graphical menus for sokoban
"""

import os
import pygame
from pygame.locals import *
import common as C
import scores as S
from graphics import *
from game import Game
from utils import *


class GenericMenu:

    def __init__(self, window):
        self.window = window
        self.quit_menu = False
        self.clickableTexts = []
        self.renderTexts = []

        self.keys_events = {
            K_ESCAPE: self.set_return,
        }
        pass

    def set_return(self):
        self.quit_menu = True

    def run(self):
        while not self.quit_menu:
            self.handle_event()
            self.window.fill(C.WHITE)
            self.render()
            pygame.display.flip()

    def click(self, pos_click):
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                verbose('clicked on', t.text)
                return True
        return False

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
            if pygame.event.peek(eventtype=VIDEORESIZE):
                return None

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

    def render(self):
        for s in self.renderTexts:
            s.update()
            s.render(self.window)


class Menu(GenericMenu):
    """
    Initial menu when launching the game, with main choices (new game, 
    continue, choose pack, or quit).
    """

    def __init__(self, window):
        super().__init__(window)
        self.image = pygame.image.load(os.path.join(
            'assets', 'images', 'menu.png')).convert_alpha()
        self.font_menu = pygame.font.Font(os.path.join(
            'assets', 'fonts', 'FreeSansBold.ttf'), 30)

        self.load()
        self.run()

    def new_game(self):
        sokoban = Game(self.window, continueGame=False)
        sokoban.start()

    def continue_game(self):
        sokoban = Game(self.window, continueGame=True)
        sokoban.start()

    def mk_pack_name(self):
        return "[ " + S.scores.pack_name() + " ]"

    def choose_pack(self):
        # choosing a level pack
        PackChoice(self.window)
        self.txtPackName.update(self.mk_pack_name())

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

        self.txtPackName = Text(
            self.mk_pack_name(),
            self.font_menu, C.BLUE, C.ACENTER, C.ACUSTOM,
            below=self.txtChoose
        )

        self.txtQuit = Text(
            "Quitter (Q)",
            self.font_menu, C.BLACK, C.ACENTER, C.ABOTTOM,
            # below=self.txtChoose,
            callback=self.set_return,
        )

        self.clickableTexts = [
            self.txtNew,
            self.txtCont,
            self.txtChoose,
            self.txtQuit,
        ]

        self.renderTexts = [
            self.txtPackName
        ] + self.clickableTexts

        self.keys_events.update({
            K_n: self.new_game,
            K_c: self.continue_game,
            K_p: self.choose_pack,
            K_q: self.set_return,
        })

    def render(self):
        xpos = (C.WINDOW_WIDTH - self.image.get_width())//2
        ypos = (C.WINDOW_HEIGHT - self.image.get_height())//2
        sc = pygame.transform.scale(
            self.image, (C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        # window.blit(self.image, (xpos,ypos))
        self.window.blit(sc, (0, 0))

        super().render()


class PackChoice(GenericMenu):
    """
    Menu when choosing a pack of Sokoban levels
    """

    def __init__(self, window):
        super().__init__(window)
        self.font_menu = pygame.font.Font(os.path.join(
            'assets', 'fonts', 'FreeSansBold.ttf'), 30)
        self.font_action = pygame.font.Font(os.path.join(
            'assets', 'fonts', 'FreeSansBold.ttf'), 24)
        self.font_text = pygame.font.Font(os.path.join(
            'assets', 'fonts', 'FreeSansBold.ttf'), 18)

        self.choice = S.scores.current_pack
        self.pack_idx = C.PACKS.index(self.choice)
        self.load()
        self.run()

    def read_desc(self):
        desc = []

        # need to differentiate the last lines as these might be "attached" to
        # the first level
        last_lines = []

        with open(os.path.join('assets', 'levels', self.choice)) as level_file:
            while True:
                l = level_file.readline()
                if valid_soko_line(l):
                    break
                l = l.strip()
                if l == "":
                    desc = desc + last_lines
                    last_lines = []
                last_lines.append(l)  # also appends empty line
        return desc

    def reload(self):
        self.choice = C.PACKS[self.pack_idx]
        desc = self.read_desc()

        self.txtTitle.update(self.choice)
        self.txtDesc.update(desc)

    def choose(self):
        S.scores.set_pack(self.choice)
        self.set_return()

    def next(self):
        self.pack_idx += 1
        self.pack_idx %= len(C.PACKS)
        self.reload()

    def pred(self):
        self.pack_idx += len(C.PACKS) - 1
        self.pack_idx %= len(C.PACKS)
        self.reload()

    def load(self):

        desc = self.read_desc()

        self.txtDesc = Paragraph(
            500, 400,
            desc,
            self.font_text, C.BLACK, C.ACENTER, C.AMID,
        )

        self.txtTitle = Text(
            self.choice,
            self.font_menu, C.BLACK, C.ACENTER, C.ACUSTOM,
            above=self.txtDesc
        )

        self.txtChoose = Text(
            "Choisir ce pack (C)",
            self.font_action, C.BLACK, C.ACENTER, C.ACUSTOM,
            below=self.txtDesc,
            callback=self.choose,
        )

        self.txtNext = Text(
            "Suivant (S)",
            self.font_action, C.BLACK, C.ARIGHT, C.AMID,
            callback=self.next,
        )

        self.txtPrev = Text(
            "Précédent (P)",
            self.font_action, C.BLACK, C.ALEFT, C.AMID,
            callback=self.pred,
        )

        self.txtReturn = Text(
            "Revenir au menu (Q)",
            self.font_action, C.BLACK, C.ACENTER, C.ABOTTOM,
            below=self.txtChoose,
            callback=self.set_return
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

        self.keys_events.update({
            K_c: self.choose,
            K_s: self.next,
            K_p: self.pred,
            K_q: self.set_return,
        })

    def render(self):
        for s in self.renderTexts:
            s.update()
            s.render(self.window)
