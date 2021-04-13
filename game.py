import pygame
import sys
from pygame.locals import *
import constants as SOKOBAN
from level import *
from explore import *
from player import *
from scores import *
from player_interface import *

KEYDIR = {
        K_UP: SOKOBAN.UP,
        K_DOWN: SOKOBAN.DOWN,
        K_LEFT: SOKOBAN.LEFT,
        K_RIGHT: SOKOBAN.RIGHT,
        K_z: SOKOBAN.UP,
        K_s: SOKOBAN.DOWN,
        K_q: SOKOBAN.LEFT,
        K_d: SOKOBAN.RIGHT
        }

class Game:
    def __init__(self, window, continueGame=True):
        self.window = window
        self.load_textures()
        self.player = None
        self.scores = Scores(self)

        if continueGame:
            self.scores.load()
        else:
            self.index_level = 1

        self.load_level()
        self.play = True
        self.player_interface = PlayerInterface(self.player, self.level)
        self.visual = False
        self.has_changed = False

        self.start()

    def load_textures(self):
        self.textures = {
            SOKOBAN.WALL: pygame.image.load('assets/images/wall.png').convert_alpha(),
            SOKOBAN.BOX: pygame.image.load('assets/images/box.png').convert_alpha(),
            SOKOBAN.TARGET: pygame.image.load('assets/images/target.png').convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load('assets/images/valid_box.png').convert_alpha(),
            SOKOBAN.PLAYER: pygame.image.load('assets/images/player_sprites.png').convert_alpha(),
            SOKOBAN.GROUND: pygame.image.load('assets/images/stoneCenter.png').convert_alpha()
        }
        # self.textures[SOKOBAN.TARGET].set_alpha(12) # does not seem to have any effect
        surfAtt = pygame.Surface((SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))
        surfAtt.set_alpha(50)
        surfAtt.fill((0,255,0)) # green highlight

        surfSucc = pygame.Surface((SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))
        surfSucc.set_alpha(50)
        surfSucc.fill((0,0,255)) # blue highlight

        self.highlights = {
                SOKOBAN.HATT:  surfAtt,
                SOKOBAN.HSUCC: surfSucc
                }

    def load_level(self):
        self.level = Level(self.index_level)
        self.board = pygame.Surface((self.level.width, self.level.height))
        if self.player:
            self.player_interface.level = self.level
            self.player.level = self.level
        else:
            self.player = Player(self.level)

    def toggle_visualize(self):
        # toggle visu
        self.visual = not(self.visual)
        self.has_changed = True
        if not self.visual:
            # just got deactivated
            self.level.reset_highlight()


    def start(self):
        while self.play:
            self.process_event(pygame.event.wait())
            self.update_screen()


    def animate_move_to(self, position):
        path = self.level.path_to(position)
        if not path:
            return

        for d in path:
            self.player.move(d)
            self.update_screen()


    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                # Quit game
                self.play = False
            elif event.key in KEYDIR.keys():
                direction = KEYDIR[event.key]

                # Move player
                self.has_changed = self.player.move(direction)
                if self.has_changed:
                    self.player_interface.colorTxtCancel = SOKOBAN.BLACK

                if self.has_win():
                    self.index_level += 1
                    self.scores.save()
                    self.load_level()
            elif event.key == K_r:
                # Restart current level
                self.load_level()
            elif event.key == K_v:
                # Vizualize possible moves
                self.toggle_visualize()
            elif event.key == K_c:
                # Cancel last move
                self.level.cancel_last_move(self.player)
                self.player_interface.colorTxtCancel = SOKOBAN.GREY

        elif event.type == MOUSEBUTTONUP:
            position = self.player_interface.click(event.pos, self.level, self)
            if position:
                self.animate_move_to(position)

        elif event.type == MOUSEMOTION:
            self.player_interface.mouse_pos = event.pos
        # else:
            # print ("Unknown event:", event)

    def update_screen(self):
        pygame.draw.rect(self.board, SOKOBAN.WHITE, (0,0, self.level.width * SOKOBAN.SPRITESIZE, self.level.height * SOKOBAN.SPRITESIZE))
        pygame.draw.rect(self.window, SOKOBAN.WHITE, (0,0,SOKOBAN.WINDOW_WIDTH,SOKOBAN.WINDOW_HEIGHT))

        self.level.render(self.board, self.textures, self.highlights)
        self.player.render(self.board, self.textures)

        if self.has_changed:
            self.has_changed=False
            if self.visual:
                self.level.update_visual()

        pos_x_board = (SOKOBAN.WINDOW_WIDTH // 2) - (self.board.get_width() // 2)
        pos_y_board = (SOKOBAN.WINDOW_HEIGHT // 2) - (self.board.get_height() // 2)
        self.window.blit(self.board, (pos_x_board, pos_y_board))

        self.origin_board = (pos_x_board, pos_y_board)

        self.player_interface.render(self.window, self.index_level, self.level)

        pygame.display.flip()

    def has_win(self):
        nb_missing_target = 0
        for y in range(len(self.level.structure)):
            for x in range(len(self.level.structure[y])):
                if self.level.structure[y][x] == SOKOBAN.TARGET:
                    nb_missing_target += 1

        return nb_missing_target == 0
