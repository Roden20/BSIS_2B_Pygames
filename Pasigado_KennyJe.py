import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
BALL_RADIUS = 50

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Set up the ball
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed_x = 5
ball_speed_y = 5

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.FINGERDOWN:
            ball_speed_x = random.choice([-5, 5])
            ball_speed_y = random.choice([-5, 5])

    # Move the ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Bounce the ball off the edges
    if ball_x - BALL_RADIUS < 0 or ball_x + BALL_RADIUS > WIDTH:
        ball_speed_x *= -1
    if ball_y - BALL_RADIUS < 0 or ball_y + BALL_RADIUS > HEIGHT:
        ball_speed_y *= -1

    # Draw everything
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_RADIUS)

    # Update the display
    pygame.display.flip()
    pygame.time.Clock().tick(60)