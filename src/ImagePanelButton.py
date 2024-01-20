# Jakub Dubiel 339630, Hubert Dyczkowski 338590
# StarFighters, wersja 1.0
# Projekt końcowy, PO

# Przycisk z obrazkiem.

import pygame as pg
import pygame_gui

# Przycisk z obrazkiem w środku.
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
        # Utworzenie panelu.
        pygame_gui.elements.UIPanel.__init__(
            self,
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            margins={ 'top': 0, 'bottom': 0, 'left': 0, 'right': 0 }
        )
        # Utworzenie przycisku w środku panelu.
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((0, 0), relative_rect.size),
            text=text,
            manager=manager,
            container=self,
        )
        # Utworzenie obrazka w środku panelu.
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