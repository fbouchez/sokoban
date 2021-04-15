import pygame
from pygame.locals import *
import constants as SOKOBAN
import queue



class Dijkstra:
    def __init__(self, level):
        self.level = level
        self.marks = None
        self.preds = None
        self.att_list = None

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
                # print ('trying y:', y+my, 'x:', x+mx)
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
        print ('source:', source, 'dest:', dest)
        while current != source:
            x,y = current
            print ('path:', current)
            current,move,direct = self.preds[y][x]
            path.append(direct)

        # print ('path:', current)
        return reversed(path)


class BoxSolution:
    def __init__(self, level):
        self.level = level

    def solve(self, pos):
        """ Solve the sokoban for one box
        """
        pass


    def move(self, source, dest=None):
        """
        Tries find a series of movement to move box from source to dest without 
        moving other boxes
        """
        assert (self.level.is_box(source))

        if dest != None and not self.level.is_empty(dest):
            return None

        succ = self.level.compute_box_successors(source)
        if not succ:
            # box is not attainable
            return None

        # save current state of level w.r.t box & player
        saveplayer = self.level.position_player

        x,y = source
        save_box = self.level.structure[y][x] # can be either target or ground
        if save_box == SOKOBAN.BOX:
            self.level.structure[y][x] = SOKOBAN.GROUND
        elif save_box == SOKOBAN.TARGET_FILLED:
            self.level.structure[y][x] = SOKOBAN.TARGET
        else:
            raise ValueError("box problem")

        # self.level.dij = None



        # initial state: box + attainable sides
        sides = self.level.box_attainable_sides(source)

        init_state = (source, sides)
        print ('init state:', init_state)

        states = {init_state: 0}

        # explore neighbouring states
        # for now, no weight

        fifo = queue.Queue()
        fifo.put (init_state)


        found = None

        while not found and not fifo.empty():
            state = fifo.get()

            box, sides = state
            # print ("Looking for successors of", state)
            succs = self.successor_states(state)

            for d,s in succs:
                # print ("\t",d,s)
                if s not in states:
                    states[s] = (state,d) # previous state + direction player has to push the box
                    fifo.put (s)

                if not dest is None and self.state_is_dest(s, dest) \
                or dest is None and self.state_is_target(s):
                    # found destination !
                    found = s
                    break



        if not found:
            path = None
        else:
            # create path
            path = self.path_from(init_state, found, states)

        # restore level
        self.level.position_player = saveplayer 
        x,y = source
        self.level.structure[y][x] = save_box
        self.level.dij = None

        return path


    def state_is_dest(self, state, dest):
        pos,_ = state
        return pos == dest

    def state_is_target(self, state):
        pos,_ = state
        return self.level.is_target(pos)


    def successor_states(self, state):

        box, sides = state
        bx,by = box
        succs = []

        for d,(mx,my) in enumerate(SOKOBAN.DIRS):
            if sides[d]:
                # this side is reachable by player
                opposite = (bx-mx,by-my)
                if self.level.is_empty(opposite):
                    suc = self.create_successor(opposite, box) # player position will be at box current one
                    succs.append((d,suc)) # also store the direction used to push from
        return succs


    def create_successor(self, box, player):

        # x,y = player
        # saveplayer = self.level.structure[y][x]
        # self.level.structure[y][x] = SOKOBAN.PLAYER
        bx,by = box
        savebox = self.level.structure[by][bx]
        self.level.structure[by][bx] = SOKOBAN.BOX
        self.level.position_player = player


        self.level.dij = None
        sides = self.level.box_attainable_sides(box)

        # self.level.structure[y][x] = saveplayer
        self.level.structure[by][bx] = savebox

        return (box, sides)


    def path_from(self, source, dest, states):

        current = dest

        path = []

        while current != source:

            prev, d = states[current]
            path.append(d)
            current = prev

        return reversed(path)









