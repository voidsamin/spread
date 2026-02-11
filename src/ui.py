from __future__ import annotations

import pygame
import config


def draw_fps(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, config.UI_COLOR)
    surface.blit(fps_text, (10, 8))


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    infected: int,
    healthy: int,
    ratio: float,
    t_above: float,
    elapsed: float,
    ammo: int,
    ammo_max: int,
    reload_timer: float,
    reload_time: float,
    shot_cd: float,
) -> None:
    # Build lines
    lines = [
        f"Time: {format_time(elapsed)}",
        f"Infected: {infected}",
        f"Healthy:  {healthy}",
        f"Infected %: {ratio*100:.1f}%",
        f">50% timer: {t_above:.1f}s",
        f"Pellets: {ammo}/{ammo_max}",
    ]

    # Reload / cooldown hints
    if ammo <= 0:
        remaining = max(0.0, reload_time - reload_timer)
        lines.append(f"Reloading: {remaining:.1f}s")
    else:
        lines.append(f"Shot CD: {max(0.0, shot_cd):.2f}s")

    # Render
    x, y = 10, 30
    for line in lines:
        surf = font.render(line, True, config.UI_COLOR)
        surface.blit(surf, (x, y))
        y += 22


def draw_infection_curve(
    surface: pygame.Surface,
    ratios: list[float],
    rect: tuple[int, int, int, int],
) -> None:
    if not ratios:
        return

    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    # Convert ratios (0..1) to points
    n = len(ratios)
    if n < 2:
        return

    pts = []
    for i, r in enumerate(ratios):
        r = max(0.0, min(1.0, r))
        px = x + int((i / (n - 1)) * (w - 2)) + 1
        py = y + int((1.0 - r) * (h - 2)) + 1
        pts.append((px, py))

    # Draw curve
    pygame.draw.lines(surface, config.INFECTED_COLOR, False, pts, 2)


def draw_center_message(surface: pygame.Surface, font: pygame.font.Font, text: str, color) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
    surface.blit(surf, rect)

def draw_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    title: str,
    options: list[str],
    selected_index: int,
    subtitle: str | None = None,
) -> None:
    # Title
    title_surf = title_font.render(title, True, config.UI_COLOR)
    title_rect = title_surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 120))
    surface.blit(title_surf, title_rect)

    # Optional subtitle
    if subtitle:
        sub_surf = ui_font.render(subtitle, True, config.UI_COLOR)
        sub_rect = sub_surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 80))
        surface.blit(sub_surf, sub_rect)

    # Options
    start_y = config.HEIGHT // 2 - 10
    for i, text in enumerate(options):
        prefix = "> " if i == selected_index else "  "
        line = prefix + text
        surf = ui_font.render(line, True, config.UI_COLOR)
        rect = surf.get_rect(center=(config.WIDTH // 2, start_y + i * 30))
        surface.blit(surf, rect)
