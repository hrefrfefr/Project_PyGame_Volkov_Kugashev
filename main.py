import os
import pygame, random, sys
from pygame.locals import *

pygame.init()
pygame.key.set_repeat(200, 70)

fps = 30
width = 600
height = 600
new_asteroid_tick = 40

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('Пояс астероидов')
pygame.mouse.set_visible(False)

player = None
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def Key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_RETURN:
                    return


def write_Text(text, font, surface, x, y):
    text_object = font.render(text, 1, pygame.Color('white'))
    text_rect = text_object.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_object, text_rect)


def terminate():
    pygame.quit()
    sys.exit()


def crash(playerRect, asteroids):
    for a in asteroids[::-1]:
        if playerRect.colliderect(a['rect']):
            return True
    return False


def start_screen():
    intro_text = ["Командир!", "SOS!!!",
                  "Мы попали в пояс астероидов",
                  "ускорение на Ctrl",
                  "удачи, конец связи шшшш..."]
    fon = pygame.transform.scale(load_image('background.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    pygame.mixer.music.load(os.path.join('data', 'startscreenmusic.mp3'))
    pygame.mixer.music.play(-1, 0.0)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


player_image = load_image('Plane.png', -1)
asteroid_image = load_image('asteroid.png', -1)
high_speed_player_image = load_image('Plane speed.png', -1)
f = load_image('f.png', -1)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(width // 2, height // 2)
        self.speed = 3
        self.rechargetime = 600
        self.highspeed = False
        self.mask = pygame.mask.from_surface(self.image)

    def speed_down(self):
        self.cur_tick = pygame.time.get_ticks()
        self.speed = 3
        self.highspeed = False
        self.image = player_image

    def speed_up(self):
        self.cur_tick = pygame.time.get_ticks()
        self.speed = 10
        self.highspeed = True
        self.image = high_speed_player_image

    def kill(self):
        self.image = f
