from __future__ import annotations

import math
import pygame
import config


def draw_fps(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, config.HUD_COLOR)
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

    # Render with semi-transparent backing panel
    x, y = 10, 30
    line_h = 22
    pad = 6
    panel_w = 220
    panel_h = len(lines) * line_h + pad * 2
    backing = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    backing.fill((255, 255, 255, 140))
    surface.blit(backing, (x - pad, y - pad))

    for line in lines:
        surf = font.render(line, True, config.HUD_COLOR)
        surface.blit(surf, (x, y))
        y += line_h


def draw_infection_curve(
    surface: pygame.Surface,
    ratios: list[float],
    rect: tuple[int, int, int, int],
    strain_histories: dict[int, list[float]] | None = None,
) -> None:
    if not ratios and not strain_histories:
        return

    x, y, w, h = rect

    # Outline box with backing
    backing = pygame.Surface((w, h), pygame.SRCALPHA)
    backing.fill((255, 255, 255, 140))
    surface.blit(backing, (x, y))
    pygame.draw.rect(surface, config.HUD_COLOR, pygame.Rect(x, y, w, h), 1)

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

    # Draw total curve (thicker)
    pts = ratios_to_pts(ratios)
    if pts:
        pygame.draw.lines(surface, config.HUD_COLOR, False, pts, 2)


def draw_healthy_population_curve(
    surface: pygame.Surface,
    ratios: list[float],
    rect: tuple[int, int, int, int],
) -> None:
    """Draw the inverse of infection ratio (healthy population trend)."""
    if not ratios:
        return

    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    # Convert ratios to healthy (inverse)
    healthy_ratios = [1.0 - r for r in ratios]

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

    # Draw healthy population curve (green)
    pts = ratios_to_pts(healthy_ratios)
    if pts:
        pygame.draw.lines(surface, config.HEALTHY_COLOR, False, pts, 2)


