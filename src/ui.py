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
    difficulty_multiplier: float = 1.0,
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

    # Show difficulty multiplier if enabled
    if config.DIFFICULTY_ENABLED:
        lines.append(f"Speed: {difficulty_multiplier:.2f}x")

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
) -> list[pygame.Rect]:
    # Dim background overlay
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # Panel
    panel_w, panel_h = 360, 240
    panel_x = (config.WIDTH - panel_w) // 2
    panel_y = (config.HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(surface, (20, 20, 20), panel_rect, border_radius=12)
    pygame.draw.rect(surface, config.UI_COLOR, panel_rect, 2, border_radius=12)

    # Title
    title_surf = title_font.render(title, True, config.UI_COLOR)
    title_rect = title_surf.get_rect(center=(config.WIDTH // 2, panel_y + 55))
    surface.blit(title_surf, title_rect)

    # Subtitle
    if subtitle:
        sub_surf = ui_font.render(subtitle, True, (180, 180, 180))
        sub_rect = sub_surf.get_rect(center=(config.WIDTH // 2, panel_y + 95))
        surface.blit(sub_surf, sub_rect)

    # Options
    option_rects: list[pygame.Rect] = []
    start_y = panel_y + 135

    for i, text in enumerate(options):
        is_sel = (i == selected_index)
        color = (255, 255, 255) if is_sel else (200, 200, 200)

        surf = ui_font.render(text, True, color)
        rect = surf.get_rect(center=(config.WIDTH // 2, start_y + i * 30))
        surface.blit(surf, rect)

        # Expand clickable area a bit
        click_rect = rect.inflate(120, 10)
        option_rects.append(click_rect)

        if is_sel:
            marker = ui_font.render(">>", True, color)
            mrect = marker.get_rect(midright=(rect.left - 14, rect.centery))
            surface.blit(marker, mrect)

    return option_rects


def draw_settings_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    settings: list[dict],
    selected_index: int,
) -> list[pygame.Rect]:
    """Draw the settings menu with adjustable values."""
    # Dim background overlay
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # Larger panel for settings
    panel_w, panel_h = 600, 500
    panel_x = (config.WIDTH - panel_w) // 2
    panel_y = (config.HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(surface, (20, 20, 20), panel_rect, border_radius=12)
    pygame.draw.rect(surface, config.UI_COLOR, panel_rect, 2, border_radius=12)

    # Title
    title_surf = title_font.render("SETTINGS", True, config.UI_COLOR)
    title_rect = title_surf.get_rect(center=(config.WIDTH // 2, panel_y + 40))
    surface.blit(title_surf, title_rect)

    # Subtitle
    subtitle = "← → to adjust, Enter to apply, Esc to cancel"
    sub_surf = ui_font.render(subtitle, True, (180, 180, 180))
    sub_rect = sub_surf.get_rect(center=(config.WIDTH // 2, panel_y + 75))
    surface.blit(sub_surf, sub_rect)

    # Settings list
    option_rects: list[pygame.Rect] = []
    start_y = panel_y + 110
    line_height = 32

    for i, setting in enumerate(settings):
        is_sel = (i == selected_index)
        y_pos = start_y + i * line_height

        # Setting name
        name_color = (255, 255, 255) if is_sel else (200, 200, 200)
        name_surf = ui_font.render(setting["name"], True, name_color)
        name_rect = name_surf.get_rect(midleft=(panel_x + 30, y_pos))
        surface.blit(name_surf, name_rect)

        # Setting value (right-aligned)
        if setting["type"] != "action":
            value = setting["value"]
            
            # Format value based on type
            if setting["type"] == "bool":
                value_str = "ON" if value else "OFF"
            elif setting["type"] == "float":
                value_str = f"{value:.2f}"
            elif setting["type"] == "int":
                value_str = str(value)
            elif setting["type"] == "enum":
                value_str = value
            else:
                value_str = str(value)
            
            value_color = (100, 200, 255) if is_sel else (150, 150, 150)
            value_surf = ui_font.render(value_str, True, value_color)
            value_rect = value_surf.get_rect(midright=(panel_x + panel_w - 30, y_pos))
            surface.blit(value_surf, value_rect)

        # Selection marker
        if is_sel:
            marker = ui_font.render(">>", True, name_color)
            mrect = marker.get_rect(midright=(name_rect.left - 10, y_pos))
            surface.blit(marker, mrect)

        # Create clickable rect
        click_rect = pygame.Rect(panel_x + 20, y_pos - 12, panel_w - 40, line_height - 4)
        option_rects.append(click_rect)

    return option_rects
