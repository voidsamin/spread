from __future__ import annotations

import pygame
import config
from agents import Agent


class Doctor:
    """
    Doctor follows the mouse and can cure infected agents with left click.
    """
    def __init__(self) -> None:
        self.pos = pygame.Vector2(config.WIDTH // 2, config.HEIGHT // 2)
        self.cooldown_timer = 0.0  # seconds until next cure allowed

    def update(self, dt: float) -> None:
        # Follow mouse cursor
        mx, my = pygame.mouse.get_pos()
        self.pos.update(mx, my)

        # Cooldown countdown
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

    def can_cure(self) -> bool:
        return self.cooldown_timer <= 0.0

    def try_cure(self, agents: list[Agent]) -> bool:
        """
        Cure the nearest infected agent within CURE_RADIUS.
        Returns True if someone was cured, else False.
        """
        if not self.can_cure():
            return False

        radius = config.CURE_RADIUS
        radius_sq = radius * radius

        nearest: Agent | None = None
        best_d2 = float("inf")

        for a in agents:
            if not a.infected:
                continue
            d2 = (a.pos - self.pos).length_squared()
            if d2 <= radius_sq and d2 < best_d2:
                best_d2 = d2
                nearest = a

        if nearest is None:
            return False

        # Cure
        nearest.infected = False

        # Start cooldown
        self.cooldown_timer = config.CURE_COOLDOWN
        return True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw a blue cross centered at the mouse position + optional cure radius ring.
        """
        x, y = int(self.pos.x), int(self.pos.y)
        color = config.DOCTOR_COLOR

        # Cross size
        arm = 10
        thickness = 3

        pygame.draw.line(surface, color, (x - arm, y), (x + arm, y), thickness)
        pygame.draw.line(surface, color, (x, y - arm), (x, y + arm), thickness)

        # Optional: show cure radius as a thin ring (nice feedback, still MVP-friendly)
        pygame.draw.circle(surface, color, (x, y), config.CURE_RADIUS, 1)
