from __future__ import annotations
from collections import deque


import sys
import pygame

import config
from agents import spawn_agents, resolve_agent_collisions
from camera import Camera
from doctor import Doctor
from map import HospitalMap
from projectiles import Projectile
from ui import draw_fps, draw_hud, draw_infection_curve, draw_menu, draw_settings_menu, draw_pause_overlay


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        
        # Use native resolution and fullscreen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        # Update config dimensions with actual screen size
        config.WIDTH, config.HEIGHT = self.screen.get_size()
        
        # Reposition graph relative to top-right
        graph_w, graph_h = 250, 90
        config.GRAPH_RECT = (config.WIDTH - graph_w - 10, 10, graph_w, graph_h)

        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_TITLE)
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)

        # Load menu background image
        import os
        bg_path = os.path.join(os.path.dirname(__file__), "components", "menu_background.png")
        orig_bg = pygame.image.load(bg_path).convert()
        
        # Calculate aspect scaling to cover the screen (crop instead of stretch)
        bg_w, bg_h = orig_bg.get_size()
        screen_w, screen_h = config.WIDTH, config.HEIGHT
        
        # Choose the larger scale factor to ensure the screen is fully covered
        scale = max( screen_w / bg_w, screen_h / bg_h)
        new_w = int(bg_w * scale)
        new_h = int(bg_h * scale) 
        
        # Scale the image
        scaled_bg = pygame.transform.smoothscale(orig_bg, (new_w, new_h))
        
        # Center-crop to screen dimensions
        crop_x = (new_w - screen_w) // 2
        crop_y = (new_h - screen_h) // 2
        self.menu_background = scaled_bg.subsurface(pygame.Rect(crop_x, crop_y, screen_w, screen_h))

        # Load logo image
        logo_path = os.path.join(os.path.dirname(__file__), "components", "logo.png")
        self.logo = pygame.image.load(logo_path).convert_alpha()
        # Scale logo to a reasonable size
        logo_aspect = self.logo.get_width() / self.logo.get_height()
        target_w = config.LOGO_TARGET_WIDTH
        target_h = int(target_w / logo_aspect)
        self.logo = pygame.transform.smoothscale(self.logo, (target_w, target_h))

        # Hospital floor background (load BEFORE agents so we can use collision mask)
        self.map = HospitalMap()

        # Camera (smooth-follow viewport)
        self.camera = Camera(self.map.world_w, self.map.world_h)

        # Spawn agents in walkable areas of the map
        self.agents = spawn_agents(hospital_map=self.map)

        # Doctor (player)
        self.doctor = Doctor()

        # --- Agent walking animation sprites ---
        agents_dir = os.path.join(os.path.dirname(__file__), "components", "Agents")
        sheet_files = {
            "healthy":   "human_walking_transparent_bg.png",
            "infected1": "infected1_walking_transparent_bg.png",
            "infected2": "infected2_walking_transparent_bg.png",
            "infected3": "infected3_walking_transparent_bg.png",
        }
        self.agent_anims: dict[str, list[pygame.Surface]] = {}
        scale = config.AGENT_SPRITE_SCALE
        for anim_key, filename in sheet_files.items():
            sheet = pygame.image.load(os.path.join(agents_dir, filename)).convert_alpha()
            rects = config.AGENT_FRAMES[anim_key]
            frames: list[pygame.Surface] = []
            for rx, ry, rw, rh in rects:
                frame = sheet.subsurface(pygame.Rect(rx, ry, rw, rh))
                scaled = pygame.transform.smoothscale(
                    frame, (int(rw * scale), int(rh * scale))
                )
                frames.append(scaled)
            self.agent_anims[anim_key] = frames

        # Legacy static sprites (kept as fallbacks)
        virus_path = os.path.join(os.path.dirname(__file__), "components", "virus.png")
        orig_virus = pygame.image.load(virus_path).convert_alpha()
        virus_size = int(config.AGENT_RADIUS * 2.2)
        self.virus_sprite = pygame.transform.smoothscale(orig_virus, (virus_size, virus_size))

        self.strain_sprites = {}
        for sid, s_info in config.STRAINS.items():
            tinted = self.virus_sprite.copy()
            color_surf = pygame.Surface((virus_size, virus_size), pygame.SRCALPHA)
            color_surf.fill(s_info["color"])
            tinted.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.strain_sprites[sid] = tinted

        healthy_path = os.path.join(os.path.dirname(__file__), "components", "healthy.png")
        self.healthy_sprite = pygame.image.load(healthy_path).convert_alpha()
        healthy_size = int(config.AGENT_RADIUS * 2.2)
        self.healthy_sprite = pygame.transform.smoothscale(self.healthy_sprite, (healthy_size, healthy_size))
        

        # Projectiles (vaccine pellets)
        self.projectiles: list[Projectile] = []


        # Infection stats (updated every frame)
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0
        self.strain_counts = {sid: 0 for sid in config.STRAINS}

        # Lose-condition timer tracking
        self.time_above_threshold = 0.0

        # Initial game state (start at main menu) 
        self.state = config.MENU
        self.menu_index = 0

        # Menu options (could be expanded with more states like Settings, etc.)
        self.main_menu_options = ["Start", "Settings", "Quit"]
        self.pause_menu_options = ["Resume", "Restart", "Quit to Menu"]
        self.end_menu_options = ["Restart", "Quit to Menu", "Quit"]

        # Pre-calculate menu option rects for mouse interaction (future-proofing for mouse support)
        self.menu_option_rects = []

        # Win-condition timer
        self.time_below_win_threshold = 0.0

        # HUD toggle
        self.show_hud = config.SHOW_HUD

        # Elapsed time
        self.elapsed_time = 0.0

        # Screen capture for pause blur
        self.pause_screenshot = None

        # Post-game animation timer
        self.post_game_timer = 0.0

        # Infection ratio history (for curve overlay)
        self.history_timer = 0.0
        maxlen = int(config.HISTORY_SECONDS / config.HISTORY_SAMPLE_DT) + 1
        # Track history for each strain and total
        self.ratio_history = deque(maxlen=maxlen)
        self.strain_histories = {sid: deque(maxlen=maxlen) for sid in config.STRAINS}

        # Difficulty scaling
        self.difficulty_multiplier = config.DIFFICULTY_START_MULTIPLIER
        
        # Time scale (fast forward)
        self.time_scale = config.TIME_SCALE_1

        # Settings menu
        self.settings_menu_index = 0
        self.settings = [
            {
                "name": "Difficulty Enabled",
                "key": "difficulty_enabled",
                "type": "bool",
                "value": config.DIFFICULTY_ENABLED,
            },
            {
                "name": "Max Speed Multiplier",
                "key": "max_multiplier",
                "type": "float",
                "value": config.DIFFICULTY_MAX_MULTIPLIER,
                "min": 1.5,
                "max": 4.0,
                "step": 0.5,
            },
            {
                "name": "Ramp Time (seconds)",
                "key": "ramp_time",
                "type": "float",
                "value": config.DIFFICULTY_RAMP_TIME,
                "min": 60.0,
                "max": 300.0,
                "step": 30.0,
            },
            {
                "name": "Curve Type",
                "key": "curve_type",
                "type": "enum",
                "value": config.DIFFICULTY_CURVE_TYPE,
                "options": ["linear", "exponential", "sigmoid"],
            },
            {
                "name": "Curve Steepness",
                "key": "curve_steepness",
                "type": "float",
                "value": config.DIFFICULTY_CURVE_STEEPNESS,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
            },
            {
                "name": "Agent Count",
                "key": "agent_count",
                "type": "int",
                "value": config.AGENT_COUNT,
                "min": 50,
                "max": 300,
                "step": 25,
            },
            {
                "name": "Infection Probability",
                "key": "infection_prob",
                "type": "float",
                "value": config.INFECTION_PROBABILITY,
                "min": 0.05,
                "max": 0.50,
                "step": 0.05,
            },
            {
                "name": "Initial Infected",
                "key": "initial_infected",
                "type": "int",
                "value": config.INITIAL_INFECTED,
                "min": 1,
                "max": 10,
                "step": 1,
            },
            {
                "name": "Infection Model",
                "key": "infection_model",
                "type": "enum",
                "value": config.INFECTION_MODEL,
                "options": ["uniform", "gaussian", "exponential"],
            },
            {
                "name": "Lose Threshold (% infected)",
                "key": "lose_threshold_ratio",
                "type": "float",
                "value": config.LOSE_THRESHOLD_RATIO,
                "min": 0.10,
                "max": 0.90,
                "step": 0.05,
            },
            {
                "name": "Lose Duration (seconds)",
                "key": "lose_threshold_seconds",
                "type": "float",
                "value": config.LOSE_THRESHOLD_SECONDS,
                "min": 30.0,
                "max": 600.0,
                "step": 30.0,
            },
            {
                "name": "Win Threshold (% infected)",
                "key": "win_threshold_ratio",
                "type": "float",
                "value": config.WIN_THRESHOLD_RATIO,
                "min": 0.01,
                "max": 0.50,
                "step": 0.05,
            },
            {
                "name": "Win Duration (seconds)",
                "key": "win_threshold_seconds",
                "type": "float",
                "value": config.WIN_THRESHOLD_SECONDS,
                "min": 10.0,
                "max": 120.0,
                "step": 10.0,
            },
            {
                "name": "Apply & Back",
                "key": "_apply",
                "type": "action",
            },
        ]

        self.running = True

    def reset_run(self) -> None:
        """Reset a play session (used for Restart)."""
        self.agents = spawn_agents(hospital_map=self.map)
        self.projectiles.clear()

        # Reset stats/timers
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0
        self.strain_counts = {sid: 0 for sid in config.STRAINS}
        self.time_above_threshold = 0.0
        self.time_below_win_threshold = 0.0

        # Reset telemetry
        self.elapsed_time = 0.0
        self.history_timer = 0.0
        self.ratio_history.clear()
        for h in self.strain_histories.values():
            h.clear()
        
        # Reset doctor (animation + gameplay state)
        self.doctor.reset()

        # Snap camera to doctor start position
        self.camera.reset(self.doctor.pos)

        # Reset difficulty
        self.difficulty_multiplier = config.DIFFICULTY_START_MULTIPLIER

        # Reset post-game animation timer
        self.post_game_timer = 0.0

    def calculate_difficulty_multiplier(self) -> float:
        """Calculate the current difficulty multiplier based on elapsed time and curve type."""
        if not config.DIFFICULTY_ENABLED:
            return config.DIFFICULTY_START_MULTIPLIER
        
        # Normalize time to [0, 1] range based on ramp time
        t = min(self.elapsed_time / config.DIFFICULTY_RAMP_TIME, 1.0)
        
        start = config.DIFFICULTY_START_MULTIPLIER
        max_mult = config.DIFFICULTY_MAX_MULTIPLIER
        delta = max_mult - start
        
        curve_type = config.DIFFICULTY_CURVE_TYPE.lower()
        steepness = config.DIFFICULTY_CURVE_STEEPNESS
        
        if curve_type == "linear":
            # Simple linear interpolation
            return start + delta * t
        
        elif curve_type == "exponential":
            # Exponential curve: slow start, fast end
            # Use steepness to control the exponent (higher = steeper)
            exponent = 1.0 + steepness * 3.0  # Maps 0.5 -> 2.5
            return start + delta * (t ** exponent)
        
        elif curve_type == "sigmoid":
            # Sigmoid curve: smooth S-curve with gradual start and end
            # Center at t=0.5, use steepness to control transition sharpness
            import math
            # Shift t to [-0.5, 0.5] and scale by steepness
            t_shifted = (t - 0.5) * steepness * 10.0
            sigmoid = 1.0 / (1.0 + math.exp(-t_shifted))
            return start + delta * sigmoid
        
        else:
            # Default to linear if unknown curve type
            return start + delta * t


    def apply_settings(self) -> None:
        """Apply current settings values to the config module."""
        for setting in self.settings:
            if setting["type"] == "action":
                continue
            
            key = setting["key"]
            value = setting["value"]
            
            # Map setting keys to config attributes
            if key == "difficulty_enabled":
                config.DIFFICULTY_ENABLED = value
            elif key == "max_multiplier":
                config.DIFFICULTY_MAX_MULTIPLIER = value
            elif key == "ramp_time":
                config.DIFFICULTY_RAMP_TIME = value
            elif key == "curve_type":
                config.DIFFICULTY_CURVE_TYPE = value
            elif key == "curve_steepness":
                config.DIFFICULTY_CURVE_STEEPNESS = value
            elif key == "agent_count":
                config.AGENT_COUNT = value
            elif key == "infection_prob":
                config.INFECTION_PROBABILITY = value
            elif key == "initial_infected":
                config.INITIAL_INFECTED = value
            elif key == "infection_model":
                config.INFECTION_MODEL = value
            elif key == "lose_threshold_ratio":
                config.LOSE_THRESHOLD_RATIO = value
            elif key == "lose_threshold_seconds":
                config.LOSE_THRESHOLD_SECONDS = value
            elif key == "win_threshold_ratio":
                config.WIN_THRESHOLD_RATIO = value
            elif key == "win_threshold_seconds":
                config.WIN_THRESHOLD_SECONDS = value

    def adjust_setting(self, delta: int) -> None:
        """Adjust the currently selected setting by delta (-1 for left, +1 for right)."""
        setting = self.settings[self.settings_menu_index]
        
        if setting["type"] == "action":
            return  # Can't adjust action items
        
        if setting["type"] == "bool":
            # Toggle boolean
            setting["value"] = not setting["value"]
        
        elif setting["type"] == "enum":
            # Cycle through options
            options = setting["options"]
            current_idx = options.index(setting["value"])
            new_idx = (current_idx + delta) % len(options)
            setting["value"] = options[new_idx]
        
        elif setting["type"] in ("int", "float"):
            # Adjust numeric value
            step = setting["step"]
            min_val = setting["min"]
            max_val = setting["max"]
            
            new_value = setting["value"] + (delta * step)
            new_value = max(min_val, min(max_val, new_value))
            
            if setting["type"] == "int":
                setting["value"] = int(new_value)
            else:
                setting["value"] = round(new_value, 2)


    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Global quit
                if event.key == pygame.K_q:
                    self.running = False

                # ---------- MENU ----------
                if self.state == config.MENU:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_index = (self.menu_index - 1) % len(self.main_menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_index = (self.menu_index + 1) % len(self.main_menu_options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.main_menu_options[self.menu_index]
                        if choice == "Start":
                            self.reset_run()
                            self.state = config.PLAYING
                        elif choice == "Settings":
                            self.state = config.SETTINGS
                            self.settings_menu_index = 0
                        elif choice == "Quit":
                            self.running = False

                # ---------- SETTINGS ----------
                elif self.state == config.SETTINGS:
                    if event.key == pygame.K_ESCAPE:
                        # Cancel and return to menu
                        self.state = config.MENU
                        self.menu_index = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.settings_menu_index = (self.settings_menu_index - 1) % len(self.settings)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.settings_menu_index = (self.settings_menu_index + 1) % len(self.settings)
                    elif event.key == pygame.K_LEFT:
                        self.adjust_setting(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.adjust_setting(1)
                    elif event.key == pygame.K_RETURN:
                        # Check if "Apply & Back" is selected
                        if self.settings[self.settings_menu_index]["type"] == "action":
                            self.apply_settings()
                            self.state = config.MENU
                            self.menu_index = 0

                # ---------- PLAYING ----------
                elif self.state == config.PLAYING:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
                        self.pause_screenshot = self.capture_screen_blur()
                        self.state = config.PAUSED
                        self.menu_index = 0
                    elif event.key == pygame.K_F1:
                        self.show_hud = not self.show_hud
                    elif event.key == pygame.K_1:
                        self.time_scale = config.TIME_SCALE_1
                    elif event.key == pygame.K_2:
                        self.time_scale = config.TIME_SCALE_2
                    elif event.key == pygame.K_3:
                        self.time_scale = config.TIME_SCALE_3

                # ---------- PAUSED ----------
                elif self.state == config.PAUSED:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
                        self.state = config.PLAYING
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_index = (self.menu_index - 1) % len(self.pause_menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_index = (self.menu_index + 1) % len(self.pause_menu_options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.pause_menu_options[self.menu_index]
                        if choice == "Resume":
                            self.state = config.PLAYING
                        elif choice == "Restart":
                            self.reset_run()
                            self.state = config.PLAYING
                        elif choice == "Quit to Menu":
                            self.state = config.MENU
                            self.menu_index = 0

                # ---------- WIN / LOSE ----------
                elif self.state in (config.WIN, config.LOSE):
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_index = (self.menu_index - 1) % len(self.end_menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_index = (self.menu_index + 1) % len(self.end_menu_options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.end_menu_options[self.menu_index]
                        if choice == "Restart":
                            self.reset_run()
                            self.state = config.PLAYING
                        elif choice == "Quit to Menu":
                            self.state = config.MENU
                            self.menu_index = 0
                        elif choice == "Quit":
                            self.running = False
                    elif event.key == pygame.K_r:
                        self.reset_run()
                        self.state = config.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = config.MENU
                        self.menu_index = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.state = config.MENU
                        self.menu_index = 0

            elif event.type == pygame.MOUSEMOTION:
                # Hover selection for menus
                if self.state in (config.MENU, config.PAUSED, config.WIN, config.LOSE):
                    mx, my = event.pos
                    for i, r in enumerate(self.menu_option_rects or []):
                        if r.collidepoint(mx, my):
                            self.menu_index = i
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Menu clicks
                if event.button == 1 and self.state in (config.MENU, config.PAUSED, config.WIN, config.LOSE):
                    mx, my = event.pos
                    for i, r in enumerate(self.menu_option_rects or []):
                        if r.collidepoint(mx, my):
                            self.menu_index = i
                            # Simulate pressing Enter
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
                            return

                # Gameplay clicks
                if self.state == config.PLAYING:
                    if event.button == 1:
                        self.doctor.try_cure(self.agents)
                    elif event.button == 3:
                        self.doctor.try_shoot()



    def update(self, dt: float) -> None:
        # Handle post-game animation states (tick doctor animation + timer)
        if self.state in (config.WIN_ANIMATION, config.LOSE_ANIMATION):
            self.doctor.update(dt, camera=self.camera, hospital_map=self.map)
            self.camera.update(self.doctor.pos, dt)
            self.post_game_timer += dt
            if self.post_game_timer >= config.POST_GAME_ANIM_DURATION:
                # Transition to the final menu state
                if self.state == config.WIN_ANIMATION:
                    self.state = config.WIN
                else:
                    self.state = config.LOSE
                self.menu_index = 0
            return

        # Only simulate while playing
        if self.state != config.PLAYING:
            return
        
        # Update elapsed time
        self.elapsed_time += dt
        
        # Calculate current difficulty multiplier
        self.difficulty_multiplier = self.calculate_difficulty_multiplier()
        
        # Update doctor (world-space, camera-aware)
        self.doctor.update(dt, camera=self.camera, hospital_map=self.map)

        # Update camera to follow doctor
        self.camera.update(self.doctor.pos, dt)

        # Collect deferred projectile from shooting animation
        proj = self.doctor.collect_projectile()
        if proj is not None:
            self.projectiles.append(proj)

        # Update agents with difficulty scaling + map collisions
        for a in self.agents:
            a.update(dt, self.difficulty_multiplier)
            a.bounce_off_map_walls(self.map)

        if config.ENABLE_AGENT_COLLISIONS:
            resolve_agent_collisions(self.agents)
        
        # ---- Projectiles update + hit detection ----
        for p in self.projectiles:
            p.update(dt, hospital_map=self.map)

        # Check hits (projectile vs infected agents)
        # If a projectile hits an infected agent, cure it and remove projectile.
        survivors: list[Projectile] = []
        for p in self.projectiles:
            hit = False
            for a in self.agents:
                if a.strain_id is None:
                    continue
                # circle-circle collision: agent radius + projectile radius
                if (a.pos - p.pos).length_squared() <= (a.radius + p.radius) ** 2:
                    a.strain_id = None
                    hit = True
                    break
            if (not hit) and (not p.is_dead()):
                survivors.append(p)

        self.projectiles = survivors


        # ---- Stats tracking (every frame) ----
        self.strain_counts = {sid: 0 for sid in config.STRAINS}
        for a in self.agents:
            if a.strain_id is not None:
                self.strain_counts[a.strain_id] += 1
        
        self.infected_count = sum(self.strain_counts.values())
        self.healthy_count = len(self.agents) - self.infected_count
        self.infected_ratio = self.infected_count / max(1, len(self.agents))

        # ---- Infection curve history sampling ----
        self.history_timer += dt
        if self.history_timer >= config.HISTORY_SAMPLE_DT:
            self.history_timer = 0.0
            self.ratio_history.append(self.infected_ratio)
            for sid in config.STRAINS:
                ratio = self.strain_counts[sid] / max(1, len(self.agents))
                self.strain_histories[sid].append(ratio)

        # ---- LOSE condition tracking ----
        if self.infected_ratio > config.LOSE_THRESHOLD_RATIO:
            self.time_above_threshold += dt
        else:
            self.time_above_threshold = 0.0

        if self.time_above_threshold >= config.LOSE_THRESHOLD_SECONDS:
            self.state = config.LOSE_ANIMATION
            self.post_game_timer = 0.0
            self.doctor.set_end_state(won=False)

        # ---- WIN condition tracking ----
        # Added warmup period to prevent instant-win at game start
        if self.infected_ratio < config.WIN_THRESHOLD_RATIO and self.elapsed_time > config.WIN_CHECK_WARMUP:
            self.time_below_win_threshold += dt
        else:
            self.time_below_win_threshold = 0.0

        if self.time_below_win_threshold >= config.WIN_THRESHOLD_SECONDS:
            self.state = config.WIN_ANIMATION
            self.post_game_timer = 0.0
            self.doctor.set_end_state(won=True)

    def capture_screen_blur(self) -> pygame.Surface:
        """Capture the current screen and apply a simple blur effect."""
        # Get actual screen surface
        raw = self.screen.copy()
        # Scale down then up to achieve a cheap 'pixelated' blur
        small = pygame.transform.smoothscale(raw, (config.WIDTH // 8, config.HEIGHT // 8))
        blurred = pygame.transform.smoothscale(small, (config.WIDTH, config.HEIGHT))
        return blurred

    def draw(self) -> None:
        # Draw scrollable map background (camera-aware, zoom-aware)
        self.map.draw(self.screen, self.camera)

        # ---------- MENU ----------
        if self.state == config.MENU:
            self.menu_option_rects = draw_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                self.logo,
                self.main_menu_options,
                self.menu_index,
                subtitle="Up/Down Arrow Keys + Enter",
                background=self.menu_background,
            )
            pygame.display.flip()
            return

        # ---------- SETTINGS ----------
        if self.state == config.SETTINGS:
            self.menu_option_rects = draw_settings_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                self.settings,
                self.settings_menu_index,
                background=self.menu_background,
            )
            pygame.display.flip()
            return

        # ---------- POST-GAME ANIMATION (only doctor, no agents) ----------
        if self.state in (config.WIN_ANIMATION, config.LOSE_ANIMATION):
            self.doctor.draw(self.screen, camera=self.camera)
            pygame.display.flip()
            return


        # ---------- WORLD (PLAYING / PAUSED / WIN / LOSE) ----------
        if self.state == config.PAUSED and self.pause_screenshot:
            self.screen.blit(self.pause_screenshot, (0, 0))
        else:
            for a in self.agents:
                a.draw(self.screen, self.agent_anims, self.strain_sprites, self.healthy_sprite, camera=self.camera)

            for p in self.projectiles:
                p.draw(self.screen, camera=self.camera)

            # Only draw doctor while actively playing (cleaner for overlays)
            if self.state == config.PLAYING:
                self.doctor.draw(self.screen, camera=self.camera)

        # ---------- HUD / DEBUG ----------
        # HUD should only show in PLAYING
        if self.state == config.PLAYING:
            if self.show_hud:
                draw_hud(
                    self.screen,
                    self.font_ui,
                    self.infected_count,
                    self.healthy_count,
                    self.infected_ratio,
                    self.time_above_threshold,
                    self.elapsed_time,
                    self.doctor.ammo,
                    config.PELLET_AMMO_MAX,
                    self.doctor.reload_timer,
                    config.PELLET_RELOAD_TIME,
                    self.doctor.shot_cooldown_timer,
                    self.difficulty_multiplier,
                    self.time_scale,
                    strain_counts=self.strain_counts,
                )

                draw_infection_curve(
                    self.screen,
                    list(self.ratio_history),
                    config.GRAPH_RECT,
                    strain_histories={sid: list(h) for sid, h in self.strain_histories.items()}
                )

            if config.SHOW_FPS:
                draw_fps(self.screen, self.clock, self.font_ui)

        # ---------- OVERLAYS ----------
        if self.state == config.PAUSED:
            # Bundle stats for the overlay
            stats = {
                "elapsed": f"{int(self.elapsed_time // 60):02d}:{int(self.elapsed_time % 60):02d}",
                "healthy": self.healthy_count,
                "infected": self.infected_count,
                "ratio": self.infected_ratio,
                "multiplier": self.difficulty_multiplier
            }
            
            self.menu_option_rects = draw_pause_overlay(
                self.screen,
                self.font_title,
                self.font_ui,
                stats,
                list(self.ratio_history),
                {sid: list(h) for sid, h in self.strain_histories.items()},
                self.pause_menu_options,
                self.menu_index,
                strain_counts=self.strain_counts,
                total_agents=len(self.agents)
            )

        elif self.state == config.WIN:
            self.menu_option_rects = draw_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                "YOU WIN",
                self.end_menu_options,
                self.menu_index,
                subtitle="R = Restart, M = Menu, Q = Quit",
                background=self.menu_background,
            )

        elif self.state == config.LOSE:
            self.menu_option_rects = draw_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                "YOU LOSE",
                self.end_menu_options,
                self.menu_index,
                subtitle="R = Restart, M = Menu, Q = Quit",
                background=self.menu_background,
            )

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt * self.time_scale)
            self.draw()

        pygame.quit()
        sys.exit()
