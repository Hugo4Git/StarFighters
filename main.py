import pygame as pg
import pygame
import pygame_gui
from random import uniform
import os
import time

# TODO
# - asteroidy: żeby asteroid pojawiało się coraz więcej z czasem
# - asteroid: żeby leciały coraz szybciej z czasem
# - asteroidy: generować pierwotną pozycję poza ekranem i kierunek tak,
#   by astorida leciała w stronę ekranu
# - wyliczanie rozmiarów obrazków w Asteroid oraz Spaceship

# TODO
# this should be changed, but I don't know where to put this
SHIP_PICKED = pg.event.custom_type()

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
        self.uimanager = pygame_gui.UIManager(self.game.SCREEN_SIZE)

    def process_event(self, event):
        pass
    def update(self, actions):
        self.uimanager.update(self.game.time_delta)
    def render(self, display_surface):
        self.uimanager.draw_ui(self.game.screen)

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

class MenuScreen(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets", "background2.png")) \
                          .convert_alpha()

        # logo
        self.logo_image = \
            pg.image.load(os.path.join("assets", "logo.png")).convert_alpha()

        # tworzenie menu głównego
        button_width, button_height = 400, 70
        gap = 10
        rect = pg.Rect(0, 0, button_width*s, button_height*s)
        rect.centerx = 960*s
        rect.centery = 650*s
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Graj',
            manager=self.uimanager
        )
        rect.centery += (gap + button_height)*s
        self.options_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Opcje',
            manager=self.uimanager
        )
        rect.centery += (gap + button_height)*s
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wyjdź',
            manager=self.uimanager
        )
    
    def play(self):
        new_state = ShipChoiceMenu(self.game)
        new_state.enter_state()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                self.play()
            elif event.ui_element == self.options_button:
                print('Kliknięto opcje')
            elif event.ui_element == self.exit_button:
                self.game.running = False
                self.game.playing = False
        self.uimanager.process_events(event)

    def update(self, actions):
        super().update(actions)
        if actions["start"]:
            print("MenuScreen: pressed start")
            self.play()
        self.game.reset_keys()

    def render(self, display_surface):
        # display_surface.fill((0, 13, 107))
        display_surface.blit(self.background, (0, 0))
        rect = self.logo_image.get_rect(center = (960, 300))
        display_surface.blit(self.logo_image, rect)
        self.game.draw_text(display_surface,
                            "Menu główne. Wciśnij ENTER by zagrać.",
                            'white',
                            self.game.GAME_WIDTH/2,
                            16,
                            self.game.retro_font_20)
        super().render(display_surface)

# Przycisk z obrazkiem w środku
class ImagePanelButton(pygame_gui.elements.UIPanel):
    def __init__(
            self,
            relative_rect,
            manager,
            padding,
            image_surface,
            text,
            container = None
        ):
        pygame_gui.elements.UIPanel.__init__(
            self,
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            margins={ 'top': 0, 'bottom': 0, 'left': 0, 'right': 0 }
        )
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((0, 0), relative_rect.size),
            text=text,
            manager=manager,
            container=self,
        )
        image_rect = pg.Rect(padding/2, padding/2,
                             relative_rect.width - padding,
                             relative_rect.height - padding)
        self.shipimage =  pygame_gui.elements.UIImage(
            relative_rect=image_rect,
            image_surface=image_surface,
            manager=manager,
            container=self
        )
    
    def set_image(self, image_surface):
        self.shipimage.set_image(image_surface)

class ShipChoiceWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect, manager, scale, ships, gap = 30):
        s = scale
        super().__init__(
            rect=rect,
            window_display_title='Wybierz statek',
            manager=manager,
            resizable=False,
            draggable=False,
            visible=False
        )
        super().set_blocking(True)

        # obrazki-przyciski statków
        self.ships = ships
        self.ships_image_buttons = []
        next_x_pos, next_y_pos = gap*s, gap*s
        ship_button_width, ship_button_height = 300, 322
        for ship in ships:
            self.ships_image_buttons.append(ImagePanelButton(
                relative_rect=pg.Rect(next_x_pos, next_y_pos, 
                                      ship_button_width*s,
                                      ship_button_height*s),
                manager=manager,
                container=self,
                padding=30*s,
                image_surface=ship['image_surface'],
                text='',
            ))
            next_x_pos += ship_button_width*s + gap*s
            if (next_x_pos >= rect.width):
                next_x_pos = 0
                next_y_pos += ship_button_width*s + gap*s

        # przycisk do anulowania
        rect = pg.Rect(0, 0, 200*s, 70*s)
        rect.centerx = 960*s
        rect.centery = 950*s
        self.cancel_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Anuluj',
            manager=manager,
            container=self
        )

        self.chosen_ship = None

    def on_close_window_button_pressed(self):
        self.hide()

    def get_ship(self, playerid):
        self.show()
        self.playerid = playerid
    
    def reset(self):
        self.hide()
        self.playerid = None

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.cancel_button:
                print('cancel button')
                self.reset()
            for i, ship in enumerate(self.ships_image_buttons):
                if event.ui_element == ship.button:
                    event_data = {
                        'ship': self.ships[i],
                        'playerid': self.playerid,
                        'ui_element': self,
                        'ui_object_id': self.most_specific_combined_id
                    }
                    pg.event.post(pg.event.Event(SHIP_PICKED, event_data))
                    self.reset()
        super().process_event(event)


class ShipChoiceMenu(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets", "background2.png")) \
                          .convert_alpha()

        # statki
        self.ship_gap = 30
        self.ship_button_width, self.ship_button_height = 300, 322
        rect = pg.Rect(0, 0,
                       self.ship_button_width*s, self.ship_button_height*s)
        rect.center = ((960 - self.ship_button_width - self.ship_gap)*s, 550*s)
        self.player1_ship = ImagePanelButton(
            relative_rect=rect,
            manager=self.uimanager,
            image_surface=self.game.player1_ship['image_surface'],
            padding=30*s,
            text='',
        )
        rect.center = ((960 + self.ship_button_width + self.ship_gap)*s,
                       rect.centery)
        self.player2_ship = ImagePanelButton(
            relative_rect=rect,
            manager=self.uimanager,
            image_surface=self.game.player2_ship['image_surface'],
            padding=30*s,
            text='',
        )

        # przyciski graj i wróć
        button_width, button_height = 400, 70
        gap = 10
        rect = pg.Rect(0, 0, button_width*s, button_height*s)
        rect.topleft = ((960 + gap/2)*s, 950*s)
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Graj',
            manager=self.uimanager
        )
        rect.topright = ((960 - gap/2)*s, rect.topright[1])
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wróć',
            manager=self.uimanager
        )

        self.choice_window = ShipChoiceWindow(
            rect=pg.Rect(0, 0, self.game.GAME_WIDTH*s, self.game.GAME_HEIGHT*s),
            manager=self.uimanager,
            scale=s,
            ships=self.game.SHIPS
        )

    def play(self):
        new_state = GameScreen(self.game)
        new_state.enter_state()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                self.play()
            elif event.ui_element == self.back_button:
                self.exit_state()
            elif event.ui_element == self.player1_ship.button:
                self.choice_window.get_ship(self.game.PLAYER1_ID) 
            elif event.ui_element == self.player2_ship.button:
                self.choice_window.get_ship(self.game.PLAYER2_ID) 
        elif event.type == SHIP_PICKED:
            if (event.playerid == self.game.PLAYER1_ID):
                self.game.player1_ship = event.ship
                self.player1_ship.set_image(event.ship['image_surface'])
            elif (event.playerid == self.game.PLAYER2_ID):
                self.game.player2_ship = event.ship
                self.player1_ship.set_image(event.ship['image_surface'])
            print(f'wybrany statek to {event.ship} dla gracza {event.playerid}')
        self.uimanager.process_events(event)
    
    def render(self, display_surface):
        display_surface.blit(self.background, (0, 0))
        self.game.draw_text(display_surface,
                            "Menu wybierania statku.",
                            'white',
                            self.game.GAME_WIDTH/2,
                            16)
        self.game.draw_text(display_surface,
                            "Statek gracza 1",
                            'azure',
                            960 - self.ship_button_width - self.ship_gap,
                            280,
                            self.game.retro_font_28)
        self.game.draw_text(display_surface,
                            "Statek gracza 2",
                            'azure',
                            960 + self.ship_button_width + self.ship_gap,
                            280,
                            self.game.retro_font_28)
        self.game.draw_text(display_surface,
                            "Wybierzcie swoje statki",
                            'azure',
                            960,
                            140,
                            self.game.retro_font_36)
        super().render(display_surface)

class GameScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.ship = Spaceship(game.GAME_SIZE, game.player1_ship['name'])
        self.asteroid_group = pg.sprite.Group()
        self.background = pg.image.load(
                            os.path.join("assets", "space.png")) \
                          .convert_alpha()

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
        display_surface.blit(self.background, (0, 0))
        self.asteroid_group.draw(display_surface)
        self.ship.draw(display_surface)
        self.game.draw_text(display_surface,
                            "Wciśnij BACKSPACE by wrócić do menu głównego.",
                            'white',
                            self.game.GAME_WIDTH/2,
                            16,
                            self.game.retro_font_20)

class Game():
        def __init__(self):
            pg.init()
            pg.mixer.init()
            pg.mixer.music.load(os.path.join("assets", "bass.wav"))
            pg.mixer.music.play(-1)
            self.GAME_SIZE = self.GAME_WIDTH, self.GAME_HEIGHT = 1920, 1080
            self.SCALE = 2 / 3
            self.SCREEN_SIZE = self.SCREEN_WIDTH, self.SCREEN_HEIGHT = \
                (int(self.GAME_WIDTH * self.SCALE),
                 int(self.GAME_HEIGHT * self.SCALE))
            self.game_canvas = pg.Surface(self.GAME_SIZE)
            self.screen = pg.display.set_mode(self.SCREEN_SIZE)
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
            self.load_players()

            self.FRAME_RATE = 60
            self.clock = pg.time.Clock()


        def game_loop(self):
            while self.playing:
                self.time_delta = self.clock.tick(self.FRAME_RATE)
                self.get_events()
                self.update()
                self.render()

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

                self.state_stack[-1].process_event(event)

        def update(self):
            self.state_stack[-1].update(self.actions)

        def render(self):
            self.screen.blit(pg.transform.smoothscale(self.game_canvas, self.SCREEN_SIZE), (0,0))
            self.state_stack[-1].render(self.game_canvas)
            pg.display.update()

        def draw_text(self, surface, text, color, x, y, font = None):
            if font == None:
                font = self.font
            text_surface = font.render(text, True, color)
            #text_surface.set_colorkey((0,0,0))
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            surface.blit(text_surface, text_rect)

        def load_assets(self):
            # Create pointers to directories 
            self.assets_dir = os.path.join("assets")
            self.font = pg.font.Font(size=30)
            self.retro_font_20 = pg.font.Font(
                                   os.path.join("assets", "PublicPixel.ttf"))
            self.retro_font_28 = pg.font.Font(
                                   os.path.join("assets", "PublicPixel.ttf"),
                                   28)
            self.retro_font_36 = pg.font.Font(
                                   os.path.join("assets", "PublicPixel.ttf"),
                                   36)
            self.SHIPS = [ 
                {
                    'name': 'yellow',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "yellow.png")).
                                        convert_alpha()
                },
                {
                    'name': 'lime',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "lime.png"))
                                        .convert_alpha()
                }
            ]
        
        def load_players(self):
            self.PLAYER1_ID = 0
            self.PLAYER2_ID = 1
            self.player1_ship = self.SHIPS[0]
            self.player2_ship = self.SHIPS[1]

        def load_states(self):
            self.title_screen = MenuScreen(self)
            self.state_stack.append(self.title_screen)

        def reset_keys(self):
            for action in self.actions:
                self.actions[action] = False

        def __del__(self):
            pg.quit()

 
if __name__ == "__main__" :
    game = Game()
    game.game_loop()

