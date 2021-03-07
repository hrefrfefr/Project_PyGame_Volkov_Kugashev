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


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(asteroid_group, all_sprites)
        self.image = asteroid_image
        self.maxspeed = 8
        self.minspeed = 1
        self.maxsize = 40
        self.minsize = 20

    def generate(self):
        self.size = random.randint(self.minsize, self.maxsize)
        self.rect = pygame.Rect(random.randint(0, width - self.size), 0, self.size, self.size)
        self.speed = random.randint(self.minspeed, self.maxspeed)
        self.image = pygame.transform.scale(asteroid_image, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global work
        if not pygame.sprite.collide_mask(self, player):
            self.rect.move_ip(0, self.speed)
        else:
            player.kill()
            work = False


start_screen()

gameover = pygame.mixer.Sound(os.path.join('data', 'game_over.wav'))
pygame.mixer.music.load(os.path.join('data', 'main_teme.mp3'))
pygame.mixer.music.play(0, 0.0)
player = Player()
work = True
font = pygame.font.Font(None, 30)
score = 0
topScore = 0

while True:
    asteroids = []
    moveLeft = moveRight = moveUp = moveDown = speed_up = False
    recharge = False
    start_time = pygame.time.get_ticks()
    asteroidsAddCounter = 0
    while work:
        score += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                work = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a:
                    moveRight = False
                    moveLeft = True

                if event.key == K_RIGHT or event.key == K_d:
                    moveLeft = False
                    moveRight = True

                if event.key == K_DOWN or event.key == K_s:
                    moveUp = False
                    moveDown = True

                if event.key == K_UP or event.key == K_w:
                    moveDown = False
                    moveUp = True

                if event.key == K_LCTRL and not recharge:
                    speedtime = pygame.time.get_ticks()
                    speed_up = True

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_LEFT or event.key == K_a:
                    moveLeft = False

                if event.key == K_RIGHT or event.key == K_d:
                    moveRight = False

                if event.key == K_UP or event.key == K_w:
                    moveUp = False

                if event.key == K_DOWN or event.key == K_s:
                    moveDown = False

        asteroidsAddCounter += 1
        if asteroidsAddCounter >= new_asteroid_tick:
            asteroidsAddCounter = 0
            asteroid = Asteroid()
            asteroid.generate()
            asteroids.append(asteroid)

        if moveLeft and player.rect.left > 0:
            player.rect.move_ip(-1 * player.speed, 0)
        if moveRight and player.rect.right < width:
            player.rect.move_ip(player.speed, 0)
        if moveUp and player.rect.top > 0:
            player.rect.move_ip(0, -1 * player.speed)
        if moveDown and player.rect.bottom < height:
            player.rect.move_ip(0, player.speed)

        for a in asteroids:
            a.update()

        for a in asteroids[:]:
            if a.rect.top > height:
                asteroids.remove(a)

        if speed_up:
            if pygame.time.get_ticks() - speedtime <= 5000:
                player.speed_up()
            else:
                speed_up = False
                player.speed_down()
                recharge = True
                rechargetime = pygame.time.get_ticks()

        screen.blit(load_image('background.png'), load_image('background.png').get_rect())

        if recharge:
            if pygame.time.get_ticks() - rechargetime <= 10000:
                write_Text('До перезарядки: %s' % ((10000 - pygame.time.get_ticks() + rechargetime) // 1000 + 1), font, screen, width / 2, 0)
            else:
                rechargetime = 600
                recharge = False

        write_Text('Счёт: %s' % (score), font, screen, 10, 0)
        write_Text('Рекорд: %s' % (topScore), font, screen, 10, 40)

        screen.blit(player.image, player.rect)

        for a in asteroids:
            screen.blit(a.image, a.rect)


        pygame.display.flip()
        clock.tick(fps)

    pygame.mixer.music.stop()
    gameover.play()
    text = font.render("ИГРА ОКОНЧЕНА!", True, (100, 255, 100))
    text_x = width // 3
    text_y = height // 3
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)
    
    pygame.display.flip()
    Key()
    gameover.stop()
