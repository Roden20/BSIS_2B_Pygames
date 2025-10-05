"""
2D Pong Game in Pygame with Galaxy Background

Controls:
- Player 1 (Left Paddle): W (up), S (down)
- Player 2 (Right Paddle): UP Arrow, DOWN Arrow
- Press ESC to quit
"""

import pygame
import sys

# --- Game Config ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Pong with Galaxy Background")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # --- Load Galaxy Background ---
    try:
        background = pygame.image.load("galaxy.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = None  # fallback if no image found

    # Paddles and Ball
    paddle1 = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(WIDTH - 60, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    ball_speed = [5, 5]
    score1, score2 = 0, 0

    running = True
    while running:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Player Controls ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= 6
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += 6
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.y -= 6
        if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
            paddle2.y += 6

        # --- Ball Movement ---
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Bounce on top/bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed[1] = -ball_speed[1]

        # Paddle collision
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            ball_speed[0] = -ball_speed[0]

        # Scoring
        if ball.left <= 0:
            score2 += 1
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_speed = [5, 5]
        if ball.right >= WIDTH:
            score1 += 1
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_speed = [-5, 5]

        # --- Draw Everything ---
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((0, 0, 30))  # dark fallback

        pygame.draw.rect(screen, WHITE, paddle1)
        pygame.draw.rect(screen, WHITE, paddle2)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))  # Middle line

        # Draw scores
        score_text = font.render(f"{score1}   {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        # Update screen
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
