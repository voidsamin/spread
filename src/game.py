from __future__ import annotations
from collections import deque


import sys
import pygame

import config
from agents import spawn_agents, resolve_agent_collisions
from doctor import Doctor
from projectiles import Projectile
from ui import draw_fps, draw_hud, draw_infection_curve, draw_center_message, draw_menu


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))

        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_TITLE)
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)

        # Spawn agents
        self.agents = spawn_agents()

        # Doctor (player)
        self.doctor = Doctor()

        # Projectiles (vaccine pellets)
        self.projectiles: list[Projectile] = []


        # Infection stats (updated every frame)
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0

        # Lose-condition timer tracking
        self.time_above_threshold = 0.0

        # Initial game state (start at main menu) 
        self.state = config.MENU
        self.menu_index = 0

        # Menu options (for future expansion, currently unused since we have no real menu navigation)
        self.main_menu_options = ["Start", "Quit"]
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

        # Infection ratio history (for curve overlay)
        self.history_timer = 0.0
        maxlen = int(config.HISTORY_SECONDS / config.HISTORY_SAMPLE_DT) + 1
        self.ratio_history = deque(maxlen=maxlen)

        self.running = True

    def reset_run(self) -> None:
        """Reset a play session (used for Restart)."""
        self.agents = spawn_agents()
        self.projectiles.clear()

        # Reset stats/timers
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0
        self.time_above_threshold = 0.0
        self.time_below_win_threshold = 0.0

        # Reset telemetry
        self.elapsed_time = 0.0
        self.history_timer = 0.0
        self.ratio_history.clear()

        # Reset doctor gameplay state (ammo/cooldowns)
        self.doctor.cooldown_timer = 0.0
        self.doctor.shot_cooldown_timer = 0.0
        self.doctor.ammo = config.PELLET_AMMO_MAX
        self.doctor.reload_timer = 0.0

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
                        elif choice == "Quit":
                            self.running = False

                # ---------- PLAYING ----------
                elif self.state == config.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = config.PAUSED
                        self.menu_index = 0
                    elif event.key == pygame.K_F1:
                        self.show_hud = not self.show_hud

                # ---------- PAUSED ----------
                elif self.state == config.PAUSED:
                    if event.key == pygame.K_ESCAPE:
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
                    for i, r in enumerate(getattr(self, "menu_option_rects", [])):
                        if r.collidepoint(mx, my):
                            self.menu_index = i
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Menu clicks
                if event.button == 1 and self.state in (config.MENU, config.PAUSED, config.WIN, config.LOSE):
                    mx, my = event.pos
                    for i, r in enumerate(getattr(self, "menu_option_rects", [])):
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
                        proj = self.doctor.try_shoot()
                        if proj is not None:
                            self.projectiles.append(proj)



    def update(self, dt: float) -> None:
        # Only simulate while playing (future-proof for MENU etc.)
        if self.state != config.PLAYING:
            return
        
        # Update elapsed time
        self.elapsed_time += dt
        
        # Update doctor
        self.doctor.update(dt)

        # Update agents
        for a in self.agents:
            a.update(dt)
            a.bounce_off_walls(config.WIDTH, config.HEIGHT)

        if config.ENABLE_AGENT_COLLISIONS:
            resolve_agent_collisions(self.agents)
        
        # ---- Projectiles update + hit detection ----
        for p in self.projectiles:
            p.update(dt)

        # Check hits (projectile vs infected agents)
        # If a projectile hits an infected agent, cure it and remove projectile.
        survivors: list[Projectile] = []
        for p in self.projectiles:
            hit = False
            for a in self.agents:
                if not a.infected:
                    continue
                # circle-circle collision: agent radius + projectile radius
                if (a.pos - p.pos).length_squared() <= (a.radius + p.radius) ** 2:
                    a.infected = False
                    hit = True
                    break
            if (not hit) and (not p.is_dead()):
                survivors.append(p)

        self.projectiles = survivors


        # ---- Stats tracking (every frame) ----
        self.infected_count = sum(1 for a in self.agents if a.infected)
        self.healthy_count = len(self.agents) - self.infected_count
        self.infected_ratio = self.infected_count / max(1, len(self.agents))

        # ---- Infection curve history sampling ----
        self.history_timer += dt
        if self.history_timer >= config.HISTORY_SAMPLE_DT:
            self.history_timer = 0.0
            self.ratio_history.append(self.infected_ratio)

        # ---- LOSE condition tracking ----
        if self.infected_ratio > config.LOSE_THRESHOLD_RATIO:
            self.time_above_threshold += dt
        else:
            self.time_above_threshold = 0.0

        if self.time_above_threshold >= config.LOSE_THRESHOLD_SECONDS:
            self.state = config.LOSE

        # ---- WIN condition tracking ----
        if self.infected_ratio < config.WIN_THRESHOLD_RATIO:
            self.time_below_win_threshold += dt
        else:
            self.time_below_win_threshold = 0.0

        if self.time_below_win_threshold >= config.WIN_THRESHOLD_SECONDS:
            self.state = config.WIN

    def draw(self) -> None:
        self.screen.fill(config.BG_COLOR)

        # ---------- MENU ----------
        if self.state == config.MENU:
            self.menu_option_rects = draw_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                "SPREAD",
                self.main_menu_options,
                self.menu_index,
                subtitle="Up/Down Arrow Keys + Enter",
            )
            pygame.display.flip()
            return

        # ---------- WORLD (PLAYING / PAUSED / WIN / LOSE) ----------
        for a in self.agents:
            a.draw(self.screen)

        for p in self.projectiles:
            p.draw(self.screen)

        # Only draw doctor while actively playing (cleaner for overlays)
        if self.state == config.PLAYING:
            self.doctor.draw(self.screen)

        # ---------- HUD / DEBUG ----------
        # HUD should only show in PLAYING (optional: also show in PAUSED)
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
                )

                draw_infection_curve(
                    self.screen,
                    list(self.ratio_history),
                    config.GRAPH_RECT,
                )

            if config.SHOW_FPS:
                draw_fps(self.screen, self.clock, self.font_ui)

        # ---------- OVERLAYS ----------
        if self.state == config.PAUSED:
            self.menu_option_rects = draw_menu(
                self.screen,
                self.font_title,
                self.font_ui,
                "PAUSED",
                self.pause_menu_options,
                self.menu_index,
                subtitle="Esc to resume",
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
            )

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
