"""
The bulk of the game, this is where the sokoban levels are displayed
and the interaction with the user playing the level happens.
"""

import pygame
import sys
import os
from pygame.locals import *
import common as C
import scores as S
from graphics import *
from sounds import *
from level import *
from explore import *
import scores as S
from queue import Queue

# correspondance between keys on keyboard and direction in Sokoban
KEYDIR = {
    # regular arrow keys
    K_UP: C.UP,
    K_DOWN: C.DOWN,
    K_LEFT: C.LEFT,
    K_RIGHT: C.RIGHT,
    # classical on Azerty keyboard
    K_z: C.UP,
    K_s: C.DOWN,
    K_q: C.LEFT,
    K_d: C.RIGHT,
}

# Keyboard keys corresponding to move directions.
# Must be in the same order as DIRS in common.py
DIRKEY = [
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
]


class GameInterface:
    """
    Interface when playing the sokoban levels, with level title,
    number of moves, possibility to cancel. etc.
    """

    def __init__(self, game):
        self.game = game
        self.level = None
        self.mouse_pos = (-1, -1)
        self.font_messages = pygame.font.Font(
            os.path.join('assets', 'fonts', 'FreeSansBold.ttf'), 18)
        self.font_win = pygame.font.Font(
            os.path.join('assets', 'fonts', 'FreeSansBold.ttf'), 32)
        self.is_lost = False
        self.has_info = False
        self.is_solving = False
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
        self.deactivate_cancel()
        self.is_lost = False
        self.has_info = False
        self.is_solving = False

    def load_assets(self):
        self.txtPack = Text(
            S.scores.pack_name(),
            self.font_messages, C.BLUE, C.ALEFT, C.ATOP,
        )

        self.txtLevel = Text(
            "Niveau 1",
            self.font_messages, C.BLUE, C.ALEFT, C.ACUSTOM,
            below=self.txtPack
        )

        self.txtTitle = Text(
            " ",
            self.font_messages, C.BLUE, C.ALEFT, C.ACUSTOM,
            below=self.txtLevel
        )

        self.txtTitle.set_pos(below=self.txtLevel)

        self.txtCancel = Text(
            "Annuler le dernier coup (C)",
            self.font_messages, C.GREY, C.ARIGHT, C.ATOP,
            callback=self.game.cancel_move
        )

        self.txtReset = Text(
            "Recommencer le niveau (R)",
            self.font_messages, C.BLACK, C.ACENTER, C.ATOP,
            callback=self.game.load_level
        )

        self.txtTest = Text(
            "Test (T)",
            self.font_messages, C.BLACK, C.ALEFT, C.ABOTTOM,
            callback=self.game.test_move
        )

        # START_CUT
        self.txtVisu = Text(
            "Aide visuelle (V)",
            self.font_messages, C.BLACK, C.ALEFT, C.ACUSTOM,
            above=self.txtTest,
            callback=self.game.toggle_visualize
        )

        self.txtHelp = Text(
            "Aide sokoban (H) / Résolution complète (A)",
            self.font_messages, C.BLACK, C.ACENTER, C.ABOTTOM,
            callback=None
        )
        # END_CUT

        self.txtNext = Text(
            ">>",
            self.font_messages, C.BLACK, C.ARIGHT, C.AMID,
            callback=self.game.load_next
        )

        self.txtPrev = Text(
            "<<",
            self.font_messages, C.BLACK, C.ALEFT, C.AMID,
            callback=self.game.load_prev
        )

        self.txtMoves = Text(
            "Coups : 0",
            self.font_messages, C.BLACK, C.ARIGHT, C.ABOTTOM,
            callback=None
        )

        self.txtBestMoves = Text(
            "Meilleur : infini",
            self.font_messages, C.BLACK, C.ARIGHT, C.ACUSTOM,
            above=self.txtMoves,
            callback=None
        )

        self.txtWin = Text("Félicitations, niveau 1 terminé",
                           self.font_win, C.BLACK, C.ACENTER, C.ACUSTOM,
                           callback=None)
        self.txtWin.set_pos(below=self.txtReset)

        self.ymessages = 210

        self.txtPress = Text(
            "(appuyez sur une touche pour continuer)",
            self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
            below=self.txtWin,
            callback=None
        )

        # START_CUT
        self.txtLost = Text(
            "Résolution impossible (certaines boîtes sont définitivement coincées)",
            self.font_messages, C.RED, C.ACENTER, C.ACUSTOM,
            yfun=self.compute_ymessages,
            callback=None
        )

        self.txtResol = Text(
            "Résolution en cours (Esc pour annuler)",
            self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
            yfun=lambda: self.compute_ymessages() - 30,
            callback=None
        )
        # END_CUT

        self.txtInfo = Text(
            " ",
            self.font_messages, C.BLACK, C.ACENTER, C.ACUSTOM,
            yfun=self.compute_ymessages,
            callback=None
        )

        self.clickableTexts = [
            self.txtCancel,
            self.txtReset,
            self.txtTest,
            # START_CUT
            self.txtVisu,
            self.txtHelp,
            # END_CUT
            self.txtNext,
            self.txtPrev,
        ]

        self.always_texts = [
            self.txtPack,
            self.txtLevel,
            self.txtTitle,
            self.txtBestMoves,
        ] + self.clickableTexts

        self.all_texts = [
            self.txtInfo,
            # START_CUT
            self.txtLost,
            self.txtResol,
            # END_CUT
        ] +self.always_texts

    def compute_ymessages(self):
        return C.WINDOW_HEIGHT - 80

    def click(self, pos_click, level):
        # check if some text has been clicked
        for t in self.clickableTexts:
            if t.is_clicked(pos_click, do_callback=True):
                return None

        x, y = pos_click
        # check if clicked in the game
        origx, origy = self.game.origin_board
        if x > origx and x < origx + self.game.board.get_width() \
                and y > origy and y < origy + self.game.board.get_height():

            bx = (x - origx) // C.SPRITESIZE
            by = (y - origy) // C.SPRITESIZE

            return bx, by

    def show_win(self, window, levelNum):
        self.txtWin.render(window, "Félicitations, niveau " +
                           str(levelNum) + " terminé")

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
            message = "Résolution en cours, " + \
                str(num) + " états explorés (Esc pour annuler)"
        self.display_info(message, error)

    def flash_screen(self, pos=None, color=C.RED):
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

        for t in self.always_texts:
            t.render(window)

        # Text that needs to be updated first
        self.txtMoves.render(window, "Coups : " + str(level.num_moves))

        # Text that is not always present
        if self.has_info:
            self.txtInfo.render(window)

