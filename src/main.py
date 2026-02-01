import sys
import pygame

import config
from agents import spawn_agents, resolve_agent_collisions


def draw_fps(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, config.UI_COLOR)
    surface.blit(fps_text, (10, 8))

def draw_stats(surface: pygame.Surface, font: pygame.font.Font, infected: int, healthy: int, ratio: float, t_above: float) -> None:
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

def draw_center_message(surface: pygame.Surface, font: pygame.font.Font, text: str, color) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
    surface.blit(surf, rect)



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

        # Infection stats (updated every frame)
        self.infected_count = 0
        self.healthy_count = 0
        self.infected_ratio = 0.0

        # Lose-condition timer tracking (no lose screen yet; just tracking)
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


    def update(self, dt: float) -> None:
        # Stop simulation if game is over or paused
        if self.state != config.PLAYING:
            return

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


        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
