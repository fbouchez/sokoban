"""
Handling of sound effects
"""

import pygame
import os
import common as C
from random import randrange


class Sounds:

    def __init__(self):
        """
        load the different sound effects for the game
        - footstep when walking
        - wood friction when pushing a box
        - jingle win when a level is finished
        """
        if not C.WITH_SOUND:
            return

        def fn(f):
            return os.path.join('assets', 'sounds', f)

        def ld(template, lst, num, volume):
            for i in range(num):
                f = fn(template.format(i))
                snd = pygame.mixer.Sound(f)
                snd.set_volume(volume)
                lst.append(snd)

        self.sndFootstep = []
        filetemplate = 'footstep-dirt-{:02d}.wav'
        ld(filetemplate, self.sndFootstep, C.SND_FOOTSTEP_NUM, .3)

        self.sndWoodpush = []
        filetemplate = 'wood-friction-{:02d}.wav'
        ld(filetemplate, self.sndWoodpush, C.SND_WOODFRIC_NUM, .8)

        self.footstep_idx = -1
        self.woodpush_idx = -1

        self.channelPushing = None
        self.channelFootsteps = None

        self.sndWin = pygame.mixer.Sound(fn('jingle-win.ogg'))
        self.sndWin.set_volume(.06)

    def play_footstep(self):
        if not C.WITH_SOUND:
            return
        if self.channelFootsteps is not None:
            if self.channelFootsteps.get_busy():
                return
        self.footstep_idx = randrange(C.SND_FOOTSTEP_NUM)
        self.channelFootsteps = self.sndFootstep[self.footstep_idx].play()

    def play_pushing(self):
        if not C.WITH_SOUND:
            return
        # check if previous sound is still playing
        if self.channelPushing is not None:
            if self.channelPushing.get_busy():
                return
        self.woodpush_idx = randrange(C.SND_WOODFRIC_NUM)
        self.channelPushing = self.sndWoodpush[self.woodpush_idx].play()

    def play_win(self):
        if not C.WITH_SOUND:
            return
        self.sndWin.play()

    def stop_move_push(self):
        if not C.WITH_SOUND:
            return
        if self.channelFootsteps is not None:
            self.channelFootsteps.stop()
        if self.channelPushing is not None:
            self.channelPushing.stop()
