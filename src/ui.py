# src/ui.py
from __future__ import annotations

import pygame
import config


def draw_fps(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, config.UI_COLOR)
    surface.blit(fps_text, (10, 8))


def draw_stats(
    surface: pygame.Surface,
    font: pygame.font.Font,
    infected: int,
    healthy: int,
    ratio: float,
    t_above: float,
) -> None:
    lines = [
        f"Infected: {infected}",
        f"Healthy:  {healthy}",
        f"Infected %: {ratio*100:.1f}%",
        f">50% timer: {t_above:.1f}s",
    ]
    y = 30
    for line in lines:
        surf = font.render(line, True, config.UI_COLOR)
        surface.blit(surf, (10, y))
        y += 22


def draw_center_message(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color,
) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
    surface.blit(surf, rect)
