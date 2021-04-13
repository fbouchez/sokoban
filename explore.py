import pygame
from pygame.locals import *
import constants as SOKOBAN
import queue

class Dijkstra:
    def __init__(self, level):
        self.level = level

    def attainable (self, source, boxes_block = True):
        init_x, init_y = source

        allowed = [SOKOBAN.GROUND, SOKOBAN.TARGET, SOKOBAN.AIR]
        if not boxes_block:
            allowed += [SOKOBAN.BOX, SOKOBAN.TARGET_FILLED]

        fifo = queue.Queue()
        fifo.put (source)

        mark =  [[False for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        mark[init_y][init_x] = True

        att = [source]

        while not fifo.empty():
            x,y = fifo.get()
            for mx,my in SOKOBAN.DIRS:
                if mark[y+my][x+mx]:
                    continue

                if self.level.structure[y+my][x+mx] not in allowed:
                    continue

                mark[y+my][x+mx] = True
                att.append ((x+mx,y+my))
                fifo.put ((x+mx,y+my))

        return att, mark
