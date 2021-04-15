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
            self.level_style = 'single_file'

        self.load_level()
        self.play = True
        self.player_interface = PlayerInterface(self.player, self.level)
        self.visual = False
        self.has_changed = False
        self.selected_position = None

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

        def surfhigh (color, alpha):
            surf = pygame.Surface((SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))
            surf.set_alpha(alpha)
            surf.fill(color) # green highlight
            return surf

        surfAtt  = surfhigh((0,255,0),50) # green highlight
        surfSucc = surfhigh((0,0,255),50) # blue highlight
        surfSelect= surfhigh((255,255,0),200) # yellow highlight
        surfError = surfhigh((255,0,0),200) # red highlight

        self.highlights = {
                SOKOBAN.HATT:   surfAtt,
                SOKOBAN.HSUCC:  surfSucc,
                SOKOBAN.HSELECT:surfSelect,
                SOKOBAN.HERROR :surfError,
                }

    def load_level(self):
        self.level = Level(self, self.index_level, self.level_style)
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
            pygame.time.wait(SOKOBAN.MOVE_DELAY)


    def animate_move_box(self, box, path):
        self.level.dij = None
        for (box,d) in path:
            print ("now path is push", box, "from", SOKOBAN.DNAMES[d])
            pos = self.level.side_box(box, d)

            self.animate_move_to(pos)


            oppd = SOKOBAN.OPPOSITE[d]
            print ("opposite direction:", SOKOBAN.DNAMES[oppd])

            print ("current player pos", self.level.player_position)
            ret = self.player.move(oppd)
            assert (ret) # should have changed the level
            self.update_screen()
            pygame.time.wait(SOKOBAN.MOVE_DELAY)

            # new box position
            box = self.level.side_box(box, oppd)
            print ("new box pos", box)


    def flash_red (self, pos):
        for x in range(4):
            self.level.highlight([pos], SOKOBAN.HERROR)
            pygame.time.wait(SOKOBAN.FLASH_DELAY)
            self.update_screen()
            self.level.reset_highlight()
            pygame.time.wait(SOKOBAN.FLASH_DELAY)
            self.update_screen()


    def cancel_selected(self):
        self.selected_position = None
        self.level.reset_highlight()


    def click_pos (self, position):
        if self.selected_position:
            postype, selpos = self.selected_position

            if postype == SOKOBAN.BOX:
                self.cancel_selected()

                # now try to move the box
                if position == selpos:
                    # same position: auto solving this box to a target
                    path = self.level.solve_one_box(selpos)
                else:
                    # different position: move the box to this area
                    path = self.level.move_one_box(selpos, position)
                if not path:
                    self.flash_red(selpos)
                else:
                    self.animate_move_box(selpos, path)

            else:
                # now we should only select boxes
                assert(false)
            return

        # nothing selected yet
        if self.level.has_box(position):
            # selecting a box
            self.selected_position = (SOKOBAN.BOX, position)
            self.level.highlight([position], SOKOBAN.HSELECT)
        else:
            # trying to move the character
            self.animate_move_to(position)



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

            elif event.key == K_k: # cheat key :-)
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
                self.level.cancel_last_change()
                self.player_interface.colorTxtCancel = SOKOBAN.GREY

            # "Test" key
            elif event.key == K_t:
                pass
                path = self.level.move_one_box((8, 3), (4, 3))
                if not path:
                    self.flash_red((8,3))
                else:
                    self.animate_move_box((8,3), path)


        elif event.type == MOUSEBUTTONUP:
            position = self.player_interface.click(event.pos, self.level, self)
            if position:
                self.click_pos(position)
            else:
                self.cancel_selected()

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

        for y in range(self.level.map_height):
            for x in range(self.level.map_width):
                if self.level.is_target((x,y)):
                    if not self.level.has_box((x,y)):
                        nb_missing_target += 1

        return nb_missing_target == 0
