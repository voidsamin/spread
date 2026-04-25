from __future__ import annotations

import os
import pygame
import config


class HospitalMap:
    """Manages the game world background (hospital floor).

    Loads the floor image once, scales it to the screen dimensions,
    and provides a draw method to blit it each frame.
    """

    def __init__(self) -> None:
        path = os.path.join(
            os.path.dirname(__file__), "components", "Map", "floor.png"
        )
        raw = pygame.image.load(path).convert()
        self.surface = pygame.transform.smoothscale(raw, (config.WIDTH, config.HEIGHT))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the floor background at (0, 0)."""
        surface.blit(self.surface, (0, 0))
