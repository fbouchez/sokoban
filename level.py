"""
Handles the reading of levels from pack files,
as well as the state of the level when playing the game
- map of whole level: floor, walls, targets
- player position
- position of boxes
"""

import os
import pygame
import common as C
from copy import deepcopy
from explore import *
from utils import *


class Level:
    """
    Store the internal state of a level
    """

    def __init__(self, game, filename):
        self.game = game
        self.num_moves = 0
# START_CUT
        self.dij = None
# END_CUT
        self.filename = filename
        self.level_lines = []
        self.level_number = 0
        self.load_file()    # read whole file
        self.loaded = False  # True when a level is loaded
        self.pushed_box = None

    def place_box(self, box):
        x, y = box
        self.mboxes[y][x] = True

    def clear_box(self, box):
        x, y = box
        self.mboxes[y][x] = False

    def set_player(self, p):
        verbose('player set at', p)
        self.player_position = p

    def parse_rows(self, rows, symbols):

        self.map = []
        max_width = 0
        self.boxes = []
        self.targets = []
        height = len(rows)

        for y in range(len(rows)):
            level_row = []
            if rows[y] == '':
                height -= 1
                continue
            if len(rows[y]) > max_width:
                max_width = len(rows[y])

            for x in range(len(rows[y])):
                block = symbols.index(rows[y][x])
                level_row.append(block)

                if block == C.BOX:
                    level_row[-1] = C.GROUND
                    self.boxes.append((x, y))

                elif block == C.TARGET:
                    self.targets.append((x, y))

                elif block == C.TARGET_FILLED:
                    level_row[-1] = C.TARGET
                    self.boxes.append((x, y))
                    self.targets.append((x, y))

                elif block == C.PLAYER:
                    level_row[-1] = C.GROUND
                    self.player_position = (x, y)

                elif block == C.PLAYER_ON_TARGET:
                    level_row[-1] = C.TARGET
                    self.targets.append((x, y))
                    self.player_position = (x, y)

            self.map.append(level_row)

        self.width = max_width
        self.height = height

        for y in range(height):
            while len(self.map[y]) < max_width:
                self.map[y].append(C.AIR)

        # map of boxes
        self.mboxes = [[False for x in range(self.width)]
                       for y in range(self.height)]
        for bx, by in self.boxes:
            self.mboxes[by][bx] = True

        verbose("Level size: ", self.width, "x", self.height)
        verbose(self.map)
        verbose(self.mboxes)
        verbose(self.boxes)

    def load_file(self):
        """
        Load a pack of sokoban levels.
        Does not create all levels but stores the corresponding lines so
        as to be able to load a particular level later.
        """

        verbose('Reading file', self.filename)
        with open(os.path.join('assets', 'levels', self.filename)) as level_file:
            # prefers that to readlines() as there is not trailing "\n"
            rows = level_file.read().splitlines()

        num = 0
        lev = []
        current = []
        title = None

        for r in rows:
            if r == '':
                # end of level
                if current != []:
                    lev.append((title, current))
                    current = []
                    title = None
                continue

            if r[0] == ';':
                continue

            if r.startswith('Title: '):
                title = r[7:]

            # check if this is a valid line:
            if not valid_soko_line(r):
                continue

            current.append(r)  # row belongs to level

        self.level_lines = lev

    def load(self, levelnum):
        self.loaded = False

        if levelnum > len(self.level_lines):
            return False

        self.title, rows = self.level_lines[levelnum-1]
        self.parse_rows(rows, C.SYMBOLS_ORIGINALS)

        # Use DFS to mark the interior floor as ground
        dfs = DFS(self)
        mark = dfs.search_floor(self.player_position)
        for y in range(self.height):
            for x in range(self.width):
                if mark[y][x]:
                    if self.map[y][x] == C.AIR:
                        self.map[y][x] = C.GROUND

# START_CUT        #
        # reset previous analyses
        self.dij = None

        # compute deadlocks
        self.compute_dead()

