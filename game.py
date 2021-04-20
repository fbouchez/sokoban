import pygame
import sys
from pygame.locals import *
import constants as SOKOBAN
from level import *
from explore import *
from player import *
from scores import *
from interface import *
from queue import Queue

KEYDIR = {
        # regular arrow keys
        K_UP: SOKOBAN.UP,
        K_DOWN: SOKOBAN.DOWN,
        K_LEFT: SOKOBAN.LEFT,
        K_RIGHT: SOKOBAN.RIGHT,
        # classical on Azerty keyboard
        K_z: SOKOBAN.UP,
        K_s: SOKOBAN.DOWN,
        K_q: SOKOBAN.LEFT,
        K_d: SOKOBAN.RIGHT
}

# keyboard keys corresponding to move directions
DIRKEY = [
        K_UP,
        K_DOWN,
        K_LEFT,
        K_RIGHT
        ]


class Game:
    """
    Class for a game of Sokoban.
    This is where the actions are decided, based on key presses,
    interaction with the graphical interface via the mouse,
    or from movements discovered using the Artificial Intelligence.
    Arguments:
    - window: where to draw things
    - continueGame: whether to continue from last saved level (from the 
      'scores' file) or to restart at level 1.

    """
    def __init__(self, window, continueGame=True):
        self.window = window
        self.player = None
        self.interface = None
        self.level = self.level = Level(self, 
                SOKOBAN.SINGLE_FILE, # filename
                single_file=True
                )
        self.scores = Scores(self)
        self.load_textures()

        if continueGame:
            self.index_level = self.scores.last_level()
        else:
            self.index_level = 0

        self.interface = Interface(self)
        self.playing = False
        self.visual = False
        self.has_changed = False
        self.selected_position = None

    def load_textures(self):
        ground = pygame.image.load('assets/images/stoneCenter.png').convert_alpha()

        self.textures = {
            SOKOBAN.WALL: pygame.image.load('assets/images/wall.png').convert_alpha(),
            SOKOBAN.BOX: pygame.image.load('assets/images/box.png').convert_alpha(),
            SOKOBAN.TARGET: ground,
            # target overlay
            SOKOBAN.TARGETOVER: pygame.image.load('assets/images/target.png').convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load('assets/images/box_correct.png').convert_alpha(),
            SOKOBAN.PLAYER: pygame.image.load('assets/images/player_sprites.png').convert_alpha(),
            SOKOBAN.GROUND: ground
        }

        def surfhigh (color, alpha):
            surf = pygame.Surface((SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))
            surf.set_alpha(alpha)
            surf.fill(color) # green highlight
            return surf

        # small surfaces to draw attention to a particular tile of the board
        # e.g., to highlight a tile
        surfAtt  = surfhigh((0,255,0),50) # green highlight, for attainable tiles
        surfSucc = surfhigh((0,0,255),50) # blue highlight,  to show successors of boxes
        surfSelect= surfhigh((255,255,0),200) # yellow highlight, to show selection
        surfError = surfhigh((255,0,0),200) # red highlight, in case of an error

        self.highlights = {
                SOKOBAN.HATT:   surfAtt,
                SOKOBAN.HSUCC:  surfSucc,
                SOKOBAN.HSELECT:surfSelect,
                SOKOBAN.HERROR :surfError,
                }

    def load_level(self, nextLevel=False, prevLevel=False):
        """
        load (or reload) current level or previous/next level
        Return True on success and False if it was not possible to load a level.
        """
        if nextLevel:
            self.index_level += 1
        if prevLevel:
            self.index_level -= 1

        self.level.load(self.index_level)

        if not self.level.loaded:
            ## We tried to load past the last available level
            print ("Plus de niveau disponible")
            self.interface.display_info("Plus de niveau disponible", error=True)
            self.interface.txtInfo.render(self.window)
            self.wait_key(update=False)
            return False

        assert(self.interface)

        self.playing = True
        # connect interface to level
        self.interface.set_level(
                self.level,
                self.index_level,
                self.level.title)

        # space to draw the level
        self.board = pygame.Surface((self.level.width, self.level.height))
        if self.player:
            self.interface.level = self.level
            self.player.level = self.level
        else:
            self.player = Player(self, self.level)

        return True

    def start(self):
        """
        main loop of  the game
        """
        loaded = self.load_level(nextLevel=True)
        if not loaded: return

        # code to test performance: compute the number of frames per second 
        # (FPS)
        self.clock = pygame.time.Clock()
        q = Queue(maxsize=1000)
        self.clock.tick()
        total_time=0
        fps_message="{fps:.2f} fps"

        # main loop
        while self.playing:
            self.update_screen()
            self.process_event(pygame.event.wait())

            # new frame: store number of milliseconds passed since previous call
            t = self.clock.tick()
            total_time += t
            q.put(t)
            if q.qsize() >= 60:
                l = q.get()
                total_time -= l
                fps = 60 / total_time * 1000
                print(fps_message.format(fps=fps), total_time, end="\r")


    def toggle_visualize(self):
        """
        Activate/deactivate visual mode:
        - mark ATT the attainable squares (without pushing any box)
        - mark SUCC the position where a box can be pushed
        """
        self.has_changed = True
        self.visual = not(self.visual)
        if not self.visual:
            # disable highlighted tiles if going out of visual aid
            self.level.reset_highlight()



    def animate_move_to(self, position):
        """
        Move the character to 'position' by computing the shortest path
        then moving it along the path.
        """
        path = self.level.path_to(position)
        if not path: return

        # speed up movement
        save_anim=S.MOVE_FRAMES
        S.MOVE_FRAMES=1

        for d in path:
            # simulate key presses
            key = DIRKEY[d]
            self.move_player(key)

            self.update_screen()
            pygame.time.wait(SOKOBAN.MOVE_DELAY)

        # restore movement speed
        S.MOVE_FRAMES=save_anim


    def animate_move_boxes(self, path, skip_last=False, fast=True):
        self.level.invalidate()

        for last,(box,d) in islast(path):

            verbose ("now path is push", box, "from", SOKOBAN.DNAMES[d])
            pos = self.level.side_box(box, d)

            self.animate_move_to(pos)
            oppd = SOKOBAN.OPPOSITE[d]

            if not skip_last or not last:
                key = DIRKEY[oppd]
                self.move_player(key)

            self.update_screen()

            # new box position
            box = self.level.side_box(box, oppd)
            verbose ("New box position", box)

        if self.level.has_win():
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

    def cancel_move(self):
        remaining = self.level.cancel_last_change()
        if not remaining:
            self.interface.deactivate_cancel()




    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == KEYDOWN:
            self.cancel_selected()
            if event.key == K_ESCAPE:
                # Quit game
                self.playing = False
                return

            elif event.key in KEYDIR.keys():
                self.move_player(event.key, continue_until_released=True)

            elif event.key == K_n: # cheat key :-)
                ret = self.load_level(nextLevel=True)
                if not ret:
                    self.playing = False
                    return

            elif event.key == K_p: # back key
                self.load_level(prevLevel=True)

            elif event.key == K_r:
                # Restart current level
                self.load_level(nextLevel=False)

            elif event.key == K_v:
                # Vizualize possible moves
                self.toggle_visualize()

            elif event.key == K_c:
                # Cancel last move
                self.cancel_move()
                lost = self.level.lost_state()
                if lost:
                    verbose ("Still lost state !")
                self.interface.set_lost_state(lost)



            # "Test" key
            elif event.key == K_t:
                pass
                # path = self.level.move_one_box((8, 3), (4, 3))
                # if not path:
                    # self.flash_screen((8,3))
                # else:
                    # self.animate_move_boxes(path)

            # "all box solve" key
            elif event.key == K_a:
                self.interface.set_solving(True, num=0)
                found,message,path = self.level.solve_all_boxes()
                if not found:
                    self.interface.set_solving(True,
                            message=message,
                            error=True
                            )
                    self.flash_screen()
                    self.update_screen()
                    self.wait_key()

                else:
                    self.interface.set_solving(True,
                            message=message,
                            error=False)
                    self.flash_screen(color=SOKOBAN.GREEN)
                    self.wait_key()
                    self.animate_move_boxes(path, skip_last=True, fast=False)

                self.interface.set_solving(False)

        elif event.type == MOUSEBUTTONDOWN:
            position = self.interface.click(event.pos, self.level)
            if position:
                self.click_pos(position)
            else:
                self.cancel_selected()

        elif event.type == MOUSEMOTION:
            self.interface.mouse_pos = event.pos
        # else:
            # print ("Unknown event:", event)
            #
            #


    def move_player(self, key, continue_until_released=False):
        """
        A direction key has been pressed.
        Move (or try to move) the player in this direction
        until the key is released
        """
        direction = KEYDIR[key]

        # Ask to move player
        status = self.player.start_move(direction)

        # after a box has been moved, the 'cancel' button becomes
        # available
        if self.level.has_cancelable():
            self.interface.activate_cancel()

        # move failed (e.g., character against a wall)
        if status == SOKOBAN.ST_IDLE:
            return

        # keep previous status to check if there is a win (only when status was 
        # 'pushing'
        prev_status = status

        # Move only one tile away, unless asked keep the motion going until key 
        # is released
        stop_next_tile = not continue_until_released

        # save one keydown event to have smooth turning
        save_event = None
        while True:
            # slows loop to target FPS
            t = self.clock.tick(SOKOBAN.TARGET_FPS)

            # if not stop_next_tile:
            # discard all events but:
            # quit
            # release of direction key
            # press of a new key (save it for later)
            while not stop_next_tile:
                event = pygame.event.poll()
                if event.type == NOEVENT: break
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == KEYDOWN:
                    save_event = event
                elif event.type == KEYUP:
                    if save_event is not None and event.key == save_event.key:
                        # the key saved is not pushed anymore
                        save_event = None

                    if event.key == key:
                        # keep moving but stop at next tile
                        stop_next_tile = True
                        if save_event is not None:
                            # put back the pressed key so it will be processed 
                            # by the main loop as soon as this function returns
                            pygame.event.post(save_event)
                        break

            on_tile = self.player.continue_move()

            if on_tile:
                if prev_status == S.ST_PUSHING:
                    # check if winable state
                    # before continuing
                    if self.level.has_win():
                        self.level_win()
                        return

                    # or if position is lost...
                    lost = self.level.lost_state()
                    if lost:
                        verbose ("Lost state !")
                    self.interface.set_lost_state(lost)

                # key not pressed anymore and finished arriving on the tile
                if stop_next_tile:
                    self.player.stop_move()
                    break

            prev_status = status
            status = self.player.status

            self.update_screen()


    def click_pos (self, position):
        if self.selected_position:
            postype, selpos = self.selected_position

            if postype == SOKOBAN.BOX:
                self.cancel_selected()

                self.interface.set_solving(True, num=0)

                # now try to move the box
                if position == selpos:
                    # same position: auto solving this box to a target
                    found,message,path = self.level.solve_one_box(selpos)
                else:
                    # different position: move the box to this area
                    found,message,path = self.level.move_one_box(selpos, position)

                self.interface.set_solving(True,
                        message=message,
                        error=not found
                    )

                if not path:
                    self.flash_screen(selpos)
                else:
                    self.animate_move_boxes(path)

                self.interface.set_solving(False)

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


    def wait_key(self, update=True):
        if update:
            self.update_screen()
        self.interface.show_press_key(self.window)
        pygame.display.flip()
        while True:
            event = pygame.event.wait()
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                break

    def check_cancel(self, message):
        self.interface.set_solving(True, message=message)
        self.interface.render(self.window, self.index_level, self.level)
        pygame.display.flip()
        event = pygame.event.poll()

        while event.type != NOEVENT:
            if event.type == KEYDOWN \
            and event.key == K_ESCAPE:
                self.interface.set_solving(False)
                return True
            event = pygame.event.poll()
        return False

    def update_screen(self, flip=True):
        # if not self.level.loaded: return

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
        self.origin_board = (pos_x_board, pos_y_board)
        self.window.blit(self.board, self.origin_board)


        self.interface.render(self.window, self.index_level, self.level)

        if flip:
            pygame.display.flip()

    def level_win(self):
        self.scores.save()
        self.update_screen(flip=False)
        self.interface.show_win(self.window, self.index_level)
        self.wait_key(update=False)

        self.load_level(nextLevel=True)


    def debug(self):
        self.update_screen()
        print ("Waiting for keypress...")
        self.wait_key()


