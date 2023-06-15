import pygame as pg

# Klasa statyczna zawierająca niestandardowe zdarzenia, 
# które występują w grze.
class UserEvent():
    SHIP_PICKED = pg.event.custom_type()
    GAME_OVER = pg.event.custom_type()