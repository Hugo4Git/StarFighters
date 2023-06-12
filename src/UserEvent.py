import pygame as pg

class UserEvent():
    SHIP_PICKED = pg.event.custom_type()
    GAME_OVER = pg.event.custom_type()