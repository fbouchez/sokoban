import pygame
import constants as SOKOBAN
from copy import deepcopy
from explore import *
from utils import *

class Level:
    def __init__(self, game, level_to_load, levelstyle):
        self.game=game
        self.num_moves = 0
        self.dij = None
        self.single_file_levels = None
        self.level_number = 0
        self.boxes = []
        self.success = self.load(level_to_load, levelstyle)

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

                if block == SOKOBAN.BOX:
                    level_row[-1] = SOKOBAN.GROUND
                    self.boxes.append((x,y))

                elif block == SOKOBAN.TARGET_FILLED:
                    level_row[-1] = SOKOBAN.TARGET
                    self.boxes.append((x,y))

                elif block == SOKOBAN.PLAYER:
                    level_row[-1] = SOKOBAN.GROUND
                    self.player_position = (x,y)

            self.map.append(level_row)

        self.map_width =  max_width
        self.map_height = height

        for y in range(height):
            while len(self.map[y]) < max_width:
                self.map[y].append(SOKOBAN.AIR)



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
            self.parse_rows(rows, SOKOBAN.SYMBOLS_MODERN)
            return True
        except FileNotFoundError:
            return False


    def load_single_file(self, levelnum, nextlevel=True):
        if not self.single_file_levels:
            with open("assets/levels/" + SOKOBAN.SINGLE_FILE + ".txt") as level_file:
                rows = level_file.read().split('\n')
            num = 0
            lev = []
            cur = []

            for r in rows:
                if r == '': continue
                if r[0] == ';':
                    curnum = int(r[2:])
                    lev.append((curnum, cur))
                    cur = []
                else:
                    cur.append(r)

            self.single_file_levels = lev

        if levelnum > len(self.single_file_levels):
            return False

        num,rows = self.single_file_levels[levelnum-1]

        self.parse_rows(rows, SOKOBAN.SYMBOLS_ORIGINALS)
        return True


    def load(self, levelnum, levelstyle='single_file'):
        verbose ('Loading level', levelnum)
        if levelstyle == 'file_by_file':
            ret = self.load_file_by_file(levelnum=levelnum)
        elif levelstyle == 'single_file':
            ret = self.load_single_file(levelnum, nextlevel=False)

        if not ret:
            return False

        self.width = self.map_width * SOKOBAN.SPRITESIZE
        self.height = self.map_height * SOKOBAN.SPRITESIZE

        dij = Dijkstra(self)
        att = dij.attainable(self.player_position, boxes_block=False)
        for x,y in att:
            if self.map[y][x] == SOKOBAN.AIR:
                self.map[y][x] = SOKOBAN.GROUND

        # highlight on some tiles
        self.mhighlight = [[SOKOBAN.HOFF for x in range(self.map_width)] for y in range(self.map_height)]

        # no previous move to cancel
        self.state_stack = []
        return True

    def reset_highlight (self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.mhighlight[y][x] = SOKOBAN.HOFF


    def highlight (self, positions, htype=SOKOBAN.HATT):
        for x,y in positions:
            self.mhighlight[y][x] = htype

    def has_box (self, pos):
        x,y = pos
        return self.mboxes[y][x]

    def is_target (self, pos):
        x,y = pos
        return self.map[y][x] in [SOKOBAN.TARGET, SOKOBAN.TARGET_FILLED]

    def is_wall (self, pos):
        x,y = pos
        return self.map[y][x] == SOKOBAN.WALL



    def is_empty (self, pos):
        x,y = pos
        return self.map[y][x] in [SOKOBAN.GROUND, SOKOBAN.TARGET, SOKOBAN.PLAYER] \
                and not self.has_box(pos)


    def lost_state(self, mboxes=None, boxlist=None):
        if mboxes is None:
            mboxes = self.mboxes
        if boxlist is None:
            boxlist = self.boxes

        # check if some boxes are in wall corners
        for box in boxlist:
            if self.is_target(box): continue
            prev = False
            for d in SOKOBAN.AROUND:
                side = in_dir(box, d)
                blocked = self.is_wall(side)
                if prev and blocked:
                    return True
                # WARNING: do not check with has_box, since it may be on 
                # a different state of boxes
                x,y = side
                if mboxes[y][x]:
                    # check if close to a wall
                    if horizontal(d):
                        d1 = SOKOBAN.UP
                        d2 = SOKOBAN.DOWN
                    else:
                        d1 = SOKOBAN.LEFT
                        d2 = SOKOBAN.RIGHT
                        # check above and below
                    ub = in_dir(box, SOKOBAN.UP)
                    us = in_dir(side, SOKOBAN.UP)
                    db = in_dir(box, SOKOBAN.DOWN)
                    ds = in_dir(side, SOKOBAN.DOWN)
                    if self.is_wall(ub) and self.is_wall(us)\
                    or self.is_wall(db) and self.is_wall(ds):
                        return True

                prev = blocked


        return False



    def get_current_state(self):
        return { 'mboxes': deepcopy(self.mboxes),
                 'player': self.player_position }

    def restore_state(self, state):
        self.mboxes = state['mboxes']
        self.update_box_positions()
        self.player_position = state['player']
        self.invalidate()

    def push_state(self):
        self.state_stack.append(self.get_current_state())


    def move_player (self, direction):
        x,y = self.player_position
        move_x, move_y = direction

        # print ("trying to move", x,"x",y," in direction",direction)

        playerHasMoved  = False
        levelHasChanged = False

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
            playerHasMoved  = True

        elif self.has_box((xx,yy)) and self.is_empty((xx2,yy2)):
            # Player is trying to push a box

            levelHasChanged = True

            # Save current state
            self.push_state()

            boxi = self.boxes.index((xx,yy))
            self.boxes[boxi] = (xx2,yy2)

            self.mboxes[yy][xx] = False
            self.mboxes[yy2][xx2] = True

            self.player_position = (xx,yy)
            playerHasMoved  = True


        if playerHasMoved:
            self.invalidate()
            self.num_moves += 1

        return levelHasChanged


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
            sides = [False for d in SOKOBAN.DIRS]
            for d,(mx,my) in enumerate(SOKOBAN.DIRS):
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
        for mx,my in SOKOBAN.DIRS:
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
            for mx,my in SOKOBAN.DIRS:
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
            print ("area is not attainable...")
            return None

        path = self.dij.shortest_path(self.player_position, pos)
        return path

    def solve_all_boxes(self):
        print ("Solving for all boxes!")
        bs = BoxSolution(self, self.boxes)
        path = bs.solve()
        return path


    def solve_one_box(self, source):
        print ("Moving one box from", source, "to any target")
        bs = BoxSolution(self, [source])
        path = bs.solve()
        return path




    def move_one_box(self, source, dest):
        print ("Moving one box from", source, "to", dest)
        bs = BoxSolution(self, [source], dest=dest)
        path = bs.solve()
        return path


    def side_box(self, box, d):
        bx,by = box
        mx,my = SOKOBAN.DIRS[d]
        return bx+mx,by+my



    def update_visual (self):
        self.reset_highlight()

        self.compute_attainable()

        self.highlight(self.dij.att_list, SOKOBAN.HATT)

        succ = self.compute_boxes_successors()
        self.highlight(succ, SOKOBAN.HSUCC)


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
            print("No previous state")
            return False

        state = self.state_stack.pop()

        self.restore_state(state)


        return self.state_stack != []


    def render(self, window, textures, highlights):

        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map[y][x] == SOKOBAN.TARGET:
                    window.blit(textures[SOKOBAN.GROUND], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))
                    window.blit(textures[self.map[y][x]], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))

                elif self.map[y][x] in textures:
                    window.blit(textures[self.map[y][x]], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))
                else:
                    pygame.draw.rect(window, SOKOBAN.WHITE, (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))

                if self.mboxes[y][x]:
                    window.blit(textures[SOKOBAN.BOX], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))

                h = self.mhighlight[y][x]
                if h:
                    window.blit(highlights[h], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))


