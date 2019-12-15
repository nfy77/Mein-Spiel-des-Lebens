from collections import OrderedDict
import pygame, random
from pygame.locals import *

import copy

speed = 4 # how many iterations per second

squares = 2 # size of squares: 0 = 8X8, 1 = 16X16, 2 = 32X32, 3 = 64X64
map_size = 16 # the width and height

rand_seed = 64 # None если не нужна генерация мира
life_chance = 4 # Шанс на зарождение жизни = 1/life_chance

total_res = 8*(map_size**2) # сколько всего ресурсов в мире
res_min = 0
res_max = 32

temp_coef = int(255/(res_max-res_min)) # для отрисовки тепловой карты ресурсов

if squares == 0:
	imgs = ["res/alive_8.png","res/empty_8.png", 8]
if squares == 1:
	imgs = ["res/alive_16.png","res/empty_16.png", 16]
if squares == 2:
	imgs = ["res/Pilz_or_32.jpg","res/Empty_32.jpg", "res/Spore_or_32.jpg", 32]
if squares == 3:
	imgs = ["res/alive_64.png","res/empty_64.png", 64]

title = 'Game of Life'

# генетическая информация
class Gen:
    def __init__(self, mass_begin=3, time_life=10, time_rep=5, spore_num=2, kus=1, food='V'):
        self.mass_begin = mass_begin # начальная масса
        #self.mass_limit=mass_limit     
        self.time_life = time_life # время жизни
        self.time_rep = time_rep # репродуктивный возраст
        
#TODO        #self.type_rep
        #self.sex = # пол если половое размножение
        self.spore_num = spore_num # число потомков
        
        self.kus = kus # кусает за раз
        self.food = food # питается

#TODO self.pretty
        
    def mutation(self):
        x = random.randint(0,100) 
        if(x == 0):
            self.mutagen(9) # сильная мутация, шанс 1%
        elif(x < 11):
            self.mutagen(3) # слабая мутация, шанс 10%
            
    def mutagen(self, force):
        # начальная масса не меньше 2
        self.mass_begin = max(2, self.mass_begin+random.randint(-force,force))
        # время жизни не меньше 8, репродуктивный возраст от 2 тиков
        self.time_life = max(8, self.time_life+random.randint(-force,force))
        self.time_rep = max(2, self.time_rep+random.randint(-force,force))  
        # число потомков не меньше 1
        self.spore_num = max(1, self.spore_num+random.randint(-1,1))  
        # кусает за раз не меньше 2
        self.kus = max(2, self.kus+random.randint(-2,2))  
#TODO        # питается
        #self.food
        
# гриб           
class Pilz:
    def __init__(self, parent=None):
        # у каждого гриба есть генетическая информация
        if(parent == None): 
            self.gen = Gen() # дефолтная
        else:
            self.gen = copy.deepcopy(parent.gen) # от предка, возможно с мутациями
            self.gen.mutation()
        
        self.mass = self.gen.mass_begin # масса
        self.time = 0 # возраст
        
        self.spore = 0 # споры, которые родил гриб
        
    def tic(self, res): # гриб живет
        self.time += 1
        if(self.time > self.gen.time_life):
            return False # погибает от старости 
        
        if(res >= self.gen.kus): # кушает сколько может
            self.mass += self.gen.kus 
        elif(res > 0):
            self.mass += res
        else:               
            return False # погибает без еды    

        return True # живет дальше
    
    def rep(self): # гриб пытается размножиться
        if(self.time > self.gen.time_rep):
            # если масса гриба хотя бы в 2 раза больше начальной + ограничение на число спор
            while(self.mass > 3*self.gen.mass_begin and self.spore < self.gen.spore_num):
                self.mass -= self.gen.mass_begin
                self.spore += 1
                
    # метод для размножения частично вынесен в свойство ячейки
    def info(self):
        print("Mass: "+str(self.mass), "Time: "+str(self.time))
        print("Gen:")
        print("Mass_begin: "+str(self.gen.mass_begin)+", Time of life: "+str(self.gen.time_life)+", Time of rep: "+str(self.gen.time_rep)+", Spore num: "+str(self.gen.spore_num)+", Kus: "+str(self.gen.kus))
        
# ячейка мира    
class Cell: 
    def __init__(self, location, res, alive=False):
        self.location = location # местоположение
        self.alive = alive # живет ли там кто нибудь
        self.res = res # ресурс ячейки
        
        self.pilz = None # ссылка на живущий в ней гриб
        self.parent = None # ссылка на родительский гриб
                
        self.to_be = None
        self.pressed = False
        
