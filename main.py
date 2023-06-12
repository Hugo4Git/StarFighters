import pygame as pg
import pygame_gui
from random import uniform
import os
import time

class UserEvent():
    SHIP_PICKED = pg.event.custom_type()
    GAME_OVER = pg.event.custom_type()

class Spaceship(pg.sprite.Sprite):
    def __init__(self, screen, color, controls, playerid):
        super().__init__()
        self.original = color
        self.image = self.original
        self.screen = screen
        self.position = pg.Vector2(uniform(0, screen.get_width()),
                                   uniform(0, screen.get_height()))
        self.direction = pg.Vector2(0, -1)
        self.inertia = pg.Vector2(0, 0)
        self.angle_speed = 3
        self.angle = 0
        self._FRICTION = 0.98
        self._MAX_INERTIA_LEN = 7
        self.controls = controls
        self.reload = 0
        self.life = 5
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.playerid = playerid

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
            bullets.add(Bullet(self.screen, self.position.copy(), self.direction.copy()))
            self.reload = time.time()
        if (self.inertia.length() > self._MAX_INERTIA_LEN):
            self.inertia *= self._MAX_INERTIA_LEN / self.inertia.length()
        self.position += self.inertia
        self.inertia *= self._FRICTION
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

class Bullet(pg.sprite.Sprite):
    def __init__(self, screen, position, direction):
        super().__init__()
        self.image = pg.image.load(os.path.join("assets", "bullet.png")).convert_alpha()
        self.screen = screen
        self.position = position + direction*100
        self.inertia = direction*8
        self.rect = self.image.get_rect()
        self.rect.center = self.position

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

class Asteroid(pg.sprite.Sprite):
    def __init__(self, screen_size, images_paths=[os.path.join("assets", "asteroid.png")]):
        super().__init__()
        self._screen_size = screen_size
        self.image = pg.image.load(images_paths[0])
        s = 80 * uniform(0.9, 1.1)
        size = (s, s)
        self.image = pg.transform.scale(self.image, size)

        self.rect = self.image.get_rect()
        self.rect.center = (uniform(0, screen_size[0]), 0)

        self._inertia = pg.Vector2(uniform(-0.8, 0.8), uniform(0.2, 1))
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

