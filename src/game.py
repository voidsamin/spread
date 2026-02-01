from __future__ import annotations

import sys
import pygame

import config
from agents import spawn_agents, resolve_agent_collisions
from doctor import Doctor
from ui import draw_fps, draw_stats, draw_center_message


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


        # Infection stats (updated every frame)
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0

        # Lose-condition timer tracking
        self.time_above_threshold = 0.0

        # Game state
        self.state = config.PLAYING

        # Win-condition timer
        self.time_below_win_threshold = 0.0

        self.running = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_p:
                    if self.state == config.PLAYING:
                        self.state = config.PAUSED
                    elif self.state == config.PAUSED:
                        self.state = config.PLAYING

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left click to cure
                if event.button == 1 and self.state == config.PLAYING:
                    self.doctor.try_cure(self.agents)


    def update(self, dt: float) -> None:
        # Only simulate while playing (future-proof for MENU etc.)
        if self.state != config.PLAYING:
            return
        
        # Update doctor
        self.doctor.update(dt)

        # Update agents
        for a in self.agents:
            a.update(dt)
            a.bounce_off_walls(config.WIDTH, config.HEIGHT)

        if config.ENABLE_AGENT_COLLISIONS:
            resolve_agent_collisions(self.agents)

        # ---- Stats tracking (every frame) ----
        self.infected_count = sum(1 for a in self.agents if a.infected)
        self.healthy_count = len(self.agents) - self.infected_count
        self.infected_ratio = self.infected_count / max(1, len(self.agents))

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

        # Draw agents
        for a in self.agents:
            a.draw(self.screen)
        
        # Draw doctor on top
        self.doctor.draw(self.screen)

        if config.SHOW_FPS:
            draw_fps(self.screen, self.clock, self.font_ui)

        draw_stats(
            self.screen,
            self.font_ui,
            self.infected_count,
            self.healthy_count,
            self.infected_ratio,
            self.time_above_threshold,
        )

        if self.state == config.WIN:
            draw_center_message(self.screen, self.font_title, "YOU WIN", (80, 220, 120))
        elif self.state == config.LOSE:
            draw_center_message(self.screen, self.font_title, "YOU LOSE", (220, 80, 80))
        elif self.state == config.PAUSED:
            draw_center_message(self.screen, self.font_title, "PAUSED", config.UI_COLOR)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
