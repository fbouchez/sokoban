import pygame
import constants as S
from copy import deepcopy
from explore import *
from utils import *

class Level:
    def __init__(self, game, filename, single_file=True):
        self.game=game
        self.num_moves = 0
        self.dij = None
        self.filename = filename
        self.single_file        = single_file
        self.single_file_levels = []
        self.level_number = 0
        self.load_file()    # read whole file
        self.loaded = False # True when a level is loaded
        self.pushed_box = None

    def place_box(self, box):
        x,y=box
        self.mboxes[y][x] = True

    def clear_box(self, box):
        x,y=box
        self.mboxes[y][x] = False

    def set_player(self, p):
        verbose('player set at', p)
        self.player_position = p

    def parse_rows(self, rows, symbols):

        self.map = []
        max_width = 0
        self.boxes = []
        height = len(rows)

        for y in range(len(rows)):
            level_row = []
            if rows[y] == '':
                height -=1
                continue
            if len(rows[y]) > max_width:
                max_width = len(rows[y])

            for x in range(len(rows[y])):
                block = symbols.index(rows[y][x])
                level_row.append(block)

                if block == S.BOX:
                    level_row[-1] = S.GROUND
                    self.boxes.append((x,y))

                elif block == S.TARGET_FILLED:
                    level_row[-1] = S.TARGET
                    self.boxes.append((x,y))

                elif block == S.PLAYER:
                    level_row[-1] = S.GROUND
                    self.player_position = (x,y)

                elif block == S.PLAYER_ON_TARGET:
                    level_row[-1] = S.TARGET
                    self.player_position = (x,y)


            self.map.append(level_row)

        self.map_width =  max_width
        self.map_height = height

        for y in range(height):
            while len(self.map[y]) < max_width:
                self.map[y].append(S.AIR)



        # map of boxes
        self.mboxes = [[False for x in range(self.map_width)] for y in range(self.map_height)]
        for bx,by in self.boxes:
            self.mboxes[by][bx] = True


        verbose ("Level size: ", self.map_width, "x", self.map_height)
        verbose (self.map)
        verbose (self.mboxes)
        verbose (self.boxes)



    def load_file_by_file(self, levelnum, nextlevel=False):
        try:
            with open("assets/levels/level_" + str(levelnum) + ".txt") as level_file:
                rows = level_file.read().split('\n')
            self.parse_rows(rows, S.SYMBOLS_MODERN)
            return True
        except FileNotFoundError:
            return False


    def load_file(self):
        if not self.single_file:
            # will not read all files
            return

        verbose ('Reading file', self.filename)
        with open("assets/levels/" + self.filename) as level_file:
            rows = level_file.read().split('\n')
        num = 0
        lev = []
        current = []
        title = None

        for r in rows:
            if r == '':
                # end of level
                if current != []:
                    lev.append((title,current))
                    current = []
                    title = None
                continue

            if r[0] == ';':
                continue

            if r.startswith('Title: '):
                title=r[7:]

            # check if this is a valid line:
            # only blanks until a wall '#'
            h = r.find('#')
            if h == -1:
                continue
            valid=True
            for i in range(h):
                if r[i] != ' ':
                    valid=False
                    break
            if not valid:
                continue

            current.append(r) # row belongs to level

        self.single_file_levels = lev


    def load(self, levelnum):
        self.loaded=False
        if self.single_file_levels:

            if levelnum > len(self.single_file_levels):
                return False

            self.title, rows = self.single_file_levels[levelnum-1]
            self.parse_rows(rows, S.SYMBOLS_ORIGINALS)
        else:
            ret = self.load_file_by_file(levelnum=levelnum)
            if not ret:
                return False

        self.width = self.map_width * S.SPRITESIZE
        self.height = self.map_height * S.SPRITESIZE

        dij = Dijkstra(self)
        att = dij.attainable(self.player_position, boxes_block=False)
        for x,y in att:
            if self.map[y][x] == S.AIR:
                self.map[y][x] = S.GROUND

        # highlight on some tiles
        self.mhighlight = [[S.HOFF for x in range(self.map_width)] for y in range(self.map_height)]

        # no previous move to cancel
        self.state_stack = []
        self.num_moves = 0
        self.loaded=True
        return True

    def reset_highlight (self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.mhighlight[y][x] = S.HOFF


    def highlight (self, positions, htype=S.HATT):
        for x,y in positions:
            self.mhighlight[y][x] = htype

    def has_box (self, pos):
        x,y = pos
        return self.mboxes[y][x]

    def is_target (self, pos):
        x,y = pos
        return self.map[y][x] in [S.TARGET, S.TARGET_FILLED]

    def is_wall (self, pos):
        x,y = pos
        return self.map[y][x] == S.WALL



    def is_empty (self, pos):
        x,y = pos
        return self.map[y][x] in [S.GROUND, S.TARGET, S.PLAYER] \
                and not self.has_box(pos)


    def lost_state(self, mboxes=None, boxlist=None):
        # print ("nothing special")
        if mboxes is None:
            mboxes = self.mboxes
        if boxlist is None:
            boxlist = self.boxes

        def is_full(p):
            x,y=p
            return self.is_wall(p) or mboxes[y][x]


        # check if some boxes are in wall corners
        for box in boxlist:
            # print ('cheking', box)
            # disp = False
            # if box == (10,5):
                # disp=True
                # print ("TESTISANOGEU")

            if self.is_target(box): continue
            prev = False
            for d in S.AROUND:
                # if disp:
                    # print ("cheking", S.DNAMES[d])
                side = in_dir(box, d)
                blocked = self.is_wall(side)
                if prev and blocked:
                    return True
                # WARNING: do not check with has_box, since it may be on 
                # a different state of boxes
                x,y = side
                if mboxes[y][x]:
                    # if disp:
                        # print ("there is a box copain", x,y)
                    # check if close to a wall
                    if horizontal(d):
                        d1 = S.UP
                        d2 = S.DOWN
                    else:
                        d1 = S.LEFT
                        d2 = S.RIGHT
                        # check above and below
                    ub = in_dir(box, d1)
                    us = in_dir(side,d1)
                    db = in_dir(box, d2)
                    ds = in_dir(side,d2)
                    if is_full(ub) and is_full(us)\
                    or is_full(db) and is_full(ds):
                        return True

                prev = blocked


        return False



    def get_current_state(self):
        return { 'mboxes': deepcopy(self.mboxes),
                 'player': self.player_position,
                 'moves' : self.num_moves
                 }

    def restore_state(self, state):
        self.mboxes = state['mboxes']
        self.update_box_positions()
        self.player_position = state['player']
        self.num_moves = state['moves']
        self.invalidate()

    def push_state(self):
        self.state_stack.append(self.get_current_state())


    def move_player (self, direction):
        x,y = self.player_position
        move_x, move_y = direction

        # print ("trying to move", x,"x",y," in direction",direction)

        player_status  = S.ST_IDLE

        xx = x+move_x
        yy = y+move_y
        xx2 = x+2*move_x
        yy2 = y+2*move_y

        if xx < 0 or xx >= self.map_width or\
           yy < 0 or yy >= self.map_height:
               return

        if self.is_empty((xx,yy)):
            # Player just moved on an empty cell
            self.player_position = (xx,yy)
            player_status  = S.ST_MOVING

        elif self.has_box((xx,yy)) and self.is_empty((xx2,yy2)):
            # Player is trying to push a box
            self.pushed_box = (xx2,yy2)

            player_status  = S.ST_PUSHING

            # Save current state
            self.push_state()

            boxi = self.boxes.index((xx,yy))
            self.boxes[boxi] = (xx2,yy2)

            self.mboxes[yy][xx] = False
            self.mboxes[yy2][xx2] = True

            self.player_position = (xx,yy)

        if player_status != S.ST_IDLE:
            self.invalidate()
            self.num_moves += 1

        return player_status

    def hide_pushed_box(self):
        x,y = self.pushed_box
        self.mboxes[y][x] = False

    def show_pushed_box(self):
        x,y = self.pushed_box
        self.mboxes[y][x] = True



    def compute_attainable(self,virtual=False):
        if virtual:
            locdij = Dijkstra(self)
            locdij.attainable(self.player_position)
            return locdij.get_marks()

        if not self.dij:
            self.dij = Dijkstra(self)
            self.dij.attainable(self.player_position)
            return self.dij.get_marks()

    def box_attainable_sides(self, boxlist, virtual=False):
        """
        if virtual, do not erase existing Dijkstra calculation
        """

        mark = self.compute_attainable(virtual)
        l = []
        for bx,by in boxlist:
            sides = [False for d in S.DIRS]
            for d,(mx,my) in enumerate(S.DIRS):
                if mark[by+my][bx+mx]:
                    sides[d] = True
            l.append(tuple(sides))
        return tuple(l)



    def compute_box_successors(self, boxpos):
        assert(self.has_box(boxpos))

        self.compute_attainable()
        mark = self.dij.get_marks()
        succ = []
        bx,by = boxpos
        for mx,my in S.DIRS:
            if mark[by+my][bx+mx] \
            and self.is_empty((bx-mx, by-my)):
                # side is attainable
                # and opposite side is free
                succ.append((bx-mx, by-my))
        return succ



    def compute_boxes_successors(self):
        self.compute_attainable()
        mark = self.dij.get_marks()
        succ = []
        for bx,by in self.boxes:
            for mx,my in S.DIRS:
                if mark[by+my][bx+mx] \
                and self.is_empty((bx-mx, by-my)):
                    # side is attainable
                    # and opposite side is free
                    succ.append((bx-mx, by-my))
        return succ



    def path_to (self, pos):
        targetx, targety = pos
        self.compute_attainable()

        if not self.dij.is_marked((targetx,targety)):
            verbose ("area is not attainable...")
            return None

        path = self.dij.shortest_path(self.player_position, pos)
        return path

    def solve_all_boxes(self):
        verbose ("Solving for all boxes!")
        bs = BoxSolution(self, self.boxes)
        return bs.solve()


    def solve_one_box(self, source):
        verbose ("Moving one box from", source, "to any target")
        bs = BoxSolution(self, [source])
        return bs.solve()

    def move_one_box(self, source, dest):
        verbose ("Moving one box from", source, "to", dest)
        bs = BoxSolution(self, [source], dest=dest)
        return bs.solve()


    def side_box(self, box, d):
        bx,by = box
        mx,my = S.DIRS[d]
        return bx+mx,by+my



    def update_visual (self):
        self.reset_highlight()

        self.compute_attainable()

        self.highlight(self.dij.att_list, S.HATT)

        succ = self.compute_boxes_successors()
        self.highlight(succ, S.HSUCC)


    def invalidate(self):
        self.dij = None


    def update_box_positions(self):
        self.boxes = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.mboxes[y][x]:
                    self.boxes.append((x,y))


    def cancel_last_change(self):
        """
        Return True if there is still cancelable moves
        """

        if not self.state_stack:
            verbose ("No previous state")
            return False

        state = self.state_stack.pop()
        self.restore_state(state)
        return self.state_stack != []

    def has_cancelable(self):
        return self.state_stack != []


    def has_win(self):
        for b in self.boxes:
            if not self.is_target(b):
                return False
        return True


    def render(self, window, textures, highlights):

        for y in range(self.map_height):
            for x in range(self.map_width):
                pos = (x * S.SPRITESIZE, y * S.SPRITESIZE)

                if self.mboxes[y][x]:
                    if self.is_target((x,y)):
                        window.blit(textures[S.TARGET_FILLED], pos)
                    else:
                        window.blit(textures[S.BOX], pos)

                elif self.map[y][x] in textures:
                    window.blit(textures[self.map[y][x]], pos)
                    if self.is_target((x,y)):
                        window.blit(textures[S.TARGETOVER], pos)

                h = self.mhighlight[y][x]
                if h:
                    window.blit(highlights[h], pos)