class Bang(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.images = [pg.image.load(x) for x in [os.path.join("assets", "bang.png"),
                       os.path.join("assets", "smallbang.png"),
                       os.path.join("assets", "supersmallbang.png")]]
        self.image = self.images[2]
        self.stime = time.time()
        self.rect = self.image.get_rect(center = position)

    def update(self):
        if time.time() > self.stime + 0.1:
            self.image = self.images[1]
        if time.time() > self.stime + 0.2:
            self.image = self.images[0]
        if time.time() > self.stime + 0.3:
            self.kill()




# klasa abstrakcyjna
class State():
    def __init__(self, game):
        self.game = game
        self.prev_state = None
        self.uimanager = pygame_gui.UIManager(self.game.SCREEN_SIZE,
                                              os.path.join("themes", "theme.json"))

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

    def exit_state(self, count=1):
        for i in range(count):
            self.game.state_stack.pop()

class ControlsScreen(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets", "background2.png")) \
                          .convert_alpha()

        button_width, button_height = 400, 70
        rect = pg.Rect(0, 0, button_width*s, button_height*s)
        rect.centerx = 510*s
        rect.centery = 850*s
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wróć',
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )
    
    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                self.exit_state()
        self.uimanager.process_events(event)

    def update(self, actions):
        super().update(actions)
        if actions["back"]:
            self.game.reset_keys()
            self.exit_state()
        self.game.reset_keys()

    def render(self, display_surface):
        display_surface.blit(self.background, (0, 0))
        controls_image = pg.image.load(
                            os.path.join("assets", "controls.png")) \
                          .convert_alpha()
        display_surface.blit(controls_image, (0, 0))
        super().render(display_surface)

class GameOverScreen(State):
    def __init__(self, game, winnerid):
        super().__init__(game)
        s = self.game.SCALE
        self.winnerid = winnerid

        button_width, button_height = 400, 70
        rect = pg.Rect(0, 0, button_width*s, button_height*s)
        rect.centerx = 960*s
        rect.centery = 600*s
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wróć do menu',
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )

    def exit_screen(self):
        self.exit_state(2)
    
    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                self.exit_screen()
        self.uimanager.process_events(event)

    def update(self, actions):
        super().update(actions)
        if actions["start"] or actions["back"]:
            self.game.reset_keys()
            self.exit_screen()
        self.game.reset_keys()
    
    def playerid_to_name(self, playerid):
        if playerid == self.game.PLAYER1_ID:
            return "Gracz 1"
        elif playerid == self.game.PLAYER2_ID:
            return "Gracz 2"

    def render(self, display_surface):
        bg_rect = pg.Rect(0, 0, 600, 230)
        bg_rect.center = (self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 20)
        bg_color = (2, 27, 136)
        pg.draw.rect(display_surface, bg_color, bg_rect)
        self.game.draw_text(display_surface,
                            f'Wygrał {self.playerid_to_name(self.winnerid)}',
                            'white',
                            self.game.GAME_WIDTH/2,
                            500,
                            self.game.retro_font_36)
        super().render(display_surface)

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
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )
        rect.centery += (gap + button_height)*s
        self.controls_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Sterowanie',
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )
        rect.centery += (gap + button_height)*s
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wyjdź',
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )
    
    def play(self):
        new_state = ShipChoiceMenu(self.game)
        new_state.enter_state()

    def controls(self):
        new_state = ControlsScreen(self.game)
        new_state.enter_state()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                self.play()
            elif event.ui_element == self.controls_button:
                self.controls()
            elif event.ui_element == self.exit_button:
                self.game.running = False
                self.game.playing = False
        self.uimanager.process_events(event)

    def update(self, actions):
        super().update(actions)
        if actions["start"]:
            self.game.reset_keys()
            self.play()
        self.game.reset_keys()

    def render(self, display_surface):
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
        x_gap = 77
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
            next_x_pos += ship_button_width*s + x_gap*s
            if (next_x_pos + ship_button_width*s >= rect.width - gap*s):
                next_x_pos = gap*s
                next_y_pos += ship_button_height*s + gap*s

        # przycisk do anulowania
        rect = pg.Rect(0, 0, 200*s, 70*s)
        rect.centerx = 960*s
        rect.centery = 950*s
        self.cancel_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Anuluj',
            manager=manager,
            container=self,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
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
                self.reset()
            for i, ship in enumerate(self.ships_image_buttons):
                if event.ui_element == ship.button:
                    event_data = {
                        'ship': self.ships[i],
                        'playerid': self.playerid,
                        'ui_element': self,
                        'ui_object_id': self.most_specific_combined_id
                    }
                    pg.event.post(pg.event.Event(UserEvent.SHIP_PICKED, event_data))
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
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
        )
        rect.topright = ((960 - gap/2)*s, rect.topright[1])
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text='Wróć',
            manager=self.uimanager,
            object_id=pygame_gui.core.ObjectID(class_id='@menu_buttons')
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
        elif event.type == UserEvent.SHIP_PICKED:
            if (event.playerid == self.game.PLAYER1_ID):
                self.game.player1_ship = event.ship
                self.player1_ship.set_image(event.ship['image_surface'])
            elif (event.playerid == self.game.PLAYER2_ID):
                self.game.player2_ship = event.ship
                self.player2_ship.set_image(event.ship['image_surface'])
        self.uimanager.process_events(event)

    def update(self, actions):
        super().update(actions)
        if actions["start"]:
            self.game.reset_keys()
            self.play()
        elif actions["back"]:
            self.game.reset_keys()
            self.exit_state()
        self.game.reset_keys()

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
        self.ships = pg.sprite.Group()
        self.ships.add(Spaceship(game.game_canvas, game.player1_ship['image_surface'], 
                                 ['w', 'a', 's', 'd', 'q'],
                                 game.PLAYER1_ID))
        self.ships.add(Spaceship(game.game_canvas, game.player2_ship['image_surface'], 
                                 ['up', 'left', 'down', 'right', 'space'],
                                 game.PLAYER2_ID))
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.bangs = pg.sprite.Group()
        self.background = pg.image.load(
                            os.path.join("assets", "space.png")) \
                          .convert_alpha()
        self.last_asteroid = 0

    def game_over(self, loser_id):
        winner_id = self.game.PLAYER2_ID \
                    if loser_id == self.game.PLAYER1_ID \
                    else self.game.PLAYER1_ID
        new_state = GameOverScreen(game, winner_id)
        new_state.enter_state()

    def process_event(self, event):
        if event.type == UserEvent.GAME_OVER:
            self.game_over(event.killed_playerid)

    def update(self, actions):
        if actions["back"]:
            self.game.reset_keys()
            self.exit_state()
        if int(time.time()) > self.last_asteroid:
            self.asteroids.add(Asteroid(self.game.GAME_SIZE))
            self.last_asteroid = int(time.time())

        self.ships.update(actions, self.bullets, self.asteroids, self.bangs)
        self.bullets.update(self.asteroids)
        self.asteroids.update()
        self.bangs.update()

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        self.ships.draw(screen)
        self.bullets.draw(screen)
        self.asteroids.draw(screen)
        self.bangs.draw(screen)
        self.game.draw_text(screen,
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
                "up" : False,
                "left": False, 
                "down" : False,
                "right": False, 
                "w" : False,
                "a" : False,
                "s" : False,
                "d" : False,
                "a" : False,
                "q" : False,
                "space" : False,
                "start" : False,
                "back" : False,
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
                    if event.key == pg.K_LEFT:
                        self.actions['left'] = True
                    if event.key == pg.K_RIGHT:
                        self.actions['right'] = True
                    if event.key == pg.K_UP:
                        self.actions['up'] = True
                    if event.key == pg.K_DOWN:
                        self.actions['down'] = True
                    if event.key == pg.K_SPACE:
                        self.actions['space'] = True
                    if event.key == pg.K_w:
                        self.actions['w'] = True
                    if event.key == pg.K_a:
                        self.actions['a'] = True
                    if event.key == pg.K_s:
                        self.actions['s'] = True
                    if event.key == pg.K_d:
                        self.actions['d'] = True
                    if event.key == pg.K_q:
                        self.actions['q'] = True
                    if event.key == pg.K_p:
                        self.actions['action1'] = True
                    if event.key == pg.K_o:
                        self.actions['action2'] = True    
                    if event.key == pg.K_RETURN:
                        self.actions['start'] = True  
                    if event.key == pg.K_BACKSPACE:
                        self.actions['back'] = True  
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.actions['left'] = False
                    if event.key == pg.K_RIGHT:
                        self.actions['right'] = False
                    if event.key == pg.K_UP:
                        self.actions['up'] = False
                    if event.key == pg.K_DOWN:
                        self.actions['down'] = False
                    if event.key == pg.K_SPACE:
                        self.actions['space'] = False
                    if event.key == pg.K_w:
                        self.actions['w'] = False
                    if event.key == pg.K_a:
                        self.actions['a'] = False
                    if event.key == pg.K_s:
                        self.actions['s'] = False
                    if event.key == pg.K_d:
                        self.actions['d'] = False
                    if event.key == pg.K_q:
                        self.actions['q'] = False
                    if event.key == pg.K_p:
                        self.actions['action1'] = False
                    if event.key == pg.K_o:
                        self.actions['action2'] = False
                    if event.key == pg.K_RETURN:
                        self.actions['start'] = False  
                    if event.key == pg.K_BACKSPACE:
                        self.actions['back'] = False

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
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            surface.blit(text_surface, text_rect)

        def load_assets(self):
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
                    'name': 'blue',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "blue.png")).
                                        convert_alpha()
                },
                {
                    'name': 'purple',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "purple.png")).
                                        convert_alpha()
                },
                {
                    'name': 'green',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "green.png")).
                                        convert_alpha()
                },
                {
                    'name': 'red',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "red.png")).
                                        convert_alpha()
                },
                {
                    'name': 'brown',
                    'image_surface': pg.image.load(
                                        os.path.join("assets", "brown.png")).
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

