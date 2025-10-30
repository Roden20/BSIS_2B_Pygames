import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 48)

# Button settings
button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 50, 100, 100)

# Score
score = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse click
            if button_rect.collidepoint(event.pos):  # Check if button clicked
                score += 1

    # Draw background
    screen.fill(WHITE)

    # Draw button
    pygame.draw.rect(screen, BLUE, button_rect)

    # Draw score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))

    # Update display
    pygame.display.flip()