# STARD_CUT
        if self.is_lost:
            self.txtLost.render(window)
        if self.is_solving:
            self.txtResol.render(window)
# END_CUT


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
        self.character = None
        self.interface = None
        self.level = Level(
            self,
            S.scores.current_pack,  # filename
        )
        self.textures = Textures()
        self.sounds = Sounds()

        if not continueGame:
            S.scores.index_level = 1

        self.interface = GameInterface(self)
        self.playing = False
        self.visual = False
        self.has_changed = False
        self.selected_position = None
        self.origin_board = (0, 0)

    def load_next(self):
        self.load_level(nextLevel=True)

    def load_prev(self):
        self.load_level(prevLevel=True)

    def load_level(self, nextLevel=False, prevLevel=False):
        """
        load (or reload) current level or previous/next level
        Return True on success and False if it was not possible to load a level.
        """
        if nextLevel:
            S.scores.index_level += 1
        if prevLevel:
            if S.scores.index_level > 1:
                S.scores.index_level -= 1

        self.level.load(S.scores.index_level)

        if not self.level.loaded:
            # We tried to load past the last available level
            print("Plus de niveau disponible")
            self.interface.display_info(
                "Plus de niveau disponible", error=True)
            self.interface.txtInfo.render(self.window)
            self.wait_key(update=False)
            self.playing = False
            return False

        assert self.interface

        self.playing = True
        # connect interface to level
        self.interface.set_level(
            self.level,
            S.scores.index_level,
            self.level.title)

        self.create_board()

        if self.character:
            self.interface.level = self.level
            self.character.level = self.level
        else:
            self.character = Character(self, self.level)

        # scales textures to current spritesize if necessary
        self.textures.update_textures()
        self.character.update_textures()

        sc = S.scores.get()
        self.interface.best_moves(sc)

        return True

    def create_board(self):
        self.textures.compute_sprite_size(self.level.height, self.level.width)
        # surface to draw the level
        self.board = pygame.Surface((
            self.level.width * C.SPRITESIZE,
            self.level.height * C.SPRITESIZE))

    def start(self):
        """
        main loop of  the game
        """
        loaded = self.load_level()
        if not loaded:
            return

        # code to test performance: compute the number of frames per second
        # (FPS)
        self.clock = pygame.time.Clock()

        # q = Queue(maxsize=1000)
        # self.clock.tick()
        # total_time=0
        # fps_message="{fps:.2f} fps"

        # main loop
        while self.playing:
            ret = self.process_event(pygame.event.wait())
            if ret:
                self.update_screen()
            self.clock.tick()  # should be called once per frame

            # new frame: store number of milliseconds passed since previous call
            # total_time += t
            # q.put(t)
            # if q.qsize() >= 60:
            # l = q.get()
            # total_time -= l
            # fps = 60 / total_time * 1000
            # print(fps_message.format(fps=fps), total_time, end="\r")


