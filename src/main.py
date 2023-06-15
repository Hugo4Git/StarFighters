# Jakub Dubiel 339630, Hubert Dyczkowski 338590
# StarFighters, wersja 1.0
# Projekt końcowy, PO

# Plik uruchamiający program.

from Game import Game

# Punkt wejściowy programu. Tworzy obiekt gry i ją uruchamia.
if __name__ == "__main__" :
    game = Game()
    game.game_loop()

