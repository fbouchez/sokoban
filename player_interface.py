import pygame
import constants as SOKOBAN

class PlayerInterface:
    def __init__(self, player, level):
        self.player = player
        self.level = level
        self.mouse_pos = (-1,-1)
        self.font_menu = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 18)
        self.font_win  = pygame.font.Font('assets/fonts/FreeSansBold.ttf', 32)
        self.txtLevel = "Niveau 1"
        self.colorTxtLevel = SOKOBAN.BLACK
        self.txtCancel = "Annuler le dernier coup (C)"
        self.colorTxtCancel = SOKOBAN.GREY
        self.txtReset = "Recommencer le niveau (R)"
        self.colorTxtReset = SOKOBAN.BLACK
        self.txtVisu = "Aide visuelle (V)"
        self.colorTxtVisu = SOKOBAN.BLACK
        self.txtMoves = "Coups : 0"
        self.colorTxtMoves = SOKOBAN.BLACK

        self.txtPress = "(appuyez sur une touche pour continuer)"
        self.colorTxtPress = SOKOBAN.BLACK

    def cancel(self):
        ret = self.level.cancel_last_change()
        if not ret:
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
                return None

        # check if clicked in the game

        origx, origy = game.origin_board
        if x > origx and x < origx + game.board.get_width() \
        and y > origy and y < origy + game.board.get_height():

            bx = (x - origx) // SOKOBAN.SPRITESIZE
            by = (y - origy) // SOKOBAN.SPRITESIZE

            return bx, by

    def show_win(self, window, levelNum):

        self.txtWin = "Félicitations, niveau " + str(levelNum) + " terminé"
        self.txtWinSurface = self.font_win.render(self.txtWin, True, self.colorTxtLevel, SOKOBAN.WHITE)

        self.posTxtWin = ((SOKOBAN.WINDOW_WIDTH // 2) - (self.txtWinSurface.get_width() // 2),
                          (self.txtWinSurface.get_height() +10))
        window.blit(self.txtWinSurface, self.posTxtWin)

        self.txtPressSurface = self.font_menu.render(self.txtPress, True, self.colorTxtPress, SOKOBAN.WHITE)
        self.posTxtPress = ((SOKOBAN.WINDOW_WIDTH // 2) - (self.txtPressSurface.get_width() // 2),
                          (self.txtWinSurface.get_height() + self.txtPressSurface.get_height()+40))
        window.blit(self.txtPressSurface, self.posTxtPress)



        self.txtPress = "(appuyez sur une touche pour continuer)"
        self.colorTxtPress = SOKOBAN.BLACK


    def render(self, window, levelNum, level):
        self.txtLevel = "Niveau " + str(levelNum)
        self.txtLevelSurface = self.font_menu.render(self.txtLevel, True, self.colorTxtLevel, SOKOBAN.WHITE)
        window.blit(self.txtLevelSurface, (10, 10))

        self.txtMoves = "Coups : " + str(level.num_moves)
        self.txtMovesSurface = self.font_menu.render(self.txtMoves, True, self.colorTxtLevel, SOKOBAN.WHITE)
        self.posTxtMoves = (
                SOKOBAN.WINDOW_WIDTH - self.txtMovesSurface.get_width() - 10,
                SOKOBAN.WINDOW_HEIGHT - self.txtMovesSurface.get_height() - 10)
        window.blit(self.txtMovesSurface, self.posTxtMoves)

        self.txtCancelSurface = self.font_menu.render(self.txtCancel, True, self.colorTxtCancel, SOKOBAN.WHITE)
        self.posTxtCancel = (SOKOBAN.WINDOW_WIDTH - self.txtCancelSurface.get_width() - 10, 10)
        window.blit(self.txtCancelSurface, self.posTxtCancel)

        self.txtResetSurface = self.font_menu.render(self.txtReset, True, self.colorTxtReset, SOKOBAN.WHITE)
        self.posTxtReset = ((SOKOBAN.WINDOW_WIDTH / 2) - (self.txtResetSurface.get_width() / 2), 10)
        window.blit(self.txtResetSurface, self.posTxtReset)

        self.txtVisuSurface = self.font_menu.render(self.txtVisu, True, self.colorTxtVisu, SOKOBAN.WHITE)
        self.posTxtVisu = (10, SOKOBAN.WINDOW_HEIGHT - self.txtVisuSurface.get_height() - 10)
        window.blit(self.txtVisuSurface, self.posTxtVisu)