# START_CUT
    def toggle_visualize(self):
        """
        Activate/deactivate visual mode:
        - mark ATT the attainable squares (without pushing any box)
        - mark SUCC the position where a box can be pushed
        """
        self.has_changed = True
        self.visual = not self.visual
        if not self.visual:
            # disable highlighted tiles if going out of visual aid
            self.level.reset_highlight()

    def animate_move_to(self, position):
        """
        Move the character to 'position' by computing the shortest path
        then moving it along the path.
        """
        path = self.level.path_to(position)
        if not path:
            return

        # speed up movement
        save_anim = C.MOVE_FRAMES
        C.MOVE_FRAMES = 1

        for d in path:
            # simulate key presses
            key = DIRKEY[d]
            self.move_character(key)

            self.update_screen()
            pygame.time.wait(C.MOVE_DELAY)

        # restore movement speed
        C.MOVE_FRAMES = save_anim

    def animate_move_boxes(self, path, skip_last=False, fast=True):
        """
        Moving a box automatically, following 'path' movements
        """
        self.level.invalidate()

        save_anim = C.MOVE_FRAMES
        C.MOVE_FRAMES = 4

        for last, (box, d) in islast(path):

            verbose("now path is push", box, "from", C.DNAMES[d])
            pos = self.level.side_box(box, d)

            # move character to the side of the box
            self.animate_move_to(pos)
            oppd = C.OPPOSITE[d]

            # now push dthe box
            if not skip_last or not last:
                key = DIRKEY[oppd]
                self.move_character(key)

            self.update_screen()

            # new box position
            box = self.level.side_box(box, oppd)

        C.MOVE_FRAMES = save_anim

        # check if last push triggered a win condition
        if self.level.has_win():
            self.level_win()
# END_CUT

    def cancel_selected(self):
        self.selected_position = None
        self.level.reset_highlight()

    def cancel_move(self):
        remaining = self.level.cancel_last_change()
        if not remaining:
            self.interface.deactivate_cancel()
# START_CUT
        lost = self.level.lost_state()
        if lost:
            verbose("Still lost state !")
        self.interface.set_lost_state(lost)
# END_CUT

    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == KEYDOWN:
            self.cancel_selected()
            if event.key == K_ESCAPE:
                # Quit game
                self.playing = False
                return False

            elif event.key in KEYDIR.keys():
                self.move_character(event.key, continue_until_released=True)

            elif event.key == K_n or event.key == K_GREATER:
                ret = self.load_level(nextLevel=True)

            elif event.key == K_p or event.key == K_LESS:
                self.load_level(prevLevel=True)

            elif event.key == K_r:
                # Restart current level
                self.load_level()

# START_CUT
            elif event.key == K_v:
                # Vizualize possible moves
                self.toggle_visualize()
# END_CUT

            elif event.key == K_c:
                # Cancel last move
                self.cancel_move()

            # "Test" key
            elif event.key == K_t:
                # Add code here that you would like to trigger with the 'T' key
                # For now, just move in a circle in the 'test_move' method
                self.test_move()

# START_CUT            #
            # "all box solve" key
            elif event.key == K_a:
                self.interface.set_solving(True, num=0)
                found, message, path = self.level.solve_all_boxes()
                if not found:
                    self.interface.set_solving(
                        True,
                        message=message,
                        error=True
                    )
                    self.interface.flash_screen()
                    self.update_screen()
                    self.wait_key()

                else:
                    self.interface.set_solving(
                        True,
                        message=message,
                        error=False
                    )
                    self.interface.flash_screen(color=C.GREEN)
                    self.wait_key()
                    self.animate_move_boxes(path, skip_last=True, fast=False)

                self.interface.set_solving(False)
# END_CUT
            else:
                verbose("Unbound key", event.key)

        elif event.type == MOUSEBUTTONDOWN:
            position = self.interface.click(event.pos, self.level)
            if position:
                self.click_pos(position)
            else:
                self.cancel_selected()

        elif event.type == MOUSEMOTION:
            self.interface.mouse_pos = event.pos
            # do not update screen after this event
            return False

        elif event.type == VIDEORESIZE:
            if pygame.event.peek(eventtype=VIDEORESIZE):
                return False

            w, h = event.dict['size']
            C.WINDOW_WIDTH = w
            C.WINDOW_HEIGHT = h

            # need to recreate the window although the doc says it should be
            # automatically updated
            self.window = pygame.display.set_mode(
                (C.WINDOW_WIDTH, C.WINDOW_HEIGHT), RESIZABLE)
            self.create_board()
            self.textures.update_textures()
            self.character.update_textures()
            self.interface.update_positions()

        return True

    def move_character(self, key, continue_until_released=False):
        """
        A direction key has been pressed.
        Move (or try to move) the character in this direction
        until the key is released
        """
        direction = KEYDIR[key]

        # Ask to move character
        status = self.character.start_move(direction)

        # after a box has been moved, the 'cancel' button becomes
        # available
        if self.level.has_cancelable():
            self.interface.activate_cancel()

        # move failed (e.g., character against a wall)
        if status == C.ST_IDLE:
            return

        # keep previous status to check if there is a win (only when status was
        # 'pushing'
        prev_status = status

        # Move only one tile away, unless asked keep the motion going until key
        # is released
        stop_next_tile = not continue_until_released
        # save one keydown event to have smooth turning
        save_event = None

        is_win = False
        while True:
            if status == C.ST_PUSHING:
                self.sounds.play_pushing()
            else:
                self.sounds.play_footstep()

            # slows loop to target FPS
            t = self.clock.tick(C.TARGET_FPS)

            # if not stop_next_tile:
            # discard all events but:
            # - quit
            # - release of direction key
            # - press of a new key (save it for later)
            while not stop_next_tile:
                event = pygame.event.poll()
                if event.type == NOEVENT:
                    break
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

            on_tile = self.character.continue_move()

            if on_tile:
                if prev_status == C.ST_PUSHING:
                    # check if winable state
                    # before continuing
                    if self.level.has_win():
                        is_win = True
                        break

