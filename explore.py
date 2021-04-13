import pygame
from pygame.locals import *
import constants as SOKOBAN
import queue

class Dijkstra:
    def __init__(self, level):
        self.level = level
        self.marks = None
        self.preds = None

    def attainable (self, source, boxes_block = True):
        init_x, init_y = source

        allowed = [SOKOBAN.GROUND, SOKOBAN.TARGET, SOKOBAN.AIR]
        if not boxes_block:
            allowed += [SOKOBAN.BOX, SOKOBAN.TARGET_FILLED]

        fifo = queue.Queue()
        fifo.put (source)

        mark =  [[False for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        pred =  [[None for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        mark[init_y][init_x] = True

        att = [source]

        while not fifo.empty():
            x,y = fifo.get()
            for d,(mx,my) in enumerate(SOKOBAN.DIRS):
                if mark[y+my][x+mx]:
                    continue

                if self.level.structure[y+my][x+mx] not in allowed:
                    continue

                mark[y+my][x+mx] = True
                att.append ((x+mx,y+my))
                fifo.put ((x+mx,y+my))
                pred[y+my][x+mx] = ((x,y), (mx,my), d)

        self.marks = mark
        self.att_list = att
        self.preds = pred

        return att

    def is_marked(self, pos):
        x,y=pos
        return self.marks[y][x]

    def get_marks(self):
        return self.marks

    def shortest_path(self, source, dest):
        assert (self.marks)
        path = []
        current = dest
        # print ('source:', source, 'dest:', dest)
        while current != source:
            x,y = current
            # print ('path:', current)
            current,move,direct = self.preds[y][x]
            path.append(direct)

        # print ('path:', current)
        return reversed(path)

