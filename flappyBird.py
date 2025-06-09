import pygame
import neat
import time
import random
import os

# Grootte van het scherm instellen
MIN_WIDTH = 500
MIN_HEIGHT = 800

# Imgs inladen
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
                pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


# klasse bird maken
class Bird:
    IMGS = BIRD_IMGS
    # Hoeveel graden de bird kan draaien op zijn y as
    MAX_ROTATION = 25
    # Hoe snel de bird kan draaien op 1 frame
    ROT_VEL = 20
    # Hoe lang de animatie van draaien duurt
    ANIMATION_TIME = 5

    # Instellen van de constructor met (x,y) tilt snelheid en imgs
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #negatieve velocity instellen omdat pygame raar doet
        self.tick_count = 0 # Houdt bij hoelang het geleden is dat we jump hebben gedaan
        self.height = self.y

    def move(self):
        self.tick_count += 1 # er is bewogen

        # Controle voor beweging
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2 # Vgl uit de fysica, verplaatsing berekenen (v.t)
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL 

    def draw(self, window):
        self.img_count += 1

        #Checkt welke afbeelding wordt getoond op basis van de ANIMATION TIME
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center) # roteert img rond center
        window.blit(rotated_img, new_rect.topleft)

    # Checkt voor collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    


#Klasse voor de pijp
class Pipe:
    GAP = 200
    VEL = 5

    # constructor
    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    #Hoogte pijpen instellen
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom  = self.height + self.GAP

    #Verplaats de pijpen
    def move(self):
        self.x -= self.VEL

    # Tekent de pijpen
    def draw(self,window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Berekent collision met pijpen
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Berekent offset en kijkt of er overlap is zoja return true
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False
    

# Maakt de base van de game
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    #Verplaats de base naar het begin als hij eindigt
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH 

    # Teken base
    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))

    
# Maakt een pygame scherm
def draw_window(window, bird):
    window.blit(BACKGROUND_IMG, (0,0))
    bird.draw(window)
    pygame.display.update()

# Roept het pygame scherm op, maakt een nieuwe bird en controleert of het spel nog bezig is
# Controleert ook movement van de bird en stelt een klok in zodat bird niet te snel valt
def main():
    bird = Bird(200,200)
    window = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()
        draw_window(window,bird)

    pygame.quit()
    quit()

main()
