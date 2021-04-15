import pygame
from pygame.locals import *
import constants as SOKOBAN
from utils import *
import queue
import heapq



class Dijkstra:
    def __init__(self, level):
        self.level = level
        self.marks = None
        self.preds = None
        self.att_list = None
        self.dist = None

    def attainable (self, source, boxes_block = True):
        init_x, init_y = source

        allowed = [SOKOBAN.GROUND, SOKOBAN.TARGET, SOKOBAN.AIR]

        fifo = queue.Queue()
        fifo.put (source)

        mark =  [[False for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        pred =  [[None for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        dist =  [[-1 for x in range(self.level.map_width)] for y in range(self.level.map_height)]
        mark[init_y][init_x] = True

        dist[init_y][init_x] = 0

        att = [source]

        while not fifo.empty():
            x,y = fifo.get()
            curdist = dist[y][x]

            for d,(mx,my) in enumerate(SOKOBAN.DIRS):
                # print ('verbose y:', y+my, 'x:', x+mx)
                if mark[y+my][x+mx]:
                    continue

                if self.level.map[y+my][x+mx] not in allowed \
                or boxes_block and self.level.has_box((x+mx,y+my)):
                    continue

                mark[y+my][x+mx] = True
                dist[y+my][x+mx] = curdist+1

                att.append ((x+mx,y+my))
                fifo.put ((x+mx,y+my))
                pred[y+my][x+mx] = ((x,y), (mx,my), d)

        self.marks = mark
        self.att_list = att
        self.preds = pred
        self.dist = dist

        return att

    def is_marked(self, pos):
        x,y=pos
        return self.marks[y][x]

    def get_marks(self):
        return self.marks

    def distance(self, target):
        x,y = target
        d = self.dist[y][x]
        assert(d!=-1)
        return d

    def show_distances(self):
        for row in self.dist:
            print(row)



    def shortest_path(self, source, dest):
        assert (self.marks)
        path = []
        current = dest
        verbose ('source:', source, 'dest:', dest)
        while current != source:
            x,y = current
            verbose ('path:', current)
            current,move,direct = self.preds[y][x]
            path.append(direct)

        return reversed(path)


class BoxSolution:
    def __init__(self, level, boxlist, dest=None):
        self.level = level
        self.boxlist = boxlist
        # these are the boxes we are allowed to move
        # others are considered walls
        self.dest=dest
        if dest:
            self.target = dest # for manhattan heuristic
            assert (len(boxlist) == 1)
        else:
            # target on most on lower right corner
            for y in reversed(range(self.level.map_height)):
                for x in reversed(range(self.level.map_width)):
                    if self.level.is_target((x,y)):
                        self.target = (x,y)
                        return






    def save_level_state(self, boxes):
        self.saveplayer = self.level.position_player
        self.saveboxes = []

    def restore_level_state(self):
        self.level.position_player = self.saveplayer

        for (x,y),old in self.saveboxes:
            self.level.structure[y][x] = old

    def make_state(self):
        tboxes = tupleit(self.level.mboxes)
        tblist = tupleit(self.boxlist)

        # do not invalidate, but make 'virtual' dijkstra
        allsides = self.level.box_attainable_sides(self.boxlist, virtual=True)

        return ((tboxes, allsides), tblist, self.level.player_position)


    def set_level_state(self, state):
        (tboxes, allsides), tblist, player = state
        for y in range(self.level.map_height):
            for x in range(self.level.map_width):
                self.level.mboxes[y][x] = tboxes[y][x]
        self.level.boxes = list(tblist)
        self.boxlist=self.level.boxes
        self.level.set_player(player)
        self.level.invalidate()
        self.level.box_attainable_sides(self.boxlist)

        # find a random position for player
        # for i,s in enumerate(allsides):
            # for d,f in enumerate(s):
                # if f:
                    # b=tblist[i]
                    # p=in_dir(b,d)
                    # self.level.set_player(p)
                    # return
        # assert(False)

    def acceptable_state(self, state):
        (tboxes, allsides), tblist, player = state

        if not self.dest is None:
            box = tblist[0]
            return box == self.dest

        # otherwise, check all boxes are on targets
        for box in tblist:
            if not self.level.is_target(box):
                return False
        return True

    def lost_state(self, state):
        (tboxes, allsides), tblist, player = state
        return self.level.lost_state(tboxes, tblist)

    def solve(self):
        """
        Tries find a series of movements to move box from source to dest without 
        moving other boxes
        """
        for b in self.boxlist:
            assert (self.level.has_box(b))

        if self.dest != None and not self.level.is_empty(self.dest):
            return None

        # save current state of level w.r.t box & player
        self.save_state = self.level.get_current_state()

        # initial state: boxes + their attainable sides
        init_state = self.make_state()
        init_hash, init_boxes, init_player = init_state

        states = {}
        states[init_hash] = {
                'boxes': init_boxes,
                'prev' : None,
                'push' : (self.level.player_position, None) # box 'pushed' represents player
                }


        # explore neighbouring states
        # for now, no weight

        prioqueue = [(0,0,init_state)]
        heapq.heapify(prioqueue)

        found = None

        states_explored = 0

        while not found and prioqueue != []:
            _, dist, state = heapq.heappop(prioqueue)

            states_explored += 1

            s_hash, s_boxes, s_player = state

            verbose ("Looking for successors of boxes:", s_boxes, "player:", s_player, "distance:", dist)

            data = states[s_hash]

            if states_explored % 100 == 0:
                print ("states explored:", states_explored)
                self.level.game.update_screen()

            self.set_level_state(state)
            self.level.game.debug()

            succs = self.successor_states(state)




            for st,(box,direct),moves in succs:
                sthash, stboxes, player = st
                # print ("retrieved succ:", st)
                verbose ("\tsuc: b:", box, "d:", SOKOBAN.DNAMES[direct], "m:",moves)

                if sthash not in states:
                    states[sthash] = {
                            'boxes': stboxes,
                            'prev' : s_hash,
                            'push' : (box,direct), # so player is at box
                            }
                    # stores current box list +
                    # previous state + box player has to push & in which 
                    # direction box

                    if self.acceptable_state(st):
                        # found destination !
                        found = st
                        break
                    if self.lost_state(st):
                        # self.set_level_state(st)
                        # self.level.game.update_screen()
                        # self.level.game.wait_key()
                        continue

                    h = self.heuristic(st)

                    heapq.heappush (prioqueue, (dist+moves+h, dist+moves, st))

        if not found:
            path = None
        else:
            # create path
            path = self.path_from(init_state, found, states)

        # restore level
        self.level.restore_state(self.save_state)

        return path

    def manhattan(self, source, dest):
        sx,sy = source
        dx,dy = dest
        return abs(dx-sx) + abs(dy-sy)

    def heuristic(self, state):
        """
        Lower bound for approximated number of box movements for 
        A*: sum of all manhattan distances to random target
        """
        return 0
        _, sblist, _ = state

        hdist = 0
        for box in sblist:
            hdist += self.manhattan(box,self.target)
        return hdist





    def successor_states(self, state):

        (sboxes, allsides), sblist, splayer = state
        alls = []
        for i,b in enumerate(sblist):
            succs = self.successor_states_one_box(b, allsides[i], splayer)
            alls += succs
        return alls


    def successor_states_one_box(self, box, sides, player):
        box, sides
        bx,by = box
        succs = []

        for d,flag in enumerate(sides):
            if flag: # this side is reachable by player
                opp=in_opp_dir(box,d)
                if self.level.is_empty(opp):
                    self.level.dij.show_distances()
                    print ('distance from', player, 'to', in_dir(box,d), SOKOBAN.DNAMES[d])
                    dist = self.level.dij.distance(in_dir(box,d))

                    stsuc = self.create_successor(box=opp, player=box) # player position will be at box current one
                    print ('distance here:', dist)
                    succs.append((stsuc,(box,d),dist+1)) # also store the box & direction pushed from
        return succs


    def create_successor(self, box, player):
        """
        Create successor state, as if player has just pushed a box.
        Hence box is the new position, and player is where the box
        was before it was pushed.
        """

        # save current state
        saveplayer = self.level.player_position

        # prepare successor state
        self.level.place_box(box)
        self.level.clear_box(player)
        self.level.player_position = player


        boxi = self.boxlist.index(player)
        self.boxlist[boxi] = box

        st = self.make_state()

        # restore state
        self.level.player_position = saveplayer
        self.level.place_box(player)
        self.level.clear_box(box)
        self.boxlist[boxi] = player

        return st


    def path_from(self, source_state, found_state, states):

        source_hash, _, _ = source_state
        found_hash, _, _ = found_state

        current = found_hash

        path = []

        while current != source_hash:

            node = states[current]

            path.append(node['push'])
            current = node['prev']

        return reversed(path)









