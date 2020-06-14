#importa as funções iniciais
import pygame, sys, os, random

import data.engine as e 

#inicializa a função tempo
clock = pygame.time.Clock()
#função pai
from pygame.locals import*

#pré inicializa a musica para tirar o delay(frequencia, tamanho, chanel(mono/stereo), toca imediatamente(buf))
pygame.mixer.pre_init(44100, -16, 2, 512)

#inicia o pygame
pygame.init()
pygame.mixer.init()

#adiciona mais channels para futuras iterações
pygame.mixer.set_num_channels(64)

#nome da janela
pygame.display.set_caption('Meu game')

#defini tamanho da janela
WINDOW_SIZE = (600,400)

TRANSPARENT = (0,0,0,0)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) 

#tamanho que será mostrado
display = pygame.Surface((300,200)) 

moving_right = False
moving_left = False
player_y_momentum = 0 #gravidade
air_timer = 0

#scroll adiciona movimento a tela e ao personagem dando efeito de paralaxe
true_scroll = [0,0]
##


#chama o arquivo txt do mapa
def carrega_o_mapa(path):
    m = open(path + '.txt', 'r')
    f = m.read()
    m.close()
    f = f.split('\n')
    mapa_jog = []
    for row in f:
        mapa_jog.append(list(row))
    return mapa_jog

#carrega animação
e.load_animations('data/img/Geral/')
#

#lista com os mapas
levels = ['map1', 'map2']
numero_nivel = 0
###

#carrega as imagens
ground_img = pygame.image.load('data/img/ground_1.png')
plataform_img = pygame.image.load('data/img/platform.png')
wall_img = pygame.image.load('data/img/wall.png')
door_img = pygame.image.load('data/img/door.png')
e_prompt_img = pygame.image.load('data/img/e.png')
chest_img = pygame.image.load('data/img/Chest.png')
open_chest_img = pygame.image.load('data/img/open_chest.png')

# Imagens de background
background1 = pygame.image.load('data/img/background1-Copia.png')
background2 = pygame.image.load('data/img/background2.png')
backgrounds = [background1, background2]
background_rects = []
for background in backgrounds:
     for background in backgrounds:
        background_rects.append(background.get_rect())


#Musicas
jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
jump_sound.set_volume(0.2)
sons_passo = [pygame.mixer.Sound('data/audio/passo_0.wav'), pygame.mixer.Sound('data/audio/passo_1.wav')]
sons_passo[0].set_volume(0.2) #ajusta altura do som
sons_passo[1].set_volume(0.2) ##

#musica tema
pygame.mixer.music.load('data/audio/music.wav')
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(-1) #-1 para deixar a musica tocando infinitamente
#

enemies = []
for i in range(5):
    enemies.append([0,e.Geral(300,80,13,13,'enemy')])
    enemies.append([0,e.Geral(450,80,13,13,'enemy')])
    enemies.append([0,e.Geral(250,500,13,13,'enemy')])



tempo_passo = 0

player= e.Geral(100,100,16,27,'player')# ajusta o tamanho do personagem com as plataformas
###

#objetos no fundo do mapa
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
###

# detecta se o jogador esta em frente de uma porta
def deteccao_porta(object_1,object_list,names):
    coordinates = 0
    collision_list, tile_type = e.collision_test(object_1, object_list, names)
    for obj in collision_list:
        if tile_type == 'D' or tile_type == 'C':
            coordinates = obj
            return True, coordinates
    return False, coordinates    

# função modifica o mapa para que os baus que foram abertos fiquem abertos
def abre_o_bau(map_file, names, num_chest):
    line_chest = (names['C'][num_chest].y)/16
    with open(map_file, 'r') as map_data:
        blocos = map_data.readlines()
        location_chest = str(blocos[int(line_chest)])
        change_chest = location_chest.replace('C', 'O') 
        blocos[int(line_chest)] = change_chest
    with open(map_file, 'w') as map_data:
        map_data.writelines(blocos)

#loop do jogo

while True:
    display.fill((146,244,255))

    # Carrega o mapa 
    mapa = carrega_o_mapa(levels[numero_nivel])

    # Cria loop infinito musica
    if tempo_passo > 0:
        tempo_passo -= 1
    
    #adicona o scroll ao mapa e o faz seguir o player
    true_scroll[0] += (player.x - true_scroll[0] - 130)/10
    true_scroll[1] += (player.y - true_scroll[1] - 95)/10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Atualiza a posição de cada camada do fundo e desenha
    for i in range(len(backgrounds)):
        background = backgrounds[i]
        background_rect = background_rects[i]
        if i == 0:
        # Atualiza a posição da imagem de fundo.
        #checa se o jogador esta movendo
            background_rect.y = -48
            if moving_right:
                background_rect.x -= 4/8
            elif moving_left:
                background_rect.x += 4/8
        # Se o fundo saiu da janela, faz ele voltar para dentro.
            if background_rect.right < 112:
                background_rect.x += background_rect.width
        # Desenha o fundo e uma cópia para a direita.
        # Assumimos que a imagem selecionada ocupa pelo menos o tamanho da janela.
        # Além disso, ela deve ser cíclica, ou seja, o lado esquerdo deve ser continuação do direito.
            display.blit(background, background_rect)
        # Desenhamos a imagem novamente, mas deslocada da largura da imagem em x.
            background_rect2 = background_rect.copy()
            #checa se o jogador esta movendo
            background_rect2.y = -48
            if moving_left or moving_right:
                background_rect2.x += -scroll[0]/100
            display.blit(background, background_rect2)
        elif i == 1:
            # Atualiza a posição da imagem de fundo.
            #checa se o jogador esta movendo
            if moving_right:
                background_rect.x -= 1
            if moving_left:
                background_rect.x += 1
        # Se o fundo saiu da janela, faz ele voltar para dentro.
            if background_rect.right < 112:
                background_rect.x += background_rect.width
        # Desenha o fundo e uma cópia para a direita.
        # Assumimos que a imagem selecionada ocupa pelo menos o tamanho da janela.
        # Além disso, ela deve ser cíclica, ou seja, o lado esquerdo deve ser continuação do direito.
            display.blit(background, background_rect)
        # Desenhamos a imagem novamente, mas deslocada da largura da imagem em x.
            background_rect2 = background_rect.copy()
            #checa se o jogador esta movendo
            if moving_right:
                background_rect2.x -= 1
            if moving_left:
                background_rect2.x += 1
            display.blit(background, background_rect2)

