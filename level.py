import pygame
import constants as SOKOBAN
from copy import deepcopy
from explore import *

class Level:
    def __init__(self, level_to_load):
        self.last_structure_state = None
        self.load(level_to_load)
        self.num_moves = 0
        self.dij = None

    def load(self, levelnum):
        print ('loading level', levelnum)

        self.structure = []
        max_width = 0
        self.boxes = []
        with open("assets/levels/level_" + str(levelnum) + ".txt") as level_file:
            rows = level_file.read().split('\n')

            for y in range(len(rows)):
                level_row = []
                if len(rows[y]) > max_width:
                    max_width = len(rows[y])

                for x in range(len(rows[y])):
                    if rows[y][x] == ' ':
                        level_row.append(SOKOBAN.AIR)
                    elif rows[y][x] == 'X' or \
                         rows[y][x] == '#':
                        level_row.append(SOKOBAN.WALL)
                    elif rows[y][x] == '*' or \
                         rows[y][x] == '$':
                        level_row.append(SOKOBAN.BOX)
                        self.boxes.append((x,y))
                    elif rows[y][x] == '.':
                        level_row.append(SOKOBAN.TARGET)
                    elif rows[y][x] == '@':
                        level_row.append(SOKOBAN.GROUND)
                        self.position_player = (x,y)
                        print ('load player position', self.position_player)
                self.structure.append(level_row)

        self.map_width =  max_width
        self.map_height = len(rows) - 1

        self.width = max_width * SOKOBAN.SPRITESIZE
        self.height = (len(rows) - 1) * SOKOBAN.SPRITESIZE

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
        return self.structure[y][x] in [SOKOBAN.GROUND, SOKOBAN.TARGET]


    def movePlayer (self, direction):
        x,y = self.position_player
        move_x, move_y = direction

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
            self.last_player_pos = [x,y]

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


    def path_to (self, pos):
        targetx, targety = pos

        if not self.dij:
            self.dij = Dijkstra(self)
            self.dij.attainable(self.position_player)

        if not self.dij.is_marked((targetx,targety)):
            print ("area is not attainable...")
            return None

        path = self.dij.shortest_path(self.position_player, pos)
        return path


    def update_visual (self):
        self.reset_highlight()
        self.dij = Dijkstra(self)
        att = self.dij.attainable(self.position_player)
        self.highlight(att, SOKOBAN.HATT)

        mark = self.dij.get_marks()

        succ = []
        for bx,by in self.boxes:
            for mx,my in SOKOBAN.DIRS:
                if mark[by+my][bx+mx] \
                and self.is_empty((bx-mx, by-my)):
                    # side is attainable
                    # and opposite side is free
                    succ.append((bx-mx, by-my))

        self.highlight(succ, SOKOBAN.HSUCC)


    def cancel_last_move(self, player):
        if self.last_structure_state:
            self.structure = self.last_structure_state
            self.boxes = self.last_boxes_state
            self.position_player = self.last_player_pos
            self.last_structure_state = None

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