def draw_infection_rate_graph(
    surface: pygame.Surface,
    ratios: list[float],
    rect: tuple[int, int, int, int],
) -> None:
    """Draw infection rate (derivative) over time."""
    if len(ratios) < 2:
        return

    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    # Calculate rate of change (derivatives)
    rates = []
    for i in range(1, len(ratios)):
        rate = (ratios[i] - ratios[i-1]) * 100  # as percentage points per sample
        rates.append(rate)

    # Convert to points
    def rates_to_pts(r_list: list[float]):
        n = len(r_list)
        if n < 1: return []
        pts = []
        # Center line at middle of graph (rate = 0)
        center_y = y + h // 2
        for i, r in enumerate(r_list):
            px = x + int((i / max(1, n - 1)) * (w - 2)) + 1
            # Cap rate at reasonable values
            r = max(-0.05, min(0.05, r))
            py = center_y - int((r / 0.05) * (h // 2 - 2))
            pts.append((px, py))
        return pts

    pts = rates_to_pts(rates)
    if pts:
        # Draw center line
        pygame.draw.line(surface, (100, 100, 100), (x + 1, y + h // 2), (x + w - 1, y + h // 2), 1)
        # Draw rate curve (orange)
        pygame.draw.lines(surface, (255, 165, 0), False, pts, 2)


def draw_per_strain_breakdown(
    surface: pygame.Surface,
    font: pygame.font.Font,
    strain_counts: dict[int, int],
    total_agents: int,
    pos: tuple[int, int],
) -> int:
    """Draw per-strain breakdown with percentages and probabilities. Returns y-offset for next element."""
    x, y = pos
    
    if not strain_counts:
        return y
    
    total_infected = sum(strain_counts.values())
    
    for sid, s_info in config.STRAINS.items():
        count = strain_counts.get(sid, 0)
        ratio_of_infected = (count / total_infected * 100) if total_infected > 0 else 0
        ratio_of_total = (count / total_agents * 100) if total_agents > 0 else 0
        prob = s_info["infection_probability"]
        
        # Format: "Alpha: 5 / 150 (3.3% of pop, 25% of infected) - 18% infection prob"
        text = f"{s_info['name']}: {count}/{total_agents} ({ratio_of_total:.1f}% pop, {ratio_of_infected:.1f}% infected) - {prob:.0%} prob"
        text_surf = font.render(text, True, s_info["color"])
        surface.blit(text_surf, (x, y))
        y += 24
    
    return y


def draw_strain_composition_bars(
    surface: pygame.Surface,
    strain_counts: dict[int, int],
    total_agents: int,
    rect: tuple[int, int, int, int],
) -> None:
    """Draw a bar chart showing the current composition of each strain."""
    if not strain_counts or total_agents == 0:
        return

    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    # Inner dimensions for drawing
    inner_x = x + 2
    inner_y = y + 2
    inner_w = w - 4
    inner_h = h - 4

    # Draw bars for each strain
    num_strains = len(strain_counts)
    bar_width = (inner_w - num_strains * 2) // num_strains if num_strains > 0 else 0

    for idx, (sid, count) in enumerate(strain_counts.items()):
        ratio = count / total_agents if total_agents > 0 else 0
        bar_x = inner_x + idx * (bar_width + 2)
        bar_h = int(inner_h * ratio)
        bar_y = inner_y + inner_h - bar_h

        # Draw the bar with strain color
        color = config.STRAINS[sid]["color"]
        pygame.draw.rect(surface, color, pygame.Rect(bar_x, bar_y, bar_width, bar_h))

        # Draw a thin border
        pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(bar_x, bar_y, bar_width, bar_h), 1)


def draw_cumulative_infections_graph(
    surface: pygame.Surface,
    ratios: list[float],
    rect: tuple[int, int, int, int],
) -> None:
    """Draw cumulative infection count over time."""
    if not ratios:
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

    # Draw cumulative (same as regular infection ratio for now, but styled differently)
    pts = ratios_to_pts(ratios)
    if pts:
        pygame.draw.lines(surface, (200, 100, 255), False, pts, 2)  # Purple


def draw_model_probability_distribution(
    surface: pygame.Surface,
    rect: tuple[int, int, int, int],
    model: str,
) -> None:
    """Draw a visual representation of the infection probability distribution based on the model."""
    x, y, w, h = rect

    # Outline box
    pygame.draw.rect(surface, config.UI_COLOR, pygame.Rect(x, y, w, h), 1)

    inner_x = x + 2
    inner_y = y + 2
    inner_w = w - 4
    inner_h = h - 4

    # Generate distribution samples based on model
    samples = 100
    dist_values = []

    if model.lower() == "uniform":
        # Uniform: constant probability
        dist_values = [1.0] * samples

    elif model.lower() == "gaussian":
        # Gaussian: peak in middle, tails on sides
        sigma = config.GAUSSIAN_SIGMA if hasattr(config, 'GAUSSIAN_SIGMA') else 0.3
        for i in range(samples):
            # Normalize i to [-3, 3] sigma range
            x_norm = (i / samples) * 6 - 3
            # Gaussian PDF
            val = math.exp(-(x_norm ** 2) / (2 * sigma ** 2))
            dist_values.append(val)

    elif model.lower() == "exponential":
        # Exponential: rapid rise
        scale = config.EXPONENTIAL_SCALE if hasattr(config, 'EXPONENTIAL_SCALE') else 1.0
        for i in range(samples):
            x_norm = i / samples
            val = min(1.0, (1 - math.exp(-5 * x_norm)))
            dist_values.append(val)

    # Normalize to max 1.0
    max_val = max(dist_values) if dist_values else 1.0
    if max_val > 0:
        dist_values = [v / max_val for v in dist_values]

    # Draw bars
    bar_width = inner_w / samples if samples > 0 else 0
    for i, val in enumerate(dist_values):
        bar_x = inner_x + i * bar_width
        bar_h = int(inner_h * val)
        bar_y = inner_y + inner_h - bar_h
        color = (100, 200, 100) if model.lower() == "uniform" else (150, 150, 255) if model.lower() == "gaussian" else (255, 150, 100)
        pygame.draw.rect(surface, color, pygame.Rect(bar_x, bar_y, bar_width, bar_h))


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
    strain_counts: dict[int, int] | None = None,
    total_agents: int = 150,
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

    # --- Split into sections (3-column layout) ---
    # Left: Stats + Strain Composition, Right: Graphs (Infection & Healthy), Bottom: Details
    margin = 40
    content_y = title_rect.bottom + 40
    col_w = (panel_w - margin * 3) // 2
    graph_h = 100

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
        stats_y += 30

    # A2. Strain Composition Bar Chart (Below Stats)
    composition_y = stats_y + 15
    comp_label = ui_font.render("Strain Composition:", True, config.UI_COLOR)
    surface.blit(comp_label, (panel_x + margin, composition_y))
    composition_graph_rect = (panel_x + margin, composition_y + 25, col_w, 50)
    total_infected = sum(strain_counts.values()) if strain_counts else 0
    total_agents_val = stats["healthy"] + stats["infected"]
    draw_strain_composition_bars(surface, strain_counts or {}, total_agents_val, composition_graph_rect)

    # A3. Strain Breakdown Details (Below bar chart)
    breakdown_y = composition_graph_rect[1] + composition_graph_rect[3] + 15
    breakdown_y = draw_per_strain_breakdown(
        surface,
        pygame.font.Font(config.FONT_NAME, 16),
        strain_counts or {},
        total_agents_val,
        (panel_x + margin, breakdown_y)
    )

    # B. Graphs Column (Right) - Multiple graphs stacked
    right_x = panel_x + panel_w - margin - col_w
    graph_h = 70

    # B1. Infection Trend Graph (Top)
    infection_graph_rect = (right_x, content_y, col_w, graph_h)
    draw_infection_curve(surface, ratios, infection_graph_rect, strain_histories)
    g_label = ui_font.render("Infection Trend", True, (180, 180, 180))
    surface.blit(g_label, (infection_graph_rect[0], infection_graph_rect[1] - 20))

    # B2. Healthy Population Graph
    healthy_start_y = infection_graph_rect[1] + infection_graph_rect[3] + 25
    healthy_graph_rect = (right_x, healthy_start_y, col_w, graph_h)
    draw_healthy_population_curve(surface, ratios, healthy_graph_rect)
    h_label = ui_font.render("Healthy Population", True, (180, 180, 180))
    surface.blit(h_label, (healthy_graph_rect[0], healthy_graph_rect[1] - 20))

    # B3. Infection Rate Graph
    rate_start_y = healthy_graph_rect[1] + healthy_graph_rect[3] + 25
    rate_graph_rect = (right_x, rate_start_y, col_w, graph_h)
    draw_infection_rate_graph(surface, ratios, rate_graph_rect)
    rate_label = ui_font.render("Infection Rate", True, (180, 180, 180))
    surface.blit(rate_label, (rate_graph_rect[0], rate_graph_rect[1] - 20))

    # B4. Strain Legend (Below graphs)
    legend_y = rate_graph_rect[1] + rate_graph_rect[3] + 10
    legend_x = right_x
    small_legend_font = pygame.font.Font(config.FONT_NAME, 16)
    for sid, s_info in config.STRAINS.items():
        # Color indicator circle
        pygame.draw.circle(surface, s_info["color"], (legend_x + 8, legend_y + 6), 4)
        # Strain name
        l_text = small_legend_font.render(s_info["name"], True, (200, 200, 200))
        surface.blit(l_text, (legend_x + 18, legend_y))
        legend_x += 75 # Horizontal spacing for legend items

    # B5. Distribution Model Note
    model_y = legend_y + 25
    model_note = f"Model: {config.INFECTION_MODEL.capitalize()}"
    model_surf = pygame.font.Font(config.FONT_NAME, 16).render(model_note, True, (150, 200, 255))
    surface.blit(model_surf, (right_x, model_y))
    
    # C. Simulation Insight (Bottom Center)
    insight_y = model_y + 40
    insight_title = ui_font.render("Simulation Insight: " + config.INFECTION_MODEL.capitalize(), True, config.UI_COLOR)
    surface.blit(insight_title, (panel_x + margin, insight_y))
    
    # Text explanation based on model
    explanations = {
        "uniform": "Infection spreads at a constant probability upon contact. Every encounter carries the same risk.",
        "gaussian": "Risk follows a Normal distribution. Most encounters are low-risk, but rare 'super-spreader' events drive spikes.",
        "exponential": "Spread risk grows rapidly with proximity. Distancing is significantly more effective here."
    }
    explanation = explanations.get(config.INFECTION_MODEL.lower(), "Standard infection dynamics.")
    
    # Use smaller font for explanation text (reduced from ui_font which is 24pt)
    small_font = pygame.font.Font(config.FONT_NAME, 16)
    
    # Wrap text manually (simple way)
    words = explanation.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if small_font.size(test_line)[0] < (panel_w - margin * 2):
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        line_surf = small_font.render(line, True, (200, 200, 200))
        surface.blit(line_surf, (panel_x + margin, insight_y + 35 + i * 22))

    # C2. Probability Distribution Visualization
    prob_dist_y = insight_y + 35 + len(lines) * 22 + 10
    prob_label = ui_font.render("Infection Probability Distribution:", True, config.UI_COLOR)
    surface.blit(prob_label, (panel_x + margin, prob_dist_y))
    
    prob_graph_rect = (panel_x + margin, prob_dist_y + 25, col_w, 50)
    draw_model_probability_distribution(surface, prob_graph_rect, config.INFECTION_MODEL)

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

    # --- Options ---
    rendered_options = []
    for opt_text in options:
        surf_normal = ui_font.render(opt_text, True, (200, 200, 200))
        surf_sel = ui_font.render(opt_text, True, (255, 255, 255))
        rendered_options.append((surf_normal, surf_sel))

    # --- Dynamic Panel Sizing ---
    margin_v = 30
    margin_h = 40
    bar_height = 44
    bar_gap = 8
    bar_w = 320

    content_w = max(title_surf.get_width(), bar_w) + margin_h * 2
    panel_w = content_w
    content_h = title_surf.get_height() + 30 + len(options) * (bar_height + bar_gap)
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
    curr_y = title_rect.bottom + 25

    # Options as bar buttons
    option_rects: list[pygame.Rect] = []
    for i, (sn, ss) in enumerate(rendered_options):
        is_sel = (i == selected_index)

        # Bar rectangle
        bar_rect = pygame.Rect(
            config.WIDTH // 2 - bar_w // 2,
            curr_y,
            bar_w,
            bar_height,
        )

        # Draw bar background
        bar_surf = pygame.Surface((bar_w, bar_height), pygame.SRCALPHA)
        if is_sel:
            bar_surf.fill((80, 160, 230, 120))   # Bright blue glow
        else:
            bar_surf.fill((255, 255, 255, 30))    # Subtle translucent
        pygame.draw.rect(bar_surf, (255, 255, 255, 60 if is_sel else 25),
                         bar_surf.get_rect(), 1, border_radius=8)
        surface.blit(bar_surf, bar_rect)

        # Text centred inside bar
        surf = ss if is_sel else sn
        text_rect = surf.get_rect(center=bar_rect.center)
        surface.blit(surf, text_rect)

        option_rects.append(bar_rect)
        curr_y += bar_height + bar_gap

    return option_rects


def draw_settings_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    settings: list[dict],
    selected_index: int,
    background: pygame.Surface | None = None,
) -> list[pygame.Rect]:
    """Draw the settings menu with adjustable values in bar-style rows."""
    # Draw background image or dim overlay
    if background is not None:
        surface.blit(background, (0, 0))
    else:
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

    # Dynamic panel sizing based on number of settings
    bar_height = 36
    bar_gap = 4
    header_height = 80
    min_panel_h = 400
    content_h = len(settings) * (bar_height + bar_gap) + header_height + 40
    panel_h = max(min_panel_h, min(content_h, int(config.HEIGHT * 0.85)))

    panel_w = 600
    panel_x = (config.WIDTH - panel_w) // 2
    panel_y = (config.HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(surface, (20, 20, 20), panel_rect, border_radius=12)
    pygame.draw.rect(surface, config.UI_COLOR, panel_rect, 2, border_radius=12)

    # Title
    title_surf = title_font.render("SETTINGS", True, config.UI_COLOR)
    title_rect = title_surf.get_rect(center=(config.WIDTH // 2, panel_y + 40))
    surface.blit(title_surf, title_rect)

    # Settings list with scrolling support if needed
    option_rects: list[pygame.Rect] = []
    start_y = panel_y + header_height
    max_visible = (panel_h - header_height - 20) // (bar_height + bar_gap)

    # Scroll to keep selected item visible
    scroll_offset = 0
    if selected_index >= max_visible:
        scroll_offset = selected_index - max_visible + 1

    bar_inner_w = panel_w - 40  # 20px padding each side

    for i, setting in enumerate(settings):
        # Skip items outside the visible range
        if i < scroll_offset or i >= scroll_offset + max_visible:
            continue

        is_sel = (i == selected_index)
        y_pos = start_y + (i - scroll_offset) * (bar_height + bar_gap)

        # Bar rectangle
        bar_rect = pygame.Rect(panel_x + 20, y_pos, bar_inner_w, bar_height)

        # Draw bar background
        bar_surf = pygame.Surface((bar_inner_w, bar_height), pygame.SRCALPHA)
        if is_sel:
            bar_surf.fill((80, 160, 230, 100))
        else:
            bar_surf.fill((255, 255, 255, 20))
        pygame.draw.rect(bar_surf, (255, 255, 255, 50 if is_sel else 15),
                         bar_surf.get_rect(), 1, border_radius=6)
        surface.blit(bar_surf, bar_rect)

        # Setting name (left-aligned inside bar)
        name_color = (255, 255, 255) if is_sel else (200, 200, 200)
        name_surf = ui_font.render(setting["name"], True, name_color)
        name_rect = name_surf.get_rect(midleft=(bar_rect.left + 12, bar_rect.centery))
        surface.blit(name_surf, name_rect)

        # --- Slider type ---
        if setting["type"] == "slider":
            value = setting["value"]
            min_v = setting["min"]
            max_v = setting["max"]
            ratio = (value - min_v) / max(0.001, max_v - min_v)

            # Slider track area (right half of the bar)
            slider_w = 160
            slider_h = 8
            slider_x = bar_rect.right - slider_w - 60
            slider_y = bar_rect.centery - slider_h // 2

            # Track background
            track_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
            pygame.draw.rect(surface, (60, 60, 60), track_rect, border_radius=4)

            # Filled portion
            fill_w = int(slider_w * ratio)
            if fill_w > 0:
                fill_rect = pygame.Rect(slider_x, slider_y, fill_w, slider_h)
                fill_color = (80, 180, 255) if is_sel else (100, 140, 180)
                pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)

            # Knob
            knob_x = slider_x + fill_w
            knob_r = 7
            knob_color = (255, 255, 255) if is_sel else (180, 180, 180)
            pygame.draw.circle(surface, knob_color, (knob_x, bar_rect.centery), knob_r)

            # Percentage text
            pct_str = f"{int(ratio * 100)}%"
            pct_color = (100, 200, 255) if is_sel else (150, 150, 150)
            pct_surf = ui_font.render(pct_str, True, pct_color)
            pct_rect = pct_surf.get_rect(midright=(bar_rect.right - 12, bar_rect.centery))
            surface.blit(pct_surf, pct_rect)

        # --- Other value types ---
        elif setting["type"] != "action":
            value = setting["value"]

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
            value_rect = value_surf.get_rect(midright=(bar_rect.right - 12, bar_rect.centery))
            surface.blit(value_surf, value_rect)

            # Draw left/right arrows when selected
            if is_sel:
                arrow_l = ui_font.render("◄", True, (100, 200, 255))
                arrow_r = ui_font.render("►", True, (100, 200, 255))
                surface.blit(arrow_l, arrow_l.get_rect(midright=(value_rect.left - 8, bar_rect.centery)))
                surface.blit(arrow_r, arrow_r.get_rect(midleft=(value_rect.right + 8, bar_rect.centery)))

        # Create clickable rect
        option_rects.append(bar_rect)

    return option_rects