#adiciona as plataformas, grouds e outros objetos definidos no mapa
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

# movimento + gravidade + animacoes
    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] +=2
    if moving_left == True:
        player_movement[0] -=2
    player_movement[1] += player_y_momentum
    player_y_momentum +=0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_y_momentum == 3:
        player.set_action('run')
    if player_movement[0] == 0:
        player.set_action('idle')
    if player_movement[0] > 0:
        player.set_flip(False)
        player.set_action('run')
    if player_movement[0] < 0:
        player.set_flip(True)
        player.set_action('run')

    collisions_types = player.move(player_movement,tile_rects, tile_names)
    em_frente_porta,local_porta = deteccao_porta(player,tile_rects, tile_names)

# Caso se o jogador tiver que interagir com uma porta
    if em_frente_porta:
        if event.type == KEYDOWN:
            if event.key == K_e:
                pygame.time.delay(200)
                # detecta qual mapa o jogador se encontra
                if levels[numero_nivel] == 'map1':
                    #define qual local o jogador sera teletransportado
                    if local_porta == tile_names['D'][0]:
                        px = tile_names['D'][4].x
                        py = tile_names['D'][4].y
                        player.set_pos(px, py)
                    elif local_porta == tile_names['D'][1]:
                        px = tile_names['D'][2].x
                        py = tile_names['D'][2].y
                        player.set_pos(px, py)
                    elif local_porta == tile_names['D'][2]:
                        px = tile_names['D'][1].x
                        py = tile_names['D'][1].y
                        player.set_pos(px, py)
                    # muda o mapa do jogador
                    elif local_porta == tile_names['D'][3]:
                        last_door = tile_names['D'][3]
                        numero_nivel = 1
                        px = 80
                        py = 96
                        player.set_pos(px, py) 
                    elif local_porta == tile_names['D'][4]:
                        px = tile_names['D'][0].x
                        py = tile_names['D'][0].y
                        player.set_pos(px, py)    
                    # muda o estado do bau permanetemente
                    elif local_porta == tile_names['C'][0]:
                        e.abre_o_bau('map1.txt', tile_names, 0)        
                elif levels[numero_nivel] == 'map2':
                    if local_porta == tile_names['D'][0]:
                        numero_nivel = 0
                        px = last_door.x
                        py = last_door.y
                        player.set_pos(px, py)

# estabelece o tempo no ar e colisões com o ground
    if collisions_types['bottom'] == True:
        air_timer = 0
        player_y_momentum = 0
        if player_movement[0] != 0: # solta o volume apenas quando detecta colisão bottom
            if tempo_passo == 0:
                tempo_passo = 30
                random.choice(sons_passo).play()
    else:
        air_timer += 1
#estabelece as animações
    player.change_frame(1)
    player.display(display,scroll)

    #define a partir de quando o enemy começa a seguir o player
    display_r = pygame.Rect(scroll[0],scroll[1],300,200)

    #define o enemy
    for enemy in enemies:
        if display_r.colliderect(enemy[1].obj.rect):
            enemy[0] += 0.2
            if enemy[0] > 3:
                enemy[0] = 3
            enemy_movement = [0,enemy[0]]
            if player.x > enemy[1].x + 5:
                enemy_movement[0] = 1
            if player.x < enemy[1].x - 5:
                enemy_movement[0] = -1
            collision_types = enemy[1].move(enemy_movement,tile_rects,names=[])
            if collision_types['bottom'] == True:
                enemy[0] = 0
            enemy[1].display(display,scroll)
            enemy_loc = pygame.Vector2(enemy[1].x, enemy[1].y)
            player_loc = pygame.Vector2(player.x, player.y)
            distance_player_enemy = enemy_loc.distance_to(player_loc)
            #print(c)
            if player.obj.rect.colliderect(enemy[1].obj.rect):
                player_y_momentum = -4
    
#movimentacao com o teclado
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_w: # desliga a música 
                pygame.mixer.music.fadeout(1000) # delay para a música não parar imediatamente
            if event.key == K_r: # liga a música
                pygame.mixer.music.play(-1) #-1 para voltar a tocar infinitamente
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60 )# mantem o jogo em 60fps

