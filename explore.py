import pygame
from pygame.locals import *
import common as C
from utils import *
import queue
import heapq
from time import time
from math import sqrt


class DFS:
    """
    Classical Depth-First Search walkthrough of the level to discover what is 
    the "interior" and "exterior.
    """
    def __init__(self, level):
        self.level = level

    def search_floor (self, source):
        init_x, init_y = source

        # to remember which tiles have been visited or not
        mark =  [[False for x in range(self.level.width)] for y in range(self.level.height)]

        def rec_explore (position):
            x, y = position
            if mark[y][x]:
                return

            # mark current position as visited
            mark[y][x] = True

            for d,(mx,my) in enumerate(C.DIRS):
                if self.level.is_wall((x+mx,y+my)):
                    continue

                rec_explore ((x+mx,y+my))

        rec_explore (source)
        return mark


# START_CUT
class Dijkstra:
    def __init__(self, level):
        self.level = level
        self.marks = None
        self.preds = None
        self.att_list = None
        self.dist = None

    def attainable (self, source, boxes_block = True):
        init_x, init_y = source

        allowed = [C.GROUND, C.TARGET, C.AIR]

        fifo = queue.Queue()
        fifo.put (source)

        mark =  [[False for x in range(self.level.width)] for y in range(self.level.height)]
        pred =  [[None for x in range(self.level.width)] for y in range(self.level.height)]
        dist =  [[-1 for x in range(self.level.width)] for y in range(self.level.height)]
        mark[init_y][init_x] = True

        dist[init_y][init_x] = 0

        att = [source]

        while not fifo.empty():
            x,y = fifo.get()
            curdist = dist[y][x]

            for d,(mx,my) in enumerate(C.DIRS):
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


MSG_SOLVE = "Explorés: {exp}     Temps: {el:.2f}s     Vitesse: {sp:.2f} états/s"

