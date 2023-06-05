import pygame as pg
from random import uniform
import os

# TODO
# - asteroidy: żeby asteroid pojawiało się coraz więcej z czasem
# - asteroid: żeby leciały coraz szybciej z czasem
# - asteroidy: generować pierwotną pozycję poza ekranem i kierunek tak,
#   by astorida leciała w stronę ekranu
# - wyliczanie rozmiarów obrazków w Asteroid oraz Spaceship

class Asteroid(pg.sprite.Sprite):
    def __init__(self, screen_size, images_paths=[os.path.join("assets", "asteroid.png")]):
        super().__init__()
        self._screen_size = screen_size
        self.image = pg.image.load(images_paths[0])
        s = 80 * uniform(0.9, 1.1)
        size = (s, s)
        self.image = pg.transform.scale(self.image, size)

        self.rect = self.image.get_rect()
        self.rect.center = (uniform(0, screen_size[0]), uniform(0, screen_size[1]))

        self._inertia = pg.Vector2(uniform(-1, 1), uniform(-1, 1))
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
    def __init__(self, screen_size, color):
        #size = (80, 80)
        self.image = pg.image.load(os.path.join("assets", color + ".png"))
        #self.image = pg.transform.scale(self.image, size)
        self.position = pg.Vector2(screen_size[0]/2, screen_size[1]/2)
        self.direction = pg.Vector2(0, -1)
        self.inertia = pg.Vector2(0, 0)
        self.angle_speed = 2
        self.angle = 0
        self._FRICTION = 0.98
        self._MAX_INERTIA_LEN = 7

    def draw(self, display_surface):
        rotated_image = pg.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center = self.position)
        display_surface.blit(rotated_image, rect)

        # print(rect)
        # rysowanie pozycji
        # pg.draw.circle(display_surface, 'red', self.position, 3)
        # rysowanie direction
        # pg.draw.line(display_surface, 'red', self.position, self.position + self.direction * 50, 2)
        # rysowanie inertia
        # pg.draw.line(display_surface, 'blue', self.position, self.position + self.inertia * 50, 2)
    
    def move(self, screen_width, screen_height, actions):
        if(actions["left"]):
            self.angle += self.angle_speed
            self.direction.rotate_ip(-self.angle_speed)

        if(actions["right"]):
            self.angle -= self.angle_speed
            self.direction.rotate_ip(self.angle_speed)

        if (actions["up"]):
            self.inertia += self.direction * 0.1

        if (actions["down"]):
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

# klasa abstrakcyjna
class State():
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, actions):
        pass
    def render(self, display_surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

class MenuScreen(State):
    def __init__(self, game):
        State.__init__(self, game)

    def update(self, actions):
        if actions["start"]:
            print("MenuScreen: pressed start")
            new_state = GameScreen(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display_surface):
        display_surface.fill('green')
        self.game.draw_text(display_surface,
                            "Menu główne. Wciśnij ENTER by zagrać.",
                            'black',
                            self.game.GAME_WIDTH/2,
                            self.game.GAME_HEIGHT/2)

class GameScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.ship = Spaceship(game.GAME_SIZE, "yellow")
        self.asteroid_group = pg.sprite.Group()
        self.background_image = pg.image.load(os.path.join("assets", "space.png"))

    def update(self, actions):
        if actions["back"]:
            print("GameScreen: pressed back")
            self.exit_state()
        if actions["asteroids"]:
            print("GameScreen: Adding asteroids")
            self.asteroid_group.add(Asteroid(self.game.GAME_SIZE))

        self.asteroid_group.update()
        self.ship.move(game.GAME_WIDTH, game.GAME_HEIGHT, actions)

        # to resetuje klawisze w każdej klatce co powoduje że trzymanie 
        # klawiszy nie rusza statku
        # self.game.reset_keys()

    def render(self, display_surface):
        display_surface.fill('black')
        self.asteroid_group.draw(display_surface)
        self.ship.draw(display_surface)
        self.game.draw_text(display_surface,
                            "Wciśnij BACKSPACE by wrócić do menu głównego.",
                            'white',
                            self.game.GAME_WIDTH/2,
                            16)

class Game():
        def __init__(self):
            pg.init()
            self.GAME_SIZE = self.GAME_WIDTH, self.GAME_HEIGHT = 1200, 800
            self.SCREEN_SIZE = self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1200, 800
            self.game_canvas = pg.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
            self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.running, self.playing = True, True
            self.actions = {
                "left": False, 
                "right": False, 
                "up" : False,
                "down" : False,
                "action1" : False,
                "action2" : False,
                "start" : False,
                "back" : False,
                "asteroids" : False
            }
            self.state_stack = []
            self.load_assets()
            self.load_states()

            self.FRAME_RATE = 60
            self.clock = pg.time.Clock()

        def game_loop(self):
            while self.playing:
                self.get_events()
                self.update()
                self.render()
                self.clock.tick(self.FRAME_RATE)

        def get_events(self):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.playing = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.playing = False
                        self.running = False
                    if event.key == pg.K_a or event.key == pg.K_LEFT:
                        self.actions['left'] = True
                    if event.key == pg.K_d or event.key == pg.K_RIGHT:
                        self.actions['right'] = True
                    if event.key == pg.K_w or event.key == pg.K_UP:
                        self.actions['up'] = True
                    if event.key == pg.K_s or event.key == pg.K_DOWN:
                        self.actions['down'] = True
                    if event.key == pg.K_p:
                        self.actions['action1'] = True
                    if event.key == pg.K_o:
                        self.actions['action2'] = True    
                    if event.key == pg.K_RETURN:
                        self.actions['start'] = True  
                    if event.key == pg.K_BACKSPACE:
                        self.actions['back'] = True
                    if event.key == pg.K_q:
                        self.actions['asteroids'] = True    

                if event.type == pg.KEYUP:
                    if event.key == pg.K_a or event.key == pg.K_LEFT:
                        self.actions['left'] = False
                    if event.key == pg.K_d or event.key == pg.K_RIGHT:
                        self.actions['right'] = False
                    if event.key == pg.K_w or event.key == pg.K_UP:
                        self.actions['up'] = False
                    if event.key == pg.K_s or event.key == pg.K_DOWN:
                        self.actions['down'] = False
                    if event.key == pg.K_p:
                        self.actions['action1'] = False
                    if event.key == pg.K_o:
                        self.actions['action2'] = False
                    if event.key == pg.K_RETURN:
                        self.actions['start'] = False  
                    if event.key == pg.K_BACKSPACE:
                        self.actions['back'] = False
                    if event.key == pg.K_q:
                        self.actions['asteroids'] = False

        def update(self):
            self.state_stack[-1].update(self.actions)

        def render(self):
            self.state_stack[-1].render(self.game_canvas)
            # Render current state to the screen
            self.screen.blit(pg.transform.scale(self.game_canvas,(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0,0))
            pg.display.update()

        def draw_text(self, surface, text, color, x, y):
            text_surface = self.font.render(text, True, color)
            #text_surface.set_colorkey((0,0,0))
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            surface.blit(text_surface, text_rect)

        def load_assets(self):
            # Create pointers to directories 
            self.assets_dir = os.path.join("assets")
            self.font = pg.font.Font(size=30)

        def load_states(self):
            self.title_screen = MenuScreen(self)
            self.state_stack.append(self.title_screen)

        def reset_keys(self):
            for action in self.actions:
                self.actions[action] = False

 
if __name__ == "__main__" :
    game = Game()
    game.game_loop()

