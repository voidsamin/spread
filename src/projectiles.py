from __future__ import annotations

from dataclasses import dataclass, field
import pygame
import config


@dataclass
class Projectile:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int
    life: float  # seconds remaining
    sprite: pygame.Surface | None = field(default=None, repr=False)

    def update(self, dt: float, hospital_map=None) -> None:
        self.pos += self.vel * dt
        self.life -= dt

        # Despawn on map-wall collision
        if hospital_map is not None:
            if hospital_map.is_wall(int(self.pos.x), int(self.pos.y)):
                self.life = -1  # mark dead

    def is_dead(self) -> bool:
        # Dead if lifetime expired or goes off world bounds
        if self.life <= 0:
            return True
        world_w = getattr(config, "WORLD_WIDTH", config.WIDTH)
        world_h = getattr(config, "WORLD_HEIGHT", config.HEIGHT)
        if self.pos.x < -50 or self.pos.x > world_w + 50:
            return True
        if self.pos.y < -50 or self.pos.y > world_h + 50:
            return True
        return False

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        if camera is not None:
            sx, sy = camera.apply(self.pos)
        else:
            sx, sy = int(self.pos.x), int(self.pos.y)

        if self.sprite is not None:
            rect = self.sprite.get_rect(center=(sx, sy))
            surface.blit(self.sprite, rect)
        else:
            pygame.draw.circle(surface, config.DOCTOR_COLOR, (sx, sy), self.radius)
