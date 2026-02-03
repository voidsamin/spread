from __future__ import annotations

from dataclasses import dataclass
import pygame
import config


@dataclass
class Projectile:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int
    life: float  # seconds remaining

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.life -= dt

    def is_dead(self) -> bool:
        # Dead if lifetime expired or goes off-screen
        if self.life <= 0:
            return True
        if self.pos.x < -50 or self.pos.x > config.WIDTH + 50:
            return True
        if self.pos.y < -50 or self.pos.y > config.HEIGHT + 50:
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, config.DOCTOR_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)