# END_CUT
        # highlight on some tiles
        self.mhighlight = [[C.HOFF for x in range(
            self.width)] for y in range(self.height)]

        # no previous move to cancel
        self.state_stack = []
        self.num_moves = 0
        self.loaded = True
        return True

    def reset_highlight(self):
        for y in range(self.height):
            for x in range(self.width):
                self.mhighlight[y][x] = C.HOFF

    def highlight(self, positions, htype=C.HATT):
        for x, y in positions:
            self.mhighlight[y][x] = htype

    # Some helper functions to check the state of a tile

    def has_box(self, pos):
        x, y = pos
        return self.mboxes[y][x]

    def is_target(self, pos):
        x, y = pos
        return self.map[y][x] in [C.TARGET, C.TARGET_FILLED]

    def is_wall(self, pos):
        x, y = pos
        return self.map[y][x] == C.WALL

    def is_floor(self, pos):
        x, y = pos
        return self.map[y][x] in [C.GROUND, C.TARGET, C.PLAYER]

    def is_empty(self, pos):
        return self.is_floor(pos) and not self.has_box(pos)

# START_CUT
    def is_dead(self, pos):
        x, y = pos
        return self.dead[y][x]

    def lost_state(self, mboxes=None, boxlist=None):
        """
        Some heuristics to determine if the level is now in an
        unsolvable state:
        - box along a unescapable wall without target
        - boxes forming a square
        - in general, box that can no longer reach any target
        """
        if mboxes is None:
            mboxes = self.mboxes
        if boxlist is None:
            boxlist = self.boxes

        def is_full(p):
            x, y = p
            return self.is_wall(p) or mboxes[y][x]

        # check if some boxes are in wall corners
        for box in boxlist:
            # print ('cheking', box)
            # disp = False
            # if box == (10,5):
            # disp=True
            # print ("TESTISANOGEU")

            if self.is_target(box):
                continue
            if self.is_dead(box):
                return True
            prev = False
            for d in C.AROUND:
                # if disp:
                # print ("cheking", C.DNAMES[d])
                side = in_dir(box, d)
                blocked = self.is_wall(side)
                if prev and blocked:
                    return True
                # WARNING: do not check with has_box, since it may be on
                # a different state of boxes
                x, y = side
                if mboxes[y][x]:
                    # if disp:
                    # print ("there is a box copain", x,y)
                    # check if close to a wall
                    if horizontal(d):
                        d1 = C.UP
                        d2 = C.DOWN
                    else:
                        d1 = C.LEFT
                        d2 = C.RIGHT
                        # check above and below
                    ub = in_dir(box, d1)
                    us = in_dir(side, d1)
                    db = in_dir(box, d2)
                    ds = in_dir(side, d2)
                    if is_full(ub) and is_full(us)\
                            or is_full(db) and is_full(ds):
                        return True

                prev = blocked

        return False
# END_CUT

    def get_current_state(self):
        return {'mboxes': deepcopy(self.mboxes),
                'player': self.player_position,
                'moves': self.num_moves,
                }

    def restore_state(self, state):
        self.mboxes = state['mboxes']
        self.update_box_positions()
        self.player_position = state['player']
        self.num_moves = state['moves']
# START_CUT
        self.invalidate()
# END_CUT

    def push_state(self):
        self.state_stack.append(self.get_current_state())

    def move_player(self, direction):
        """
        Update the internal state of the level after a player movement:
        position of the player and maybe a box has been moved.
        Return value:
        - ST_MOVING if the player is moving without pushing a box
        - ST_PUSHING if the payer is moving and pushing a box
        - ST_IDLE if the player is not moving (the move was illegal)
        """
        x, y = self.player_position
        move_x, move_y = direction

        # print ("trying to move", x,"x",y," in direction",direction)

        player_status = C.ST_IDLE

        xx = x+move_x
        yy = y+move_y
        xx2 = x+2*move_x
        yy2 = y+2*move_y

        if xx < 0 or xx >= self.width or\
           yy < 0 or yy >= self.height:
            return

        if self.is_empty((xx, yy)):
            # Player just moved on an empty cell
            self.player_position = (xx, yy)
            player_status = C.ST_MOVING

        elif self.has_box((xx, yy)) and self.is_empty((xx2, yy2)):
            # Player is trying to push a box
            self.pushed_box = (xx2, yy2)

            player_status = C.ST_PUSHING

            # Save current state
            self.push_state()

            boxi = self.boxes.index((xx, yy))
            self.boxes[boxi] = (xx2, yy2)

            self.mboxes[yy][xx] = False
            self.mboxes[yy2][xx2] = True

            self.player_position = (xx, yy)

        if player_status != C.ST_IDLE:
            # START_CUT
            self.invalidate()
