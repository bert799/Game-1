import pygame
import os
WIDTH = 768
HEIGHT = 576
FPS = 60

class Wall(object):
    
    def __init__(self, pos):
        walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)

class Platform(object):
    
    def __init__(self, pos):
        platforms.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)

current_level = 1

pygame.init()

pygame.display.set_caption("Teste de nível")
screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
walls = []
platforms = []

if current_level == 1:

    level = [
    "WWWWWWWWWWWWWWWWWWWWWWWW",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W               PP     W",
    "W                      W",
    "W   PPP                W",
    "W                      W",
    "W             PPPP     W",
    "W                      W",
    "W                      W",
    "WWWWWWWWWWWWWWWWWWWWWWWW",
    ]

    x = y = 0
    for row in level:
        for col in row:
            if col == "W":
                Wall((x, y))
            if col == "P":
                Platform((x, y))
            x += 32
        y += 32
        x = 0
    
running = True
while running:

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
    
    screen.fill((0, 0, 0))
    for wall in walls:
        pygame.draw.rect(screen, (255, 255, 255), wall.rect)
    for platform in platforms:
        pygame.draw.rect(screen, (0, 255, 255), platform.rect)
    pygame.display.flip()