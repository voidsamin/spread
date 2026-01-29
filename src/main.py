import sys
import pygame

import config


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

        # Placeholder title text (will be replaced once we add states/menus)
        self.title_surf = self.font_title.render("SPREAD", True, config.WHITE)
        self.title_rect = self.title_surf.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))

        self.running = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt: float) -> None:
        # dt is seconds since last frame (for movement later)
        pass

    def draw(self) -> None:
        self.screen.fill(config.BG_COLOR)

        # Temporary splash / placeholder
        self.screen.blit(self.title_surf, self.title_rect)

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
