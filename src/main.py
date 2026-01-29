import pygame
import sys

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPREAD - Simulation Lab")

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.SysFont(None, 48)
text = font.render("Hello SPREAD!", True, (255, 255, 255))
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background
    screen.fill((30, 30, 30))

    # Draw text
    screen.blit(text, text_rect)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Clean exit
pygame.quit()
sys.exit()