# START_CUT
                    # or if position is lost...
                    lost = self.level.lost_state()
                    if lost:
                        verbose("Lost state !")
                    self.interface.set_lost_state(lost)
# END_CUT

                # key not pressed anymore and finished arriving on the tile
                if stop_next_tile:
                    self.character.stop_move()
                    break
                # otherwise, continue, and play new sound

            prev_status = status
            status = self.character.status

            self.update_screen()

        # stop sounds
        self.sounds.stop_move_push()

        if is_win:
            self.level_win()

    def click_pos(self, position):
        if self.selected_position:
            postype, selpos = self.selected_position

            if postype == C.BOX:
                self.cancel_selected()

# START_CUT
                # solving for only one box
                self.interface.set_solving(True, num=0)

                # now try to move the box
                if position == selpos:
                    # same position: auto solving this box to a target
                    found, message, path = self.level.solve_one_box(selpos)
                else:
                    # different position: move the box to this area
                    found, message, path = self.level.move_one_box(
                        selpos, position)

                self.interface.set_solving(
                    True,
                    message=message,
                    error=not found
                )

                if not path:
                    self.interface.flash_screen(selpos)
                else:
                    self.animate_move_boxes(path)

                self.interface.set_solving(False)
# END_CUT

            else:
                # now we should only select boxes
                assert false
            return

        # nothing selected yet
        if self.level.has_box(position):
            # selecting a box
            self.selected_position = (C.BOX, position)
            self.level.highlight([position], C.HSELECT)
        else:
            verbose("position selected, what now?")
# START_CUT
            # trying to move the character
            self.animate_move_to(position)
# END_CUT


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
        """
        Can be used in a long calculation to check
        whether the user pressed 'Escape'
        """
# START_CUT
        self.interface.set_solving(True, message=message)
# END_CUT
        self.interface.render(self.window, S.scores.index_level, self.level)
        pygame.display.flip()
        event = pygame.event.poll()

        # absorb all events but escape
        while event.type != NOEVENT:
            if event.type == KEYDOWN \
                    and event.key == K_ESCAPE:
                # do something here to cancel calculation
# START_CUT
                self.interface.set_solving(False)
# END_CUT
                return True
            event = pygame.event.poll()
        return False

    def update_screen(self, flip=True):
        # clear screen
        self.window.fill(C.WHITE)
        self.board.fill(C.WHITE)

        self.level.render(
            self.board,
            self.textures.get(C.SPRITESIZE),
            self.textures.highlights
        )
        self.character.render(self.board)

        if self.has_changed:
            self.has_changed = False
            if self.visual:
                self.level.update_visual()

        pos_x_board = (C.WINDOW_WIDTH // 2) - (self.board.get_width() // 2)
        pos_y_board = (C.WINDOW_HEIGHT // 2) - (self.board.get_height() // 2)
        self.origin_board = (pos_x_board, pos_y_board)
        self.window.blit(self.board, self.origin_board)

        self.interface.render(self.window, S.scores.index_level, self.level)

        if flip:
            pygame.display.flip()

    def level_win(self):
        S.scores.update(self.level.num_moves)
        self.sounds.play_win()
        self.update_screen(flip=False)
        self.interface.show_win(self.window, S.scores.index_level)
        self.wait_key(update=False)

        self.load_level(nextLevel=True)

    def debug(self):
        self.update_screen()
        print("Waiting for keypress...")
        self.wait_key()

    def test_move(self):
        """
        "automated" movement: pretend the user has pressed a direction key
        on the keyboard.
        Here we move up, right, down, then left
        """
        for m in [C.UP, C.RIGHT, C.DOWN, C.LEFT]:
            key = DIRKEY[m]
            self.move_character(key)
