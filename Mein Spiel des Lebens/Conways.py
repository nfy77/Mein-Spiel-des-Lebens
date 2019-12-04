from collections import OrderedDict
import pygame, random
from pygame.locals import *

speed = 2 # how many iterations per second
squares = 2 # size of squares: 0 = 8X8, 1 = 16X16, 2 = 32X32, 3 = 64X64
map_size = 16 # the width and height

rand_seed = 64

if squares == 0:
	imgs = ["res/alive_8.png","res/dead_8.png", 8]
if squares == 1:
	imgs = ["res/alive_16.png","res/dead_16.png", 16]
if squares == 2:
	imgs = ["res/Pilz_or_32.jpg","res/Empty_32.jpg", 32]
if squares == 3:
	imgs = ["res/alive_64.png","res/dead_64.png", 64]

title = 'Game of Life'

class cell:
    def __init__(self, location, alive = False):
        self.location = location
        self.alive = alive
                
        self.to_be = None
        self.pressed = False


class World:
    def __init__(self):
        self.map = []

    def fill(self, rand_seed=None):
        if rand_seed!=None:
            random.seed(rand_seed)
            
        for i in range(map_size):
            self.map.append([])
            for g in range(map_size):
                if rand_seed==None:
                    self.map[i].insert(g, cell((i,g)))
                else: 
                    a = random.randint(0,4)
                    if a == 0: self.map[i].insert(g, cell((i,g),True))
                    else: self.map[i].insert(g, cell((i,g)))
					
    def draw(self, screen):
        for i in range(map_size):
            for g in range(map_size):
                cell = self.map[i][g]
                loc = cell.location
                if cell.alive == True: screen.blit(alive, (loc[0]*imgs[2], loc[1]*imgs[2]))
                else: screen.blit(dead, (loc[0]*imgs[2], loc[1]*imgs[2]))

    def get_cells(self, cell):# gets the cells around a cell
        mapa = self.map
        a = []
        b = []
        c = 0
        cell_loc = cell.location
        try: a.append(mapa[abs(cell_loc[0]-1)][abs(cell_loc[1]-1)].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0])][abs(cell_loc[1]-1)].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0]+1)][abs(cell_loc[1]-1)].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0]-1)][abs(cell_loc[1])].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0]+1)][abs(cell_loc[1])].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0]-1)][abs(cell_loc[1]+1)].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0])][abs(cell_loc[1]+1)].location)
        except Exception: pass
        try: a.append(mapa[abs(cell_loc[0]+1)][abs(cell_loc[1]+1)].location)
        except Exception: pass
        num = len(list(OrderedDict.fromkeys(a)))# removes duplicates
        for i in range(len(a)): b.append(mapa[a[i][0]][a[i][1]].alive)
        for i in b:# c houses how many cells are alive around it
            if i == True: c+=1
        if cell.alive == True:# rules
            if c < 2: cell.to_be = False
            if c > 3:cell.to_be = False
        else:
            if c == 3: cell.to_be = True
							  #rules
    def update_frame(self):
        for i in range(map_size):
            for g in range(map_size):
                cell = self.map[i][g]
                self.get_cells(cell)

    def update(self, screen):
        for i in range(map_size):
            for g in range(map_size):
                cell = self.map[i][g]
                loc = cell.location
                if cell.to_be != None: cell.alive = cell.to_be
                if self.map[i][g].alive == True: screen.blit(alive,(loc[0]*imgs[2],loc[1]*imgs[2]))
                else: screen.blit(dead,(loc[0]*imgs[2],loc[1]*imgs[2]))
                cell.to_be = None

def cell_list(world):
    lst = []
    for i in range(map_size):
        lst.append([])
        for g in range(map_size): lst[i].append((world.map[i][g].location[0]*imgs[2],world.map[i][g].location[1]*imgs[2]))
    return lst

#-----CONFIG-----
pygame.init()
pygame.display.set_caption(title)

width = map_size*imgs[2]
height = map_size*imgs[2]
screen_size = width,height
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
alive = pygame.image.load(imgs[0]).convert()
dead = pygame.image.load(imgs[1]).convert()
done = False

# генерация мира

world = World()
# world.fill()
world.fill(rand_seed)

world.draw(screen)  
tp = 0
run = False

while done == False:
    milliseconds = clock.tick(60)
    seconds = milliseconds / 1000.0
    tp += milliseconds

    for event in pygame.event.get():
        if event.type == QUIT:
            done = True

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                run = not run

        if event.type == KEYUP:
            if event.key == K_q:
                run = False
                world.update_frame()
                world.update(screen)

        if event.type == MOUSEBUTTONUP:
            for i in range(map_size):
                for g in range(map_size):
                    world.map[i][g].pressed = False

    pressed = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    pos = pygame.mouse.get_pos()

    if pressed[K_r]:
        world.map = []
        world.fill(None)
        world.draw(screen)
    if pressed[K_a]:
        world.map = []
        world.fill(rand_seed)
        world.draw(screen)

    if run == True and tp >= 1000/speed :
        tp = 0
        world.update_frame()
        world.update(screen)

    if mouse[0]:# makes cells alive
        rects = cell_list(world)
        for i in range(map_size):
            for g in range(map_size):
                if pos[0] >= rects[i][g][0] and pos[0] < rects[i][g][0]+imgs[2] and pos[1] >= rects[i][g][1] and pos[1] < rects[i][g][1]+imgs[2] and world.map[i][g].pressed == False:
                    world.map[i][g].alive = True
                    world.map[i][g].pressed = True
                    world.update(screen)

    if mouse[2]: # kills cells
        rects = cell_list(world)
        for i in range(map_size):
            for g in range(map_size):
                if pos[0] >= rects[i][g][0] and pos[0] < rects[i][g][0]+imgs[2] and pos[1] >= rects[i][g][1] and pos[1] < rects[i][g][1]+imgs[2] and world.map[i][g].pressed == False:
                    world.map[i][g].alive = False
                    world.map[i][g].pressed = False
                    world.update(screen)

    pygame.display.flip()

pygame.quit()