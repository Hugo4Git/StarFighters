# Jakub Dubiel 339630, Hubert Dyczkowski 338590
# StarFighters, wersja 1.0
# Projekt końcowy, PO

# Klasa statyczna zawierająca niestandardowe zdarzenia, 
# które występują w grze.

import pygame as pg

class UserEvent():
    SHIP_PICKED = pg.event.custom_type()
    GAME_OVER = pg.event.custom_type()