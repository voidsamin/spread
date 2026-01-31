import sys
import pygame

import config
from agents import spawn_agents, resolve_agent_collisions


def draw_fps(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, config.UI_COLOR)
    surface.blit(fps_text, (10, 8))


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

        self.running = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt: float) -> None:
        for a in self.agents:
            a.update(dt)
            a.bounce_off_walls(config.WIDTH, config.HEIGHT)

        if config.ENABLE_AGENT_COLLISIONS:
            resolve_agent_collisions(self.agents)

    def draw(self) -> None:
        self.screen.fill(config.BG_COLOR)

        # Draw agents
        for a in self.agents:
            a.draw(self.screen)

        if config.SHOW_FPS:
            draw_fps(self.screen, self.clock, self.font_ui)

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
