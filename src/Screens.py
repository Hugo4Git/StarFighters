# Jakub Dubiel 339630, Hubert Dyczkowski 338590
# StarFighters, wersja 1.0
# Projekt końcowy, PO

# Klasy reprezentujące poszczególne ekrany w grze.

import pygame as pg
import pygame_gui
import os
import time

from ImagePanelButton import ImagePanelButton
from UserEvent import UserEvent
from GameObjects import Spaceship
from GameObjects import Asteroid

# Klasa abstrakcyjna reprezentująca stan programu. Wykorzystywana do tworzenia
# ekranów (menu głównego, menu wyboru statków etc.).
class State():
    def __init__(self, game):
        self.game = game
        self.prev_state = None
        self.uimanager = pygame_gui.UIManager(self.game.screen_size,
                           os.path.join("themes", "theme.json"))

    # Metoda przetwarzająca zdarzenia (np. kliknięcia przycisków,
    # naciśnięcia klawiszy).
    def process_event(self, event):
        pass

    # Aktualizuje stan obiektów na ekranie (np. zmienia pozycję statków).
    def update(self, actions):
        self.uimanager.update(self.game.time_delta)

    # Rysuje na ekranie to, co powinno być widoczne dla użytkownika.
    def render(self, display_surface):
        self.uimanager.draw_ui(self.game.screen)

    # Zmienia globalny stan programu, otwierając nowy ekran.
    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    # Zamyka ekran.
    def exit_state(self, count=1):
        for i in range(count):
            self.game.state_stack.pop()

# Ekran, na którym znajduje się instrukcja sterowania grą.
class ControlsScreen(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets",
                                         "backgrounds",
                                         "background.png")).convert_alpha()

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
                            os.path.join("assets",
                                         "controls.png")).convert_alpha()
        display_surface.blit(controls_image, (0, 0))
        super().render(display_surface)

# Ekran końca gry. Pokazuje, który gracz wygrał i jaki statek pilotował.
class GameOverScreen(State):
    def __init__(self, game, winnerid):
        super().__init__(game)
        s = self.game.SCALE
        self.winnerid = winnerid

        button_width, button_height = 400, 70
        rect = pg.Rect(0, 0, button_width*s, button_height*s)
        rect.centerx = 960*s
        rect.centery = 680*s
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
        if playerid == self.game.player1_id:
            return "gracz 1"
        elif playerid == self.game.player2_id:
            return "gracz 2"

    def get_ship(self, playerid):
        if playerid == self.game.player1_id:
            return self.game.player1_ship
        elif playerid == self.game.player2_id:
            return self.game.player2_ship

    def render(self, display_surface):
        bg_rect = pg.Rect(0, 0, 950, 430)
        bg_rect.center = (self.game.game_width/2, self.game.game_height/2 + 10)
        bg_color = 'azure'
        pg.draw.rect(display_surface, bg_color, bg_rect)

        message = f'Wygrał {self.playerid_to_name(self.winnerid)} statkiem:'
        self.game.draw_text(display_surface,
                            message,
                            'black',
                            self.game.game_width/2,
                            400,
                            self.game.retro_font_36)

        ship_width, ship_height = 150, 161
        rect = pg.Rect(0, 0, ship_width, ship_height)
        rect.center = (self.game.game_width/2, self.game.game_height/2)
        scaled_ship = pg.transform.smoothscale( 
            self.get_ship(self.winnerid)['image_surface'],
            (ship_width, ship_height)
        )
        display_surface.blit(scaled_ship, rect)
        super().render(display_surface)

# Ekran głównego menu gry. Jego głównym zadaniem jest otwieranie odpowiednich,
# nowych ekranów po kliknięciu przycisku z menu lub wciśnięciu klawisza.
class MenuScreen(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets",
                                         "backgrounds",
                                         "background.png")).convert_alpha()

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
        new_state = ShipChoiceScreen(self.game)
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
        super().render(display_surface)

# Okno wyświetlane na ekranie wyboru statków (ShipChoiceScreen), pozwalające
# graczowi wybrać inny statek.
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

        # Utworzenie obrazków-przycisków statków.
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

        # Utworzenie przycisku do anulowania wyboru.
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

    # Nadpisanie metody z klasy okna (UIWindow), by stawało się ukryte,
    # ale nie było niszczone przy naciśnięciu przycisku 'X'.
    def on_close_window_button_pressed(self):
        self.hide()

    # Wyświetla okno.
    def get_ship(self, playerid):
        self.show()
        self.playerid = playerid
    
    # Ukrywa okno.
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
                    pg.event.post(pg.event.Event(UserEvent.SHIP_PICKED,
                                                 event_data))
                    self.reset()
        super().process_event(event)

# Ekran wyboru statków. Po kliknięciu na statek otwiera okno, w którym gracz
# może go zmienić. Po kliknięciu przycisku "Graj" otwiera ekran właściwej gry.
class ShipChoiceScreen(State):
    def __init__(self, game):
        super().__init__(game)
        s = self.game.SCALE

        # tło
        self.background = pg.image.load(
                            os.path.join("assets",
                                         "backgrounds",
                                         "background.png")).convert_alpha()

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
            rect=pg.Rect(0, 0, self.game.game_width*s, self.game.game_height*s),
            manager=self.uimanager,
            scale=s,
            ships=self.game.ships
        )

    # Przechodzi do ekranu rozgrywki.
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
                self.choice_window.get_ship(self.game.player1_id) 
            elif event.ui_element == self.player2_ship.button:
                self.choice_window.get_ship(self.game.player2_id) 
        elif event.type == UserEvent.SHIP_PICKED:
            if (event.playerid == self.game.player1_id):
                self.game.player1_ship = event.ship
                self.player1_ship.set_image(event.ship['image_surface'])
            elif (event.playerid == self.game.player2_id):
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

# Ekran rozgrywki. Tworzy statki, asteroidy i inne obiekty występujące w grze.
# Po zniszczeniu jednego ze statków otwiera ekran końca gry (GameOverScreen).
class GameScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.ships = pg.sprite.Group()
        self.ships.add(Spaceship(game.game_canvas,
                                 game.player1_ship['image_surface'], 
                                 ['w', 'a', 's', 'd', 'q'],
                                 game.player1_id))
        self.ships.add(Spaceship(game.game_canvas,
                                 game.player2_ship['image_surface'], 
                                 ['up', 'left', 'down', 'right', 'space'],
                                 game.player2_id))
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.bangs = pg.sprite.Group()
        self.background = pg.image.load(
                            os.path.join("assets",
                                         "backgrounds",
                                         "space.png")).convert_alpha()
        self.last_asteroid = 0

    def game_over(self, loser_id):
        winner_id = self.game.player2_id \
                    if loser_id == self.game.player1_id \
                    else self.game.player1_id
        new_state = GameOverScreen(self.game, winner_id)
        new_state.enter_state()

    def process_event(self, event):
        if event.type == UserEvent.GAME_OVER:
            self.game_over(event.killed_playerid)

    def update(self, actions):
        if actions["back"]:
            self.game.reset_keys()
            self.exit_state()
        if int(time.time()) > self.last_asteroid:
            self.asteroids.add(Asteroid(self.game.game_size))
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
