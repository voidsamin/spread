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
    time_scale: float = 1.0,
    strain_counts: dict[int, int] | None = None,
) -> None:
    # Build lines
    lines = [
        f"Time: {format_time(elapsed)}",
        f"Infected: {infected}",
    ]
    
    if strain_counts:
        for sid, count in strain_counts.items():
            name = config.STRAINS[sid]["name"]
            lines.append(f"  - {name}: {count}")

    lines.extend([
        f"Healthy:  {healthy}",
        f"Infected %: {ratio*100:.1f}%",
        f">50% timer: {t_above:.1f}s",
        f"Pellets: {ammo}/{ammo_max}",
        f"Sim Speed: {time_scale:.0f}x",
    ])

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
    strain_histories: dict[int, list[float]] | None = None,
) -> None:
    if not ratios and not strain_histories:
        return

    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    # Helper to convert ratio list to points
    def ratios_to_pts(r_list: list[float]):
        n = len(r_list)
        if n < 2: return []
        pts = []
        for i, r in enumerate(r_list):
            r = max(0.0, min(1.0, r))
            px = x + int((i / (n - 1)) * (w - 2)) + 1
            py = y + int((1.0 - r) * (h - 2)) + 1
            pts.append((px, py))
        return pts

    # Draw per-strain curves first (thinner)
    if strain_histories:
        for sid, h_list in strain_histories.items():
            pts = ratios_to_pts(h_list)
            if pts:
                color = config.STRAINS[sid]["color"]
                pygame.draw.lines(surface, color, False, pts, 1)

    # Draw total curve (thicker, white/default)
    pts = ratios_to_pts(ratios)
    if pts:
        pygame.draw.lines(surface, config.UI_COLOR, False, pts, 2)


def draw_center_message(surface: pygame.Surface, font: pygame.font.Font, text: str, color) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
    surface.blit(surf, rect)


