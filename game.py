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
        self.player_interface = None
        self.scores = Scores(self)
        self.scores.load()

        if continueGame:
            self.index_level = self.scores.last_level()
        else:
            self.index_level = 0

        self.load_level(nextLevel=True)
        self.play = True
        self.player_interface = PlayerInterface(self, self.player, self.level)
        self.visual = False
        self.has_changed = False
        self.selected_position = None

        self.start()

    def load_textures(self):
        ground = pygame.image.load('assets/images/stoneCenter.png').convert_alpha()

        self.textures = {
            SOKOBAN.WALL: pygame.image.load('assets/images/wall.png').convert_alpha(),
            SOKOBAN.BOX: pygame.image.load('assets/images/box.png').convert_alpha(),
            SOKOBAN.TARGET: ground,
            SOKOBAN.TARGETOVER: pygame.image.load('assets/images/target.png').convert_alpha(),
            # SOKOBAN.TARGETOVER: pygame.image.load('assets/images/target.png').convert(),
            # SOKOBAN.TARGET_FILLED: pygame.image.load('assets/images/valid_box.png').convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load('assets/images/box_correct.png').convert_alpha(),
            SOKOBAN.PLAYER: pygame.image.load('assets/images/player_sprites.png').convert_alpha(),
            SOKOBAN.GROUND: ground
        }
        self.textures[SOKOBAN.TARGETOVER].set_alpha(128) # does not seem to have any effect

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

    def load_level(self, nextLevel=False):
        if nextLevel:
            self.index_level += 1
        self.level = Level(self, self.index_level, self.scores.level_style())
        if self.player_interface:
            self.player_interface.txtCancel.change_color(SOKOBAN.GREY)

        if not self.level.success:
            self.play = False
            return


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


    def animate_move_boxes(self, path, skip_last=False, fast=True):
        self.level.invalidate()

        for last,(box,d) in islast(path):

            verbose ("now path is push", box, "from", SOKOBAN.DNAMES[d])
            pos = self.level.side_box(box, d)

            self.animate_move_to(pos)
            oppd = SOKOBAN.OPPOSITE[d]

            if not skip_last or not last:
                ret = self.player.move(oppd)
                assert (ret) # should have changed the level

            self.update_screen()
            if fast:
                pygame.time.wait(SOKOBAN.FLASH_DELAY)
            else:
                pygame.time.wait(SOKOBAN.SOLVE_DELAY)

            # new box position
            box = self.level.side_box(box, oppd)
            verbose ("New box position", box)

        if self.has_win():
            self.level_win()


    def flash_screen (self, pos=None, color=SOKOBAN.RED):
        if pos is None:
            surf = pygame.Surface((self.board.get_width(), self.board.get_height()))
            surf.set_alpha(50)
            surf.fill(color)

        for x in range(4):
            if pos is not None:
                self.level.highlight([pos], SOKOBAN.HERROR)
            else:
                self.window.blit(surf, self.origin_board)
            pygame.display.flip()
            pygame.time.wait(SOKOBAN.FLASH_DELAY)

            if pos is not None:
                self.level.reset_highlight()
            self.update_screen()
            pygame.time.wait(SOKOBAN.FLASH_DELAY)


    def cancel_selected(self):
        self.selected_position = None
        self.level.reset_highlight()


    def click_pos (self, position):
        if self.selected_position:
            postype, selpos = self.selected_position

            if postype == SOKOBAN.BOX:
                self.cancel_selected()

                self.player_interface.set_solving(True, num=0)

                # now try to move the box
                if position == selpos:
                    # same position: auto solving this box to a target
                    found,message,path = self.level.solve_one_box(selpos)
                else:
                    # different position: move the box to this area
                    found,message,path = self.level.move_one_box(selpos, position)

                self.player_interface.set_solving(True,
                        message=message,
                        error=not found
                    )

                if not path:
                    self.flash_screen(selpos)
                else:
                    self.animate_move_boxes(path)

                self.player_interface.set_solving(False)

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

        if event.type == KEYDOWN:
            self.cancel_selected()
            if event.key == K_ESCAPE:
                # Quit game
                self.play = False
                return

            elif event.key in KEYDIR.keys():
                direction = KEYDIR[event.key]

                # Move player
                self.has_changed = self.player.move(direction)
                if self.has_changed:
                    self.player_interface.txtCancel.change_color(SOKOBAN.BLACK)

                if self.has_win():
                    self.level_win()
                    return

                lost = self.level.lost_state()
                if lost:
                    verbose ("Lost state !")
                self.player_interface.set_lost_state(lost)

            elif event.key == K_k: # cheat key :-)
                    self.load_level(nextLevel=True)

            elif event.key == K_r:
                # Restart current level
                self.load_level(nextLevel=False)

            elif event.key == K_v:
                # Vizualize possible moves
                self.toggle_visualize()

            elif event.key == K_c:
                # Cancel last move
                self.player_interface.cancel()

                lost = self.level.lost_state()
                if lost:
                    verbose ("Lost state !")
                self.player_interface.set_lost_state(lost)



            # "Test" key
            elif event.key == K_t:
                pass
                path = self.level.move_one_box((8, 3), (4, 3))
                if not path:
                    self.flash_screen((8,3))
                else:
                    self.animate_move_boxes(path)

            # "all box solve" key
            elif event.key == K_a:
                self.player_interface.set_solving(True, num=0)
                found,message,path = self.level.solve_all_boxes()
                if not found:
                    self.player_interface.set_solving(True,
                            message=message,
                            error=True
                            )
                    self.flash_screen()
                    self.update_screen()
                    self.wait_key()

                else:
                    self.player_interface.set_solving(True,
                            message=message,
                            error=False)
                    self.flash_screen(color=SOKOBAN.GREEN)
                    self.wait_key()
                    self.animate_move_boxes(path, skip_last=True, fast=False)

                self.player_interface.set_solving(False)

        elif event.type == MOUSEBUTTONDOWN:
            position = self.player_interface.click(event.pos, self.level)
            if position:
                self.click_pos(position)
            else:
                self.cancel_selected()

        elif event.type == MOUSEMOTION:
            self.player_interface.mouse_pos = event.pos
        # else:
            # print ("Unknown event:", event)
            #

    def wait_key(self):
        self.update_screen()
        self.player_interface.show_press_key(self.window)
        pygame.display.flip()
        while True:
            event = pygame.event.wait()
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                break

    def update_check_cancel(self, num_states):
        self.player_interface.set_solving(True, num=num_states)
        self.update_screen()
        event = pygame.event.poll()

        while event.type != NOEVENT:
            if event.type == KEYDOWN \
            and event.key == K_ESCAPE:
                self.player_interface.set_solving(False)
                return True
            event = pygame.event.poll()
        return False


    def debug(self):
        self.update_screen()
        print ("Waiting for keypress...")
        self.wait_key()

    def level_win(self):
        self.scores.save()
        self.update_screen()
        self.player_interface.show_win(self.window, self.index_level)
        pygame.display.flip()
        self.wait_key()

        self.load_level(nextLevel=True)


    def update_screen(self):
        if not self.level.success: return

        # clear screen
        self.window.fill(SOKOBAN.WHITE)
        self.board.fill(SOKOBAN.WHITE)

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
