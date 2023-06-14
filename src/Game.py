import pygame as pg
import os

from Screens import MenuScreen

class Game():
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.mixer.music.load(os.path.join("assets", "bass.wav"))
        pg.mixer.music.play(-1)
        self.game_size = self.game_width, self.game_height = 1920, 1080
        self.SCALE = 2 / 3
        self.screen_size = self.screen_width, self.screen_height = \
            (int(self.game_width * self.SCALE),
             int(self.game_height * self.SCALE))
        self.game_canvas = pg.Surface(self.game_size)
        self.screen = pg.display.set_mode(self.screen_size)
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

        self.frame_rate = 60
        self.clock = pg.time.Clock()


    def game_loop(self):
        while self.playing:
            self.time_delta = self.clock.tick(self.frame_rate)
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
        self.screen.blit(pg.transform.smoothscale(self.game_canvas,
                                                  self.screen_size),
                                                  (0,0))
        self.state_stack[-1].render(self.game_canvas)
        pg.display.update()

    def draw_text(self, surface, text, color, x, y, font = None):
        if font == None:
            font = self.font.retro_font_20
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        self.retro_font_20 = pg.font.Font(
                                os.path.join("assets", "PublicPixel.ttf"))
        self.retro_font_28 = pg.font.Font(
                                os.path.join("assets", "PublicPixel.ttf"),
                                28)
        self.retro_font_36 = pg.font.Font(
                                os.path.join("assets", "PublicPixel.ttf"),
                                36)
        ship_names = [
            'yellow',
            'blue',
            'purple',
            'green',
            'red',
            # 'brown',
            'lime',
            'cyan',
            'magenta',
            'xwing-green',
            'xwing-red'
        ]
        self.ships = [
            {
                'name': name,
                'image_surface': pg.image.load(
                                    os.path.join("assets",
                                                    "ships",
                                                    f"{name}.png")).
                                    convert_alpha()
            }
            for name in ship_names
        ]
    
    def load_players(self):
        self.player1_id = 0
        self.player2_id = 1
        self.player1_ship = self.ships[0]
        self.player2_ship = self.ships[1]

    def load_states(self):
        title_screen = MenuScreen(self)
        self.state_stack.append(title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False

    def __del__(self):
        pg.quit()