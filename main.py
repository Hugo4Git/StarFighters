from pygame.locals import *
from pygame.math import Vector2
from random import uniform
import os
import pygame

# TODO
# - asteroidy: żeby asteroid pojawiało się coraz więcej z czasem
# - asteroid: żeby leciały coraz szybciej z czasem
# - asteroidy: generować pierwotną pozycję poza ekranem i kierunek tak,
#   by astorida leciała w stronę ekranu

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_size, images_paths=[os.path.join("assets", "asteroid.png")]):
        super().__init__()
        self._screen_size = screen_size
        self.image = pygame.image.load(images_paths[0])
        s = 80 * uniform(0.9, 1.1)
        size = (s, s)
        self.image = pygame.transform.scale(self.image, size)

        self.rect = self.image.get_rect()
        self.rect.center = (uniform(0, screen_size[0]), uniform(0, screen_size[1]))

        self._inertia = Vector2(uniform(-1, 1), uniform(-1, 1))
        MIN_INERTIA_LENGTH = 2
        MAX_INERTIA_LENGTH = 4
        inertia_length = uniform(MIN_INERTIA_LENGTH, MAX_INERTIA_LENGTH)
        self._inertia.scale_to_length(inertia_length) 

    def update(self):
        if (
            self.rect.centerx < -self.rect.width or
            self.rect.centery < -self.rect.height or
            self.rect.centerx > self._screen_size[0] + self.rect.width or
            self.rect.centery > self._screen_size[1] + self.rect.height
        ):
            self.kill()
        self.rect.center += self._inertia

class Spaceship: # TODO: should inherit from sprite?
    def __init__(self, image_path=os.path.join("assets", "ship.png")):
        size = (80, 80)
        self.original_image = pygame.image.load(image_path)
        self.original_image = pygame.transform.scale(self.original_image, size)
        self.position = Vector2(0, 0)
        self.direction = Vector2(0, -1)
        self.inertia = Vector2(0, 0)
        self.angle_speed = 2
        self.angle = 0
        self._FRICTION = 0.995
        self._MAX_INERTIA_LEN = 7

    def draw(self, display_surface):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated_image.get_rect(center = self.position)
        display_surface.blit(rotated_image, rect)

        # print(rect)
        # pygame.draw.circle(display_surface, 'red', self.position, 3)

        # pygame.draw.line(display_surface, 'red', self.position, self.position + self.direction * 50, 2)
        # pygame.draw.line(display_surface, 'blue', self.position, self.position + self.inertia * 50, 2)
    
    def move (self, screen_width, screen_height):
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_LEFT] or keys[ord('a')]): # and self.position[0] > 0:
            self.angle += self.angle_speed
            self.direction.rotate_ip(-self.angle_speed)

        if (keys[pygame.K_RIGHT] or keys[ord('d')]): # and self.position[0] < width - self.width:
            self.angle -= self.angle_speed
            self.direction.rotate_ip(self.angle_speed)

        if (keys[pygame.K_UP] or keys[ord('w')]): # and self.position[1] > 0:
            # self.position += self.direction * self.speed
            self.inertia += self.direction * 0.1

        if (keys[pygame.K_DOWN] or keys[ord('s')]): # and self.position[1] < height - self.height:
            self.inertia -= self.direction * 0.05

        # max inertia
        if (self.inertia.length() > self._MAX_INERTIA_LEN):
            self.inertia *= self._MAX_INERTIA_LEN / self.inertia.length()

        # move according to inertia
        self.position += self.inertia

        # apply friction
        self.inertia *= self._FRICTION

        self.position[0] %= screen_width
        self.position[1] %= screen_height
 
class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1200, 800
        self.ship = Spaceship()
        self.FRAME_RATE = 60
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE
                                                     | pygame.DOUBLEBUF)
        self._running = True
        self.clock = pygame.time.Clock()

        self.asteroid_group = pygame.sprite.Group()
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        keys = pygame.key.get_pressed()
        if keys[ord('q')]:
            self.asteroid_group.add(Asteroid(self.size))
        
        self.asteroid_group.update()
        self.ship.move(self.width, self.height)

        print(self.asteroid_group)
    
    def on_render(self):
        self._display_surf.fill('black')
        self.asteroid_group.draw(self._display_surf)
        self.ship.draw(self._display_surf)
        pygame.display.update() # or flip()
        self.clock.tick(self.FRAME_RATE)

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

