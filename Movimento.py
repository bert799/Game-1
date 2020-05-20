import pygame
import random
import time
from os import path

img_dir = path.join(path.dirname(__file__), 'img')


TITULO = 'Teste animações'
WIDTH = 480 # Largura da tela
HEIGHT = 600 # Altura da tela
FPS = 60 # Frames por segundo


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#estados
STOP = 0
WALKING = 1
DYING = 2
FIGHTING = 3
JUMPING = 4
#tamanho do personagem e objetos
TILE_SIZE = 40 
PLAYER_WIDTH = TILE_SIZE
PLAYER_HEIGHT = int(TILE_SIZE * 1.5)





def load_spritesheet(spritesheet, rows, columns):
    sprite_width = spritesheet.get_width() // columns
    sprite_height = spritesheet.get_height() // rows
    
    # adiciona em uma lista
    sprites = []
    for row in range(rows):
        for column in range(columns):
            x = column * sprite_width
            y = row * sprite_height
            dest_rect = pygame.Rect(x, y, sprite_width, sprite_height)
            image = pygame.Surface((sprite_width, sprite_height))
            image.blit(spritesheet, (0, 0), dest_rect)
            sprites.append(image)
    return sprites


class Player(pygame.sprite.Sprite):
    
    def __init__(self, player_sheet):
        
        pygame.sprite.Sprite.__init__(self)
        player_sheet = pygame.transform.scale(player_sheet, (640, 640))

        spritesheet = load_spritesheet(player_sheet, 10, 10)
        self.animations = {
            STOP: spritesheet[0:20],
            WALKING: spritesheet[20:29],
            WALKING: spritesheet[29:20]
            DYING: spritesheet[41:50],
            FIGHTING: spritesheet[31:40],
            JUMPING: spritesheet[71:80],
        }
        #estado atual do personagem
        self.state = STOP
        self.animation = self.animations[self.state]
        #atualiza o frame
        self.frame = 0
        self.image = self.animation[self.frame]
        #posicionamento
        self.rect = self.image.get_rect()
        
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2

        self.last_update = pygame.time.get_ticks()

        self.frame_ticks = 300
        
    def update(self):
        now = pygame.time.get_ticks()

        elapsed_ticks = now - self.last_update

        if elapsed_ticks > self.frame_ticks:

            self.last_update = now

            self.frame += 1

            self.animation = self.animations[self.state]
            if self.frame >= len(self.animation):
                self.frame = 0
            
            center = self.rect.center
            self.image = self.animation[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center
    

def game_screen(screen):
    clock = pygame.time.Clock()

    player_sheet = pygame.image.load(path.join(img_dir, 'Oldhero.png')).convert_alpha()

    player = Player(player_sheet)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    PLAYING = 0
    DONE = 1

    state = PLAYING
    while state != DONE:
        
        clock.tick(FPS)
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                state = DONE
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    player.state = STOP
                elif event.key == pygame.K_2:
                    player.state = WALKING
                elif event.key == pygame.K_3:
                    player.state = DYING
                elif event.key == pygame.K_4:
                    player.state = FIGHTING
                elif event.key == pygame.K_5:
                    player.state = JUMPING
                
                
                
                
      
        all_sprites.update()
        
        
        screen.fill(BLACK)
        all_sprites.draw(screen)

        pygame.display.flip()



pygame.init()
pygame.mixer.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(TITULO)


print('*' * len(TITULO))
print(TITULO.upper())
print('*' * len(TITULO))
print('Utilize as teclas "1", "2", "3", "4" e "5" do seu teclado para mudar a animação atual.')


try:
    game_screen(screen)
finally:
    pygame.quit()