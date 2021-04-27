import pygame
import sys
import os
from pygame.locals import *
import constants as SOKOBAN
from level import *
from explore import *
from player import *
from scores import *
from interface import *
from queue import Queue
from random import randrange

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
        self.load_sounds()

        if continueGame:
            self.index_level = self.scores.last_level()
        else:
            self.index_level = 0

        self.interface = Interface(self)
        self.playing = False
        self.visual = False
        self.has_changed = False
        self.selected_position = None
        self.origin_board = (0,0)

    def load_textures(self):
        def fn(f):
            return os.path.join('assets', 'images', f)

        ground = pygame.image.load(fn('stoneCenter.png')).convert_alpha()

        self.textures = {
                SOKOBAN.ORIG_SPRITESIZE:
        {
            SOKOBAN.WALL: pygame.image.load(fn('wall.png')).convert_alpha(),
            SOKOBAN.BOX: pygame.image.load(fn('box.png')).convert_alpha(),
            SOKOBAN.TARGET: ground,
            # target overlay
            SOKOBAN.TARGETOVER: pygame.image.load(fn('target.png')).convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load(fn('box_correct.png')).convert_alpha(),
            SOKOBAN.PLAYER: pygame.image.load(fn('player_sprites.png')).convert_alpha(),
            SOKOBAN.GROUND: ground
        }
        }

        def surfhigh (size, color, alpha):
            surf = pygame.Surface((size, size))
            surf.set_alpha(alpha)
            surf.fill(color) # green highlight
            return surf

        # small surfaces to draw attention to a particular tile of the board
        # e.g., to highlight a tile
        surfAtt  = lambda s: surfhigh(s,(0,255,0),50) # green highlight, for attainable tiles
        surfSucc = lambda s: surfhigh(s,(0,0,255),50) # blue highlight,  to show successors of boxes
        surfSelect= lambda s: surfhigh(s,(255,255,0),200) # yellow highlight, to show selection
        surfError = lambda s: surfhigh(s,(255,0,0),200) # red highlight, in case of an error

        self.highlights = {}
        for s in SOKOBAN.SPRITESIZES:
            self.highlights[s] = {
                    SOKOBAN.HATT:   surfAtt(s),
                    SOKOBAN.HSUCC:  surfSucc(s),
                    SOKOBAN.HSELECT:surfSelect(s),
                    SOKOBAN.HERROR :surfError(s),
                    }

    def load_sounds(self):
        if not SOKOBAN.WITH_SOUND: return
        # pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, 
        # buffersize
        # pygame.mixer.pre_init(48000, 16, 2, 4096) #frequency, size, channels, buffersize
        # pygame.init() #turn all of pygame on.

        # filetest = 'assets/sounds/test.wav'
        # test = pygame.mixer.Sound(filetest)
        # for i in range(10):
            # print('playing')
            # test.play()
            # pygame.time.wait(test.duration())
            # pygame.time.wait(100)

        def fn(f):
            return os.path.join('assets', 'sounds', f)

        def ld(template,lst,num,volume):
            for i in range (num):
                f = fn(template.format(i))
                snd = pygame.mixer.Sound(f)
                snd.set_volume(volume)
                lst.append(snd)

        self.sndFootstep = []
        filetemplate = 'footstep-dirt-{:02d}.wav'
        ld(filetemplate, self.sndFootstep, SOKOBAN.SND_FOOTSTEP_NUM, .3)

        # self.sndWoodpush = []
        # filetemplate = 'wood-friction-{:02d}.wav'
        # ld(filetemplate, self.sndWoodpush, SOKOBAN.SND_WOODFRIC_NUM, .3)
        self.sndPushing = pygame.mixer.Sound(fn('wood-friction-sheyvan.wav'))

        self.footstep_idx = -1
        self.woodpush_idx = -1

        # self.sndPushing = pygame.mixer.Sound(fn('pushing-short.wav'))
        # self.sndPushing = pygame.mixer.Sound(fn('wood-friction.wav'))
        # self.sndPushing.set_volume(.08)
        self.channelPushing = None
        self.channelFootsteps = None

        self.sndWin = pygame.mixer.Sound(fn('jingle-win.wav'))
        self.sndWin.set_volume(.06)



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

        self.create_board()


        if self.player:
            self.interface.level = self.level
            self.player.level = self.level
        else:
            self.player = Player(self, self.level)

        # scales textures to current spritesize if necessary
        self.update_textures()
        self.player.update_textures()

        sc = self.scores.get()
        self.interface.best_moves(sc)

        return True

    def create_board(self):
        # determine size of level on screen
        max_height = SOKOBAN.WINDOW_HEIGHT - 120
        max_width  = SOKOBAN.WINDOW_WIDTH - 2*BORDER

        max_sprite_size = min(
                max_height / self.level.height,
                max_width / self.level.width
                )

        # print ('could use sprite size', max_sprite_size)
        sp = int(max_sprite_size / 4)*4
        sp = max(min(sp, 64), 16)
        verbose ('will use sprite size', sp)
        SOKOBAN.SPRITESIZE = sp

        # space to draw the level
        self.board = pygame.Surface((
            self.level.width * SOKOBAN.SPRITESIZE,
            self.level.height * SOKOBAN.SPRITESIZE))


    def update_textures(self):
        if SOKOBAN.SPRITESIZE not in self.textures:
            sp = SOKOBAN.SPRITESIZE
            self.textures[sp] = {}
            for key, texture in self.textures[SOKOBAN.ORIG_SPRITESIZE].items():
                sc = pygame.transform.smoothscale(texture, (sp, sp))
                self.textures[sp][key] = sc


    def sound_play_footstep(self):
        if not SOKOBAN.WITH_SOUND: return
        if self.channelFootsteps is not None:
            if self.channelFootsteps.get_busy():
                return
        # self.footstep_idx += 1
        # self.footstep_idx %= SOKOBAN.SND_FOOTSTEPNUM
        self.footstep_idx = randrange(SOKOBAN.SND_FOOTSTEP_NUM)
        self.channelFootsteps = self.sndFootstep[self.footstep_idx].play()


    def sound_play_pushing(self):
        if not SOKOBAN.WITH_SOUND: return
        # check if previous sound is still playing
        if self.channelPushing is not None:
            if self.channelPushing.get_busy():
                return
        self.channelPushing = self.sndPushing.play() #0,1000)

        # self.woodpush_idx = randrange(SOKOBAN.SND_WOODFRIC_NUM)
        # self.channelPushing = self.sndWoodpush[self.woodpush_idx].play()


    def sound_play_win(self):
        if not SOKOBAN.WITH_SOUND: return
        self.sndWin.play()







    def start(self):
        """
        main loop of  the game
        """
        loaded = self.load_level(nextLevel=True)
        if not loaded: return

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
            self.clock.tick() # should be called once per frame

            # new frame: store number of milliseconds passed since previous call
            # total_time += t
            # q.put(t)
            # if q.qsize() >= 60:
                # l = q.get()
                # total_time -= l
                # fps = 60 / total_time * 1000
                # print(fps_message.format(fps=fps), total_time, end="\r")


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
        """
        Moving a box automatically, following 'path' movements
        """
        self.level.invalidate()

        save_anim=SOKOBAN.MOVE_FRAMES
        SOKOBAN.MOVE_FRAMES=4

        for last,(box,d) in islast(path):

            verbose ("now path is push", box, "from", SOKOBAN.DNAMES[d])
            pos = self.level.side_box(box, d)

            # move character to the side of the box
            self.animate_move_to(pos)
            oppd = SOKOBAN.OPPOSITE[d]

            # now push dthe box
            if not skip_last or not last:
                key = DIRKEY[oppd]
                self.move_player(key)

            self.update_screen()

            # new box position
            box = self.level.side_box(box, oppd)

        SOKOBAN.MOVE_FRAMES=save_anim

        # check if last push triggered a win condition
        if self.level.has_win():
            self.level_win()



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
                return False

            elif event.key in KEYDIR.keys():
                self.move_player(event.key, continue_until_released=True)

            elif event.key == K_n: # cheat key :-)
                ret = self.load_level(nextLevel=True)
                if not ret:
                    self.playing = False
                    return  False

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
                    self.interface.flash_screen()
                    self.update_screen()
                    self.wait_key()

                else:
                    self.interface.set_solving(True,
                            message=message,
                            error=False)
                    self.interface.flash_screen(color=SOKOBAN.GREEN)
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
            # do not update screen after this event
            return False

        elif event.type == VIDEORESIZE:
            w,h = event.dict['size']
            SOKOBAN.WINDOW_WIDTH = w
            SOKOBAN.WINDOW_HEIGHT = h

            # need to recreate the window although the doc says it should be 
            # automatically updated
            self.window = pygame.display.set_mode((SOKOBAN.WINDOW_WIDTH, SOKOBAN.WINDOW_HEIGHT),RESIZABLE)
            self.create_board()
            self.update_textures()
            self.player.update_textures()
            self.interface.update_positions()



        return True


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

        is_win = False
        while True:
            if status == SOKOBAN.ST_PUSHING:
                self.sound_play_pushing()
            else:
                self.sound_play_footstep()

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
                        is_win = True
                        break

                    # or if position is lost...
                    lost = self.level.lost_state()
                    if lost:
                        verbose ("Lost state !")
                    self.interface.set_lost_state(lost)

                # key not pressed anymore and finished arriving on the tile
                if stop_next_tile:
                    self.player.stop_move()
                    break
                # otherwise, continue, and play new sound

            prev_status = status
            status = self.player.status

            self.update_screen()

        # stop sounds
        if self.channelFootsteps is not None:
            self.channelFootsteps.stop()
        if self.channelPushing is not None:
            self.channelPushing.stop()

        if is_win:
            self.level_win()

    def click_pos (self, position):
        if self.selected_position:
            postype, selpos = self.selected_position

            if postype == SOKOBAN.BOX:
                self.cancel_selected()

                # solving for only one box
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
                    self.interface.flash_screen(selpos)
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
        # clear screen
        self.window.fill(SOKOBAN.WHITE)
        self.board.fill(SOKOBAN.WHITE)

        self.level.render(self.board, self.textures[SOKOBAN.SPRITESIZE], self.highlights)
        self.player.render(self.board, self.textures[SOKOBAN.ORIG_SPRITESIZE])

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
        self.sound_play_win()
        self.update_screen(flip=False)
        self.interface.show_win(self.window, self.index_level)
        self.wait_key(update=False)

        self.load_level(nextLevel=True)


    def debug(self):
        self.update_screen()
        print ("Waiting for keypress...")
        self.wait_key()


