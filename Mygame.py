import pygame, sys, os

#inicializa a função tempo
clock = pygame.time.Clock()
#função pai
from pygame.locals import*
pygame.init()


#nome da janela
pygame.display.set_caption('Meu game')
WIDTH = 600
HEIGHT = 400
WINDOW_SIZE = (WIDTH,HEIGHT)
TRANSPARENT = (0,0,0,0)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) #inicializa a imgemm

display = pygame.Surface((WIDTH/2,HEIGHT/2)) #tamanho que será mostrado

levels = ['map1', 'map2']
numero_nivel = 0

trigger_transition = False

moving_right = False
moving_left = False
player_y_momentum = 0 #gravidade
air_timer = 0

#scroll adiciona movimento a tela e ao personagem dando efeito de paralaxe
true_scroll = [0,0]
##

#spawna inimigo#
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('player_animations',img))
        self.image.convert_alpha()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#chama o arquivo txt do mapa
def carrega_o_mapa(path):
    m = open (path + '.txt', 'r')
    f = m.read()
    m.close()
    f = f.split('\n')
    mapa_jog = []
    for row in f:
        mapa_jog.append(list(row))
    return mapa_jog

#carrega as animações#
global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # animações na pasta
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

#da o flip na animação
def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame

#chama as animações nas pastas#
animation_database = {}

animation_database['run'] = load_animation('player_animations/run',[10,10,10,10,10,10,10,10,10,10])
animation_database['idle'] = load_animation('player_animations/idle',[10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10])

###

#incializa as colisões em x e y do retângulo do personagem

ground_img = pygame.image.load('ground_1.png')
plataform_img = pygame.image.load('platform.png')
wall_img = pygame.image.load('wall.png')
door_img = pygame.image.load('door.png')
e_prompt_img = pygame.image.load('e.png')
chest_img = pygame.image.load(os.path.join('tile_set', 'Chest.png'))
open_chest_img = pygame.image.load(os.path.join('tile_set', 'open_chest.png'))

player_action = 'idle'
player_frame = 0
player_flip = False

enemy   = Enemy(32,72,'enemie.png')# spawn enemy
enemy_list = pygame.sprite.Group()   # create enemy group
enemy_list.add(enemy) 

player_rect = pygame.Rect(100,100,16,27) # ajusta o tamanho do personagem com as plataformas
###

#objetos no fundo do mapa
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
###

def abre_o_bau(map_file, num_chest):
    line_chest = (tile_names['C'][num_chest].y)/16
    with open(map_file, 'r') as map_data:
        blocos = map_data.readlines()
        location_chest = str(blocos[int(line_chest)])
        change_chest = location_chest.replace('C', 'O') 
        blocos[int(line_chest)] = change_chest
    with open(map_file, 'w') as map_data:
        map_data.writelines(blocos)

def collision_test(rect,tiles,names):
    hit_list = []
    name = ''
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
            for key in names:
                if tile in names[key]:
                    name = key
    return hit_list, name

#colisões e movimentos##
def move(rect,movement,tiles,names):
   
    collision_types = {'top':False, 'bottom':False, 'right':False, 'left': False}
   
    rect.x += movement[0]
   
    hit_list, tile_type = collision_test(rect, tiles, names)
    
    for tile in hit_list:
        if movement[0] > 0 and tile_type != '2' and tile_type !='D' and tile_type !='C' and tile_type !='O':
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0 and tile_type != '2' and tile_type !='D' and tile_type !='C' and tile_type !='O':
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list, tile_type = collision_test(rect, tiles, names)
    
    for tile in hit_list:
        if movement [1] > 0 and tile_type !='D' and tile_type !='C' and tile_type !='O':
            rect.bottom = tile.top 
            collision_types['bottom'] = True
        elif movement[1] < 0 and tile_type != '2' and tile_type !='D' and tile_type !='C' and tile_type !='O':
            rect.top = tile.bottom
            collision_types['top'] = True
        
    return rect, collision_types

def deteccao_porta(rect,tiles,names):
    coordinates = 0
    hit_list, tile_type = collision_test(rect, tiles,names)
    for tile in hit_list:
        if tile_type == 'D' or tile_type == 'C':
            coordinates = tile
            return True, coordinates
        
    
    return False, coordinates    