# END_CUT
            self.num_moves += 1

        return player_status

    def hide_pushed_box(self):
        x, y = self.pushed_box
        self.mboxes[y][x] = False

    def show_pushed_box(self):
        x, y = self.pushed_box
        self.mboxes[y][x] = True


# START_CUT

    def compute_attainable(self, virtual=False):
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
        for bx, by in boxlist:
            sides = [False for d in C.DIRS]
            for d, (mx, my) in enumerate(C.DIRS):
                if mark[by+my][bx+mx]:
                    sides[d] = True
            l.append(tuple(sides))
        return tuple(l)

    def compute_box_successors(self, boxpos):
        assert(self.has_box(boxpos))

        self.compute_attainable()
        mark = self.dij.get_marks()
        succ = []
        bx, by = boxpos
        for mx, my in C.DIRS:
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
        for bx, by in self.boxes:
            for mx, my in C.DIRS:
                if mark[by+my][bx+mx] \
                        and self.is_empty((bx-mx, by-my)):
                    # side is attainable
                    # and opposite side is free
                    succ.append((bx-mx, by-my))
        return succ

    def path_to(self, dest):
        self.compute_attainable()
        if not self.dij.is_marked(dest):
            verbose("area is not attainable...")
            return None

        path = self.dij.shortest_path(self.player_position, dest)
        return path

    def solve_all_boxes(self):
        verbose("Solving for all boxes!")
        bs = BoxSolution(self, self.boxes)
        return bs.solve()

    def solve_one_box(self, source):
        verbose("Moving one box from", source, "to any target")
        bs = BoxSolution(self, [source])
        found, message, path = bs.solve()
        if path is not None:
            pass
            # trying to improve last steps
            bs.improve()
        return (found, message, bs.path)

    def move_one_box(self, source, dest):
        verbose("Moving one box from", source, "to", dest)
        bs = BoxSolution(self, [source], dest=dest)
        return bs.solve()

    def side_box(self, box, d):
        bx, by = box
        mx, my = C.DIRS[d]
        return bx+mx, by+my

    def compute_dead(self):
        self.dl = Deadlocks(self)
        self.dead = self.dl.compute()

    def update_visual(self):
        self.reset_highlight()

        self.compute_attainable()
        self.highlight(self.dij.att_list, C.HATT)

        succ = self.compute_boxes_successors()
        self.highlight(succ, C.HSUCC)

        for y in range(self.height):
            for x in range(self.width):
                if self.dead[y][x] and self.is_floor((x, y)):
                    self.highlight([(x, y)], C.HERROR)

    def invalidate(self):
        self.dij = None
# END_CUT

    def update_box_positions(self):
        self.boxes = []
        for y in range(self.height):
            for x in range(self.width):
                if self.mboxes[y][x]:
                    self.boxes.append((x, y))

    def cancel_last_change(self):
        """
        Return True if there is still cancelable moves
        """

        if not self.state_stack:
            verbose("No previous state")
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
        """
        Render the whole level.
        Some tiles might be highlighted.
        """

        for y in range(self.height):
            for x in range(self.width):
                pos = (x * C.SPRITESIZE, y * C.SPRITESIZE)

                if self.mboxes[y][x]:
                    if self.is_target((x, y)):
                        window.blit(textures[C.TARGET_FILLED], pos)
                    else:
                        window.blit(textures[C.BOX], pos)

                elif self.map[y][x] in textures:
                    window.blit(textures[self.map[y][x]], pos)
                    if self.is_target((x, y)):
                        window.blit(textures[C.TARGETOVER], pos)

                h = self.mhighlight[y][x]
                if h:
                    window.blit(highlights[C.SPRITESIZE][h], pos)
