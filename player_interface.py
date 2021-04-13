import pygame
import constants as SOKOBAN

class PlayerInterface:
    def __init__(self, player, level):
        self.player = player
        self.level = level
        self.mouse_pos = (-1,-1)
        self.font_menu = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 18)
        self.txtLevel = "Niveau 1"
        self.colorTxtLevel = SOKOBAN.BLACK
        self.txtCancel = "Annuler le dernier coup (C)"
        self.colorTxtCancel = SOKOBAN.GREY
        self.txtReset = "Recommencer le niveau (R)"
        self.colorTxtReset = SOKOBAN.BLACK
        self.txtVisu = "Aide visuelle (V)"
        self.colorTxtVisu = SOKOBAN.BLACK


    def cancel(self):
        self.level.cancel_last_move(self.player, self)
        self.colorTxtCancel = SOKOBAN.GREY

    def click(self, pos_click, level, game):
        x = pos_click[0]
        y = pos_click[1]

        callbacks = [
                (self.posTxtVisu,   self.txtVisuSurface,   game.toggle_visualize),
                (self.posTxtReset,  self.txtResetSurface,  game.load_level),
                (self.posTxtCancel, self.txtCancelSurface, self.cancel),
                ]

        for pos,surf,call in callbacks:
            if x > pos[0] and x < pos[0] + surf.get_width() \
            and y > pos[1] and y < pos[1] + surf.get_height():
                call()
                return

    def setTxtColors(self):
        pass

    def render(self, window, level):
        self.txtLevel = "Niveau " + str(level)
        self.txtLevelSurface = self.font_menu.render(self.txtLevel, True, self.colorTxtLevel, SOKOBAN.WHITE)
        window.blit(self.txtLevelSurface, (10, 10))

        self.txtCancelSurface = self.font_menu.render(self.txtCancel, True, self.colorTxtCancel, SOKOBAN.WHITE)
        self.posTxtCancel = (SOKOBAN.WINDOW_WIDTH - self.txtCancelSurface.get_width() - 10, 10)
        window.blit(self.txtCancelSurface, self.posTxtCancel)

        self.txtResetSurface = self.font_menu.render(self.txtReset, True, self.colorTxtReset, SOKOBAN.WHITE)
        self.posTxtReset = ((SOKOBAN.WINDOW_WIDTH / 2) - (self.txtResetSurface.get_width() / 2), 10)
        window.blit(self.txtResetSurface, self.posTxtReset)

        self.txtVisuSurface = self.font_menu.render(self.txtVisu, True, self.colorTxtVisu, SOKOBAN.WHITE)
        self.posTxtVisu = (10, SOKOBAN.WINDOW_HEIGHT - self.txtVisuSurface.get_height() - 10)
        window.blit(self.txtVisuSurface, self.posTxtVisu)