# мир        
class World:
    def __init__(self):
        self.map = [] # карта расположения живности 

    # начальная генерация мира
    def fill(self, rand_life=True, rand_res=True):
        free_res = total_res # ресурс, оставшийся для распределения
        for i in range(map_size):
            self.map.append([])
            for j in range(map_size):                
                if(rand_life==True): # шанс что в клетке кто то живет = 1/life_chance
                    a = random.randint(0,life_chance)
                else:
                    a = 1
                if(a == 0): 
                    alive = True
                else:
                    alive = False
                    
                if(rand_res==True): # ресурс конечен
                    r = random.randint(res_min, res_max)
                else: 
                    r = total_res/(map_size**2) # равномерное распределение
                res = min(r, free_res)
                    
                self.map[i].insert(j, Cell((i,j), res, alive))
                free_res -= a

    def tic(self):
        for i in range(-2, map_size-2): # костыль out of range
            for j in range(-2, map_size-2):
                cell = self.map[i][j]
                # работаем ячейками, содержащими гриб
                if(cell.alive == True):   
                    if(cell.pilz == None): # рождение гриба
                        cell.pilz = Pilz(cell.parent)
                    
                    alive = cell.pilz.tic(cell.res) # жизнь гриба
                    cell.res = max(0, cell.res - cell.pilz.gen.kus) # обеднение ресурса
                    
                    cell.pilz.rep() # генерация спор
                    # метание спор в случайную сторону, даже под себя
                    while(cell.pilz.spore > 0):
                        a = random.randint(-1,1)
                        b = random.randint(-1,1)
                        # если место не занято - сажаем, если занято - спора погибает и пополняет ресурс
                        if(self.map[i+a][j+b].alive == False):
                            self.map[i+a][j+b].alive = True
                            self.map[i+a][j+b].parent = cell.pilz
                        else:
                            self.map[i+a][j+b].res += cell.pilz.gen.mass_begin
                        cell.pilz.spore -= 1
                    
                    if(alive == False): # смерть гриба
                        cell.alive = alive
                        cell.res += cell.pilz.mass
                        cell.pilz = None      
                    

    def update(self, screen):
        for i in range(-2, map_size-2): # костыль out of range
            for j in range(-2, map_size-2):
                cell = self.map[i][j]
                loc = cell.location
                res = cell.res
                if cell.pilz != None: 
                    screen.blit(img_occupied, (loc[0]*img_size, loc[1]*img_size))
                    screen.blit(render_cel(cell.pilz.mass), (loc[0]*img_size+img_size/2,loc[1]*img_size+img_size/2))  
                elif cell.alive == True:
                    screen.blit(img_plant, (loc[0]*img_size, loc[1]*img_size))
                else:
                    screen.blit(img_empty, (loc[0]*img_size, loc[1]*img_size))                    
                screen.blit(render_cel(res), (loc[0]*img_size,loc[1]*img_size))
                cell.to_be = None
 
    def info(self):
        num = 0
        mid_mass_begin = 0
        mid_time_life = 0
        mid_time_rep = 0
        mid_spore_num = 0
        mid_kus = 0
        for i in range(-2, map_size-2): # костыль out of range
            for j in range(-2, map_size-2):
                cell = self.map[i][j]
                if cell.pilz != None:
                    gen = cell.pilz.gen
                    num += 1
                    mid_mass_begin += gen.mass_begin
                    mid_time_life += gen.time_life
                    mid_time_rep += gen.time_rep
                    mid_spore_num += gen.spore_num
                    mid_kus += gen.kus
                    
        mid_mass_begin /= num
        mid_time_life /= num
        mid_time_rep /= num
        mid_spore_num /= num
        mid_kus /= num            
        
        print("Num of Pilz: "+str(num))            
        print("Mid Values: ")
        print("Mass_begin: "+str(mid_mass_begin)+", Time of life: "+str(mid_time_life)+", Time of rep: "+str(mid_time_rep)+", Spore num: "+str(mid_spore_num)+", Kus: "+str(mid_kus))
                        
# цвет ресурса: мало-красный, много-зеленый
def render_cel(res):
    color = min(255, (res-res_min)*temp_coef)
    rendersurface = labelFont.render(str(res), False, (255 - color, color, 0))
    return rendersurface
    
def cell_list(world):
    lst = []
    for i in range(map_size):
        lst.append([])
        for g in range(map_size): lst[i].append((world.map[i][g].location[0]*imgs[3],world.map[i][g].location[1]*imgs[3]))
    return lst

#-----CONFIG-----
pygame.init()
pygame.display.set_caption(title)

width = map_size*imgs[3]
height = map_size*imgs[3]
screen_size = width,height
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

img_occupied = pygame.image.load(imgs[0]).convert()
img_empty = pygame.image.load(imgs[1]).convert()
img_plant = pygame.image.load(imgs[2]).convert()
img_size = imgs[3]

done = False

pygame.font.init() #1
labelFont = pygame.font.SysFont('Monaco', 20)

# генерация мира
if rand_seed!=None:
    random.seed(rand_seed)
            
world = World()
world.fill()
world.update(screen)

tp = 0
run = False

while done == False:
    if(run == True):
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
                world.tic()
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
        world.fill(rand_life=False, rand_res=True)
        world.update(screen)
    if pressed[K_a]:
        world.map = []
        world.fill()
        world.update(screen)
    if pressed[K_i]:
        print("Time of World: "+str(tp))
        world.info()
            
    if run == True and tp >= 1000/speed :
        tp = 0
        world.tic()
        world.update(screen)

#    if mouse[0]:# makes cells alive
#        rects = cell_list(world)
#        for i in range(map_size):
#            for g in range(map_size):
#                if pos[0] >= rects[i][g][0] and pos[0] < rects[i][g][0]+imgs[3] and pos[1] >= rects[i][g][1] and pos[1] < rects[i][g][1]+imgs[3] and world.map[i][g].pressed == False:
#                    world.map[i][g].alive = True
#                    world.map[i][g].pressed = True
#                    world.update(screen)
    
    if mouse[0]: # info
        rects = cell_list(world)
        for i in range(map_size):
            for g in range(map_size):
                if pos[0] >= rects[i][g][0] and pos[0] < rects[i][g][0]+imgs[3] and pos[1] >= rects[i][g][1] and pos[1] < rects[i][g][1]+imgs[3] and world.map[i][g].pressed == False:
                    world.map[i][g].pilz.info()
                        


    if mouse[2]: # kills cells
        rects = cell_list(world)
        for i in range(map_size):
            for g in range(map_size):
                if pos[0] >= rects[i][g][0] and pos[0] < rects[i][g][0]+imgs[3] and pos[1] >= rects[i][g][1] and pos[1] < rects[i][g][1]+imgs[3] and world.map[i][g].pressed == False:
                    world.map[i][g].alive = False
                    world.map[i][g].pressed = False
                    world.update(screen)

    pygame.display.flip()

pygame.quit()