import pygame as pg
import os
from random import uniform
from UserEvent import UserEvent
import time

# Klasa reprezentująca obiekt latający w kosmosie.
class FlyingObject(pg.sprite.Sprite):
    def __init__(self, image, position, inertia = pg.Vector2(0, 0)):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.position = position
        self.rect.center = position
        self.inertia = inertia.copy()

# Klasa reprezentująca statek kosmiczny.
class Spaceship(FlyingObject):
    def __init__(self, screen, image, controls, playerid):
        position = pg.Vector2(uniform(0, screen.get_width()),
                              uniform(0, screen.get_height()))
        super().__init__(image, position)
        self.original = image
        self.screen = screen
        self.direction = pg.Vector2(0, -1)
        self.angle_speed = 3
        self.angle = 0
        self.friction = 0.98
        self.max_inertia_len = 7
        self.controls = controls
        self.reload = 0
        self.life = 5
        self.playerid = playerid

    # Aktualizacja pozycji statku, wykrywanie kolizji z innymi obiektami.
    def update(self, actions, bullets, asteroids, bangs):
        if (actions[self.controls[0]]):
            self.inertia += self.direction * 0.2
        if(actions[self.controls[1]]):
            self.angle += self.angle_speed
            self.direction.rotate_ip(-self.angle_speed)
        if (actions[self.controls[2]]):
            self.inertia -= self.direction * 0.1
        if(actions[self.controls[3]]):
            self.angle -= self.angle_speed
            self.direction.rotate_ip(self.angle_speed)
        if(actions[self.controls[4]] and self.reload + 0.5 < time.time()):
            bullets.add(Bullet(self.screen,
                               self.position.copy(),
                               self.direction.copy()))
            self.reload = time.time()
        if (self.inertia.length() > self.max_inertia_len):
            self.inertia *= self.max_inertia_len / self.inertia.length()
        self.position += self.inertia
        self.inertia *= self.friction
        self.position[0] %= self.screen.get_width()
        self.position[1] %= self.screen.get_height()
        self.image = pg.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center = self.position)

        colisions = len(pg.sprite.spritecollide(self, bullets, True)) 
        colisions += len(pg.sprite.spritecollide(self, asteroids, True))
        if colisions:
            self.life -= colisions
            bangs.add(Bang(self.position))
            if self.life <= 0:
                self.kill()
                event_data = { 'killed_playerid': self.playerid }
                pg.event.post(pg.event.Event(UserEvent.GAME_OVER, event_data))

# Klasa reprezentująca pocisk.
class Bullet(FlyingObject):
    def __init__(self, screen, position, direction):
        image = \
            pg.image.load(os.path.join("assets", "bullet.png")).convert_alpha()
        super().__init__(image, position + direction*100, direction*8)
        self.screen = screen

    # Aktualizacjia pozycji i wykrywanie kolizji.
    def update(self, asteroids):
        self.rect.center += self.inertia
        if (
            self.rect.centerx < -self.rect.width or
            self.rect.centery < -self.rect.height or
            self.rect.centerx > self.screen.get_width() + self.rect.width or
            self.rect.centery > self.screen.get_height() + self.rect.height
        ):
            self.kill()
        if pg.sprite.spritecollide(self, asteroids, True):
            self.kill()

# Klasa reprezentująca asteroidę.
class Asteroid(FlyingObject):
    def __init__(self, screen_size):
        image = pg.image.load(os.path.join("assets", "asteroid.png"))
        inertia = pg.Vector2(uniform(-0.8, 0.8), uniform(0.2, 1))
        super().__init__(image, (0, 0), inertia)
        self.screen_size = screen_size
        s = 80 * uniform(0.9, 1.1)
        size = (s, s)
        self.image = pg.transform.scale(self.image, size)

        self.rect = self.image.get_rect()
        self.rect.center = (uniform(0, screen_size[0]), 0)

        MIN_INERTIA_LENGTH = 2
        MAX_INERTIA_LENGTH = 4
        inertia_length = uniform(MIN_INERTIA_LENGTH, MAX_INERTIA_LENGTH)
        self.inertia.scale_to_length(inertia_length) 

    # Aktualizacja pozycji.
    def update(self):
        if (
            self.rect.centerx < -self.rect.width or
            self.rect.centery < -self.rect.height or
            self.rect.centerx > self.screen_size[0] + self.rect.width or
            self.rect.centery > self.screen_size[1] + self.rect.height
        ):
            self.kill()
        self.rect.center += self.inertia

# Klasa reprezentująca wybuch.
class Bang(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.images = [pg.image.load(x) for x in 
                       [os.path.join("assets", "bang.png"),
                       os.path.join("assets", "smallbang.png"),
                       os.path.join("assets", "supersmallbang.png")]]
        self.image = self.images[2]
        self.stime = time.time()
        self.rect = self.image.get_rect(center = position)

    # Zmiana wyglądu wybuchu zależnie od czasu.
    def update(self):
        if time.time() > self.stime + 0.1:
            self.image = self.images[1]
        if time.time() > self.stime + 0.2:
            self.image = self.images[0]
        if time.time() > self.stime + 0.3:
            self.kill()