class Deadlocks:
    """
    Searches for deadlock tiles, i.e., tiles where a box cannot
    reach any target anymore.
    """
    def __init__(self, level):
        self.level = level

    def compute(self):

        # will mark as "reverse-attainable" tiles
        # consider all tiles as dead, then unmark them if they are
        # reversed-attainable
        dead =  [[True for x in range(self.level.width)] for y in range(self.level.height)]

        # lifo would just do also fine here
        fifo = queue.Queue()
        for t in self.level.targets:
            fifo.put(t)
            x,y = t
            dead[y][x] = False

        while not fifo.empty():
            t = fifo.get()

            # check all neighbours
            for d in range(C.NUMDIRS):
                n = in_dir(t,d)
                x,y=n
                if self.level.is_wall(n): continue
                if not dead[y][x]: continue # already visited
                n2 = in_dir(t,d,dist=2)
                if self.level.is_wall(n2): continue

                # otherwise, possible to push a box from n using n2
                fifo.put(n)
                dead[y][x] = False

        # now unmarked tiles are deadlocks
        self.dead = dead
        return dead









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
            for y in reversed(range(self.level.height)):
                for x in reversed(range(self.level.width)):
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

    def reset_level_state(self, state):
        """
        remove boxes based on list
        """
        _, boxes, _ = state
        for x,y in boxes:
            self.level.mboxes[y][x] = False


    def set_level_state(self, state):
        _, boxes, player = state
        for x,y in boxes:
            self.level.mboxes[y][x] = True

        self.level.boxes = list(boxes)
        self.boxlist=self.level.boxes
        self.level.set_player(player)
        self.level.invalidate()
        self.level.box_attainable_sides(self.boxlist)


    def acceptable_state(self, state):
        _, boxes, player = state

        if not self.dest is None:
            box = boxes[0]
            return box == self.dest

        # otherwise, check all boxes are on targets
        for box in boxes:
            if not self.level.is_target(box):
                return False
        return True

    def lost_state(self, state):
        (mapboxes, _), boxes, _ = state
        return self.level.lost_state(mapboxes, boxes)



    def solve(self):
        """
        Tries find a series of movements to move box from source to dest without 
        moving other boxes
        """

        if self.dest != None and not self.level.is_empty(self.dest):
            return (False, "Destination impossible", None)

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

        # clear existing boxes
        for x,y in self.boxlist:
            assert (self.level.mboxes[y][x])
            self.level.mboxes[y][x] = False


        # explore neighbouring states
        # for now, no weight

        prioqueue = [(0,0,init_state)]
        heapq.heapify(prioqueue)

        found = None
        cancelled = False

        states_explored = 0

        start_time = time()

        while not found and prioqueue != []:
            _, dist, state = heapq.heappop(prioqueue)
            s_hash, s_boxes, s_player = state
            verbose ("Looking for successors of boxes:", s_boxes, "player:", s_player, "distance:", dist)

            data = states[s_hash]
            self.set_level_state(state)

            states_explored += 1

            if states_explored % 31 == 0:
                if states_explored % 155 == 0:
                    self.level.game.update_screen()

                # update text and check cancel
                elapsed = time() - start_time
                speed = states_explored/elapsed

                message = MSG_SOLVE.format(exp=states_explored, el=elapsed, sp=speed)
                cancelled = self.level.game.check_cancel(message)
                if cancelled: break

            # self.level.game.debug()
            # Search for all successor states of current state
            succs = self.successor_states(state)

            for st,(box,direct),moves in succs:
                sthash, stboxes, player = st
                # print ("retrieved succ:", st)
                verbose ("\tsuc: b:", box, "d:", C.DNAMES[direct], "m:",moves)

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
            self.reset_level_state(state)

        if not found:
            path = None
            if cancelled:
                message = "Annulée après exploration de "+str(states_explored)+\
                " états"
            else:
                message = "Échouée après exploration de "+str(states_explored)+\
                " états (aucune solution possible)"
        else:
            # create path
            path = self.path_from(init_state, found, states)
            elapsed = time() - start_time
            message = "Solution trouvée après exploration de "+str(states_explored)+ " états en " \
                    + str(round(elapsed,1)) + " secondes"


        # restore level
        self.level.restore_state(self.save_state)

        self.final_state = found
        self.path = path

        return (found, message, path)

    def improve(self):
        # trying to improve final state if only one box by pushing it as much 
        # as we can
        sthash, stboxes, player = self.final_state
        assert (len(stboxes) == 1)
        assert (self.path is not None)

        # find last push direction
        (box,d) = self.path[-1]
        d = opposite(d)
        box = in_dir(box,d)
        assert (box == stboxes[0])

        sucbox = in_dir(box,d)
        while self.level.is_empty(sucbox) \
        and   self.level.is_target(sucbox):
            self.path.append((box,opposite(d)))
            box = sucbox
            sucbox = in_dir(box,d)

        # now see if it can be pushed on one side
        side = rotate(d)
        sideo = opposite(side)

        go = None
        if self.level.is_empty(in_dir(box,side)) \
        and self.level.is_empty(in_dir(box,sideo)):
            if self.level.is_target(in_dir(box,side)):
                go=side
            elif self.level.is_target(in_dir(box,sideo)):
                go=sideo

        if go is not None:
            d = go
            sucbox = in_dir(box,d)
            while self.level.is_empty(sucbox) \
            and   self.level.is_target(sucbox):
                self.path.append((box,opposite(d)))
                box = sucbox
                sucbox = in_dir(box,d)



    def manhattan(self, source, dest):
        sx,sy = source
        dx,dy = dest
        return abs(dx-sx) + abs(dy-sy)

    def heuristic(self, state):
        """
        Lower bound for approximated number of box movements for 
        A*: sum of all manhattan distances to random target
        """
        # just change to 0 to get Dijkstra
        # return 0
        _, sblist, _ = state

        hdist = 0
        surf = self.level.width * self.level.height
        for box in sblist:
            m =self.manhattan(box,self.target)

            # hdist += m*m  ## good for open levels
            # hdist += m
            # hdist += int(sqrt(m))

            # Trying special for labyrinth-like levels
            #
            heur = surf * m
            heur -= m*(m+1)//2
            hdist += heur

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
                    # self.level.dij.show_distances()
                    # print ('distance from', player, 'to', in_dir(box,d), C.DNAMES[d])
                    dist = self.level.dij.distance(in_dir(box,d))

                    stsuc = self.create_successor(box=opp, player=box) # player position will be at box current one
                    # print ('distance here:', dist)
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

        return list(reversed(path))

# END_CUT