#loop do jogo

while True:
    display.fill((146,244,255))
    #if trigger_transition:

    mapa = carrega_o_mapa(levels[numero_nivel])

    #adicona o scroll ao mapa e o faz seguir o player
    true_scroll[0] += (player_rect.x - true_scroll[0] - 130)/10
    true_scroll[1] += (player_rect.y - true_scroll[1] - 95)/10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    ##

    # adiciona o background
    pygame.draw.rect(display,(7,80,75),pygame.Rect(0,120,300,80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display,(14,222,150),obj_rect)
        else:
            pygame.draw.rect(display,(9,91,85),obj_rect)

#adiciona as plataformas e grouds
    tile_rects = []
    tile_names = {}
    y=0
    for layer in mapa:
        x=0
        for tile in layer:
            if tile == 'W':
                display.blit(wall_img, (x*16 - scroll[0], y*16 - scroll[1]))
            if tile == 'D':
                display.blit(door_img, (x*16 - scroll[0], y*16 - scroll[1]))
            if tile == 'C':
                display.blit(chest_img, (x*16 - scroll[0],y*16 - scroll[1]))
            if tile == 'O':
                display.blit(open_chest_img, (x*16 - scroll[0],y*16 - scroll[1]))    
            if tile == '1':
                display.blit(ground_img, (x*16 - scroll[0], y*16 - scroll[1]))
            if tile == '2':
                display.blit(plataform_img, (x*16 - scroll[0], y*16 - scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x*16, y*16, 16,16))
                if tile in tile_names:
                    tile_names[tile].append(pygame.Rect(x*16, y*16, 16,16))    
                else:
                    tile_names[tile] = [(pygame.Rect(x*16, y*16, 16,16))]    
            x+=1
        y +=1

#movimento + gravidade + animacoes
    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] +=2
    if moving_left == True:
        player_movement[0] -=2
    player_movement[1] += player_y_momentum
    player_y_momentum +=0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'run')


    player_rect,collisions = move(player_rect,player_movement,tile_rects,tile_names)
    em_frente_porta,local_porta = deteccao_porta(player_rect,tile_rects, tile_names)

##Caso se o jogador tiver que interagir com uma porta
    if em_frente_porta:
        if event.type == KEYDOWN:
            if event.key == K_e:
                pygame.time.delay(100)
                trigger_transition = True
                # detecta qual mapa o jogador se encontra
                if levels[numero_nivel] == 'map1':
                    #define qual local o jogador sera teletransportado
                    if local_porta == tile_names['D'][0]:
                        player_rect.x = tile_names['D'][4].x
                        player_rect.y = tile_names['D'][4].y
                    elif local_porta == tile_names['D'][1]:
                        player_rect.x = tile_names['D'][2].x
                        player_rect.y = tile_names['D'][2].y
                    elif local_porta == tile_names['D'][2]:
                        player_rect.x = tile_names['D'][1].x
                        player_rect.y = tile_names['D'][1].y
                    #muda o mapa do jogador
                    elif local_porta == tile_names['D'][3]:
                        numero_nivel = 1
                        last_door = tile_names['D'][3]
                        player_rect.x = 96
                        player_rect.y = 80
                    elif local_porta == tile_names['C'][0]:
                        abre_o_bau('map1.txt', 0)
                    elif local_porta == tile_names['D'][4]:
                        player_rect.x = tile_names['D'][0].x
                        player_rect.y = tile_names['D'][0].y
                elif levels[numero_nivel] == 'map2':
                    if local_porta == tile_names['D'][0]:
                        numero_nivel = 0
                        player_rect.x = last_door.x
                        player_rect.y = last_door.y
    elif not em_frente_porta:
        e_prompt_img.fill(TRANSPARENT)

##estabelece o tempo no ar
    if collisions['bottom'] == True:
        air_timer = 0
        player_y_momentum = 0
    else:
        air_timer += 1
##   
#estabelece as animações
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

#movimentacao com o teclado
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
                
    enemy_list.draw(display)
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE),(0,0))
    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)# mantem o jogo em 60fps