def draw_pause_overlay(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    stats: dict,
    ratios: list[float],
    strain_histories: dict[int, list[float]],
    options: list[str],
    selected_index: int,
) -> list[pygame.Rect]:
    """Draw a modern, clean pause overlay with stats, graphs, and insights."""
    # 1. Dim/Blur effect (provided by the background surface passed in Game.draw)
    # We still want to add a semi-transparent dark overlay for readability
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    # 2. Main Panel
    panel_w, panel_h = config.WIDTH * 0.8, config.HEIGHT * 0.8
    panel_x = (config.WIDTH - panel_w) // 2
    panel_y = (config.HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(surface, (15, 15, 15, 230), panel_rect, border_radius=20)
    pygame.draw.rect(surface, config.UI_COLOR, panel_rect, 2, border_radius=20)

    # 3. Title
    title_surf = title_font.render("SYSTEM PAUSED", True, config.UI_COLOR)
    title_rect = title_surf.get_rect(center=(config.WIDTH // 2, panel_y + 50))
    surface.blit(title_surf, title_rect)

    # --- Split into sections ---
    # Left: Stats, Right: Graph, Bottom: Insight
    margin = 40
    content_y = title_rect.bottom + 40
    col_w = (panel_w - margin * 3) // 2

    # A. Statistics Column (Left)
    stats_y = content_y
    stats_list = [
        ("Time Elapsed", stats["elapsed"]),
        ("Healthy Remaining", f"{stats['healthy']}"),
        ("Infected Agents", f"{stats['infected']}"),
        ("Infection Ratio", f"{stats['ratio']*100:.1f}%"),
        ("Current Speed", f"{stats['multiplier']:.2f}x"),
    ]

    for label, val in stats_list:
        l_surf = ui_font.render(label, True, (180, 180, 180))
        surface.blit(l_surf, (panel_x + margin, stats_y))
        v_surf = ui_font.render(val, True, config.WHITE)
        surface.blit(v_surf, (panel_x + margin + col_w - v_surf.get_width(), stats_y))
        stats_y += 35

    # B. Graph Column (Right)
    graph_rect = (panel_x + panel_w - margin - col_w, content_y, col_w, 200)
    draw_infection_curve(surface, ratios, graph_rect, strain_histories)
    # Graph label
    g_label = ui_font.render("Infection Trend", True, (180, 180, 180))
    surface.blit(g_label, (graph_rect[0], graph_rect[1] - 25))

    # B2. Strain Legend (Below Graph)
    legend_y = graph_rect[1] + graph_rect[3] + 15
    legend_x = graph_rect[0]
    for sid, s_info in config.STRAINS.items():
        # Color indicator circle
        pygame.draw.circle(surface, s_info["color"], (legend_x + 8, legend_y + 10), 6)
        # Strain name
        l_text = ui_font.render(s_info["name"], True, (200, 200, 200))
        surface.blit(l_text, (legend_x + 24, legend_y))
        legend_x += 100 # Horizontal spacing for legend items

    # C. Simulation Insight (Bottom Center)
    insight_y = content_y + 240
    insight_title = ui_font.render("Simulation Insight: " + config.INFECTION_MODEL.capitalize(), True, config.UI_COLOR)
    surface.blit(insight_title, (panel_x + margin, insight_y))
    
    # Text explanation based on model
    explanations = {
        "uniform": "Infection spreads at a constant probability upon contact. Every encounter carries the same risk.",
        "gaussian": "Risk follows a Normal distribution. Most encounters are low-risk, but rare 'super-spreader' events drive spikes.",
        "exponential": "Spread risk grows rapidly with proximity. Distancing is significantly more effective here."
    }
    explanation = explanations.get(config.INFECTION_MODEL.lower(), "Standard infection dynamics.")
    
    # Wrap text manually (simple way)
    words = explanation.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if ui_font.size(test_line)[0] < (panel_w - margin * 2):
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        line_surf = ui_font.render(line, True, (200, 200, 200))
        surface.blit(line_surf, (panel_x + margin, insight_y + 35 + i * 28))

    # D. Navigation Options (Bottom)
    option_rects: list[pygame.Rect] = []
    opt_y = panel_y + panel_h - 60
    opt_spacing = panel_w // (len(options) + 1)
    
    for i, opt in enumerate(options):
        is_sel = (i == selected_index)
        color = config.WHITE if is_sel else (150, 150, 150)
        surf = ui_font.render(opt, True, color)
        rect = surf.get_rect(center=(panel_x + opt_spacing * (i + 1), opt_y))
        surface.blit(surf, rect)
        
        click_rect = rect.inflate(40, 20)
        option_rects.append(click_rect)
        
        if is_sel:
            pygame.draw.line(surface, color, (rect.left, rect.bottom + 2), (rect.right, rect.bottom + 2), 2)

    return option_rects

def draw_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    title: str,
    options: list[str],
    selected_index: int,
    subtitle: str | None = None,
    background: pygame.Surface | None = None,
) -> list[pygame.Rect]:
    # Draw background image or dim overlay
    if background is not None:
        surface.blit(background, (0, 0))
    else:
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

    # --- Title (Text or Surface) ---
    if isinstance(title, pygame.Surface):
        title_surf = title
    else:
        title_surf = title_font.render(title, True, config.UI_COLOR)

    # --- Subtitle ---
    sub_surf = None
    if subtitle:
        sub_surf = ui_font.render(subtitle, True, (180, 180, 180))

    # --- Options ---
    rendered_options = []
    for opt_text in options:
        surf_normal = ui_font.render(opt_text, True, (200, 200, 200))
        surf_sel = ui_font.render(opt_text, True, (255, 255, 255))
        rendered_options.append((surf_normal, surf_sel))

    # --- Dynamic Panel Sizing ---
    margin_v = 30
    margin_h = 40
    option_gap = 10
    
    # Width: Max of logo, subtitle, and options + horizontal margins
    content_w = title_surf.get_width()
    if sub_surf:
        content_w = max(content_w, sub_surf.get_width())
    for (sn, ss) in rendered_options:
        content_w = max(content_w, sn.get_width() + 40) # 40 for selection markers
    
    panel_w = content_w + margin_h * 2
    
    # Height: Sum of components + vertical margins
    content_h = title_surf.get_height() + 20 # Title height + gap
    if sub_surf:
        content_h += sub_surf.get_height() + 20
    
    content_h += len(options) * 30 # Options (assume 30px per line)
    
    panel_h = content_h + margin_v * 2
    
    panel_x = (config.WIDTH - panel_w) // 2
    panel_y = (config.HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(surface, (20, 20, 20), panel_rect, border_radius=12)
    pygame.draw.rect(surface, config.UI_COLOR, panel_rect, 2, border_radius=12)

    # --- Rendering ---
    curr_y = panel_y + margin_v
    
    # Logo / Title
    title_rect = title_surf.get_rect(centerx=config.WIDTH // 2, top=curr_y)
    surface.blit(title_surf, title_rect)
    curr_y = title_rect.bottom + 15

    # Subtitle
    if sub_surf:
        sub_rect = sub_surf.get_rect(centerx=config.WIDTH // 2, top=curr_y)
        surface.blit(sub_surf, sub_rect)
        curr_y = sub_rect.bottom + 20
    else:
        curr_y += 10

    # Options
    option_rects: list[pygame.Rect] = []
    for i, (sn, ss) in enumerate(rendered_options):
        is_sel = (i == selected_index)
        surf = ss if is_sel else sn
        rect = surf.get_rect(centerx=config.WIDTH // 2, top=curr_y)
        surface.blit(surf, rect)

        if is_sel:
            marker = ui_font.render(">>", True, (255, 255, 255))
            mrect = marker.get_rect(midright=(rect.left - 10, rect.centery))
            surface.blit(marker, mrect)

        # Expand clickable area
        click_rect = rect.inflate(panel_w // 2, 8)
        option_rects.append(click_rect)
        curr_y += 30

    return option_rects


def draw_settings_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    settings: list[dict],
    selected_index: int,
    background: pygame.Surface | None = None,
) -> list[pygame.Rect]:
    """Draw the settings menu with adjustable values."""
    # Draw background image or dim overlay
    if background is not None:
        surface.blit(background, (0, 0))
    else:
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
