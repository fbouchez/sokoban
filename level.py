import pygame
import constants as SOKOBAN
from copy import deepcopy
from explore import *

class Level:
    def __init__(self, level_to_load, levelstyle):
        self.last_structure_state = None
        self.num_moves = 0
        self.dij = None
        self.single_file_levels = None
        self.level_number = 0
        self.load(level_to_load, levelstyle)

    def parse_rows(self, rows, symbols):

        self.structure = []
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

                if block == SOKOBAN.BOX or block == SOKOBAN.TARGET_FILLED:
                    self.boxes.append((x,y))
                elif block == SOKOBAN.PLAYER:
                    level_row[-1] = SOKOBAN.GROUND
                    self.position_player = (x,y)

            self.structure.append(level_row)

        self.map_width =  max_width
        self.map_height = height
        # print ("Level size: ", self.map_width, "x", self.map_height)
        # print (self.structure)



    def load_file_by_file(self, levelnum, nextlevel=False):
        with open("assets/levels/level_" + str(levelnum) + ".txt") as level_file:
            rows = level_file.read().split('\n')
        self.parse_rows(rows, SOKOBAN.SYMBOLS_MODERN)


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
                    # print ("newlevel:", curnum, cur)
                    cur = []
                else:
                    cur.append(r)

            self.single_file_levels = lev

        # if nextlevel:
            # self.level_number += 1
            # levelnum = self.level_number
#
        # for num,rows in self.single_file_levels:
            # if num == levelnum:
                # self.parse_rows(rows, SOKOBAN.SYMBOLS_ORIGINALS)
                # return

        if levelnum > len(self.single_file_levels):
            raise ValueError("Level does not exist (did you finish them all?)")

        num,rows = self.single_file_levels[levelnum-1]

        self.parse_rows(rows, SOKOBAN.SYMBOLS_ORIGINALS)
        return
        raise ValueError("level number not found")


    def load(self, levelnum, levelstyle='single_file'):
        # print ('loading level', levelnum)
        if levelstyle == 'file_by_file':
            self.load_file_by_file(levelnum=levelnum)
        elif levelstyle == 'single_file':
            self.load_single_file(levelnum, nextlevel=False)

        self.width = self.map_width * SOKOBAN.SPRITESIZE
        self.height = self.map_height * SOKOBAN.SPRITESIZE

        dij = Dijkstra(self)
        att = dij.attainable(self.position_player, boxes_block=False)
        for x,y in att:
            if self.structure[y][x] == SOKOBAN.AIR:
                self.structure[y][x] = SOKOBAN.GROUND

        self.mhighlight = [[SOKOBAN.HOFF for x in range(self.map_width)] for y in range(self.map_height)]
        # self.highlight( att)

    def reset_highlight (self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.mhighlight[y][x] = SOKOBAN.HOFF


    def highlight (self, positions, htype=SOKOBAN.HATT):
        for x,y in positions:
            self.mhighlight[y][x] = htype

    def is_box (self, pos):
        x,y = pos
        return self.structure[y][x] in [SOKOBAN.BOX, SOKOBAN.TARGET_FILLED]

    def is_empty (self, pos):
        x,y = pos
        return self.structure[y][x] in [SOKOBAN.GROUND, SOKOBAN.TARGET, SOKOBAN.PLAYER]


    def move_player (self, direction):
        x,y = self.position_player
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
            self.position_player = (xx,yy)
            playerHasMoved  = True

        elif self.is_box((xx,yy)) and self.is_empty((xx2,yy2)):
            # Player is trying to push a box

            levelHasChanged = True

            self.last_structure_state = deepcopy(self.structure)
            self.last_boxes_state = deepcopy(self.boxes)
            self.last_player_pos = (x,y)

            boxi = self.boxes.index((xx,yy))
            self.boxes[boxi] = (xx2,yy2)

            if self.structure[yy][xx] == SOKOBAN.TARGET_FILLED:
                self.structure[yy][xx] = SOKOBAN.TARGET
            else:
                self.structure[yy][xx] = SOKOBAN.GROUND

            if self.structure[yy2][xx2] == SOKOBAN.TARGET:
                self.structure[yy2][xx2] = SOKOBAN.TARGET_FILLED
            else:
                self.structure[yy2][xx2] = SOKOBAN.BOX

            self.position_player = (xx,yy)
            playerHasMoved  = True

        if playerHasMoved:
            self.dij = None
            self.num_moves += 1

        return levelHasChanged


    def compute_attainable(self):
        if not self.dij:
            self.dij = Dijkstra(self)
            self.dij.attainable(self.position_player)

    def box_attainable_sides(self, boxpos):

        self.compute_attainable()
        mark = self.dij.get_marks()
        succ = []
        bx,by = boxpos
        sides = [False for d in SOKOBAN.DIRS]
        for d,(mx,my) in enumerate(SOKOBAN.DIRS):
            if mark[by+my][bx+mx]:
                sides[d] = True
        return tuple(sides)



    def compute_box_successors(self, boxpos):
        assert(self.is_box(boxpos))

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

        path = self.dij.shortest_path(self.position_player, pos)
        return path


    def solve_one_box(self, position):
        return False


    def move_one_box(self, source, dest):
        print ("Moving one box from", source, "to", dest)
        bs = BoxSolution(self)
        path = bs.move(source, dest)

        if not path:
            return False

        # print ("push the box as follows:")
        # for d in path:
            # print ("\tfrom",SOKOBAN.DNAMES[d])
        # print ("now path", list(path))
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


    def cancel_last_move(self):
        if self.last_structure_state:
            self.structure = self.last_structure_state
            self.boxes = self.last_boxes_state
            self.position_player = self.last_player_pos
            self.last_structure_state = None
            self.dij = None

        else:
            print("No previous state")

    def render(self, window, textures, highlights):

        for y in range(len(self.structure)):
            for x in range(len(self.structure[y])):
                if self.structure[y][x] == SOKOBAN.TARGET:
                    window.blit(textures[SOKOBAN.GROUND], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))
                    window.blit(textures[self.structure[y][x]], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))

                if self.structure[y][x] in textures:
                    window.blit(textures[self.structure[y][x]], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))
                else:
                    if self.structure[y][x] == SOKOBAN.TARGET_FILLED:
                        pygame.draw.rect(window, (0,255,0), (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))
                    else:
                        pygame.draw.rect(window, SOKOBAN.WHITE, (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE, SOKOBAN.SPRITESIZE))

                h = self.mhighlight[y][x]
                if h:
                    window.blit(highlights[h], (x * SOKOBAN.SPRITESIZE, y * SOKOBAN.SPRITESIZE))


