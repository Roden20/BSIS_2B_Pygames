import pygame 
import random
import sys

# Initialize
pygame.init()

# Screen
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)

# Clock
clock = pygame.time.Clock()

# Bird
bird_size = 30
bird_x = 50
bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.5
jump = -8

# Pipes
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
pipes = []

# Score
score = 0
font = pygame.font.SysFont("Arial", 30)

def draw_bird(x, y):
    pygame.draw.circle(screen, (255, 255, 0), (x, y), bird_size // 2)

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe[0])  # Top pipe
        pygame.draw.rect(screen, GREEN, pipe[1])  # Bottom pipe

def check_collision(bird_rect, pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe[0]) or bird_rect.colliderect(pipe[1]):
            return True
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return True
    return False

# Game loop
running = True
while running:
    screen.fill(BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_velocity = jump

    # Bird physics
    bird_velocity += gravity
    bird_y += bird_velocity
    bird_rect = pygame.Rect(bird_x, bird_y, bird_size, bird_size)
    draw_bird(bird_x, bird_y)

    # Pipe movement
    if len(pipes) == 0 or pipes[-1][0].x < WIDTH - 200:
        pipe_height = random.randint(100, 400)
        top_pipe = pygame.Rect(WIDTH, 0, pipe_width, pipe_height)
        bottom_pipe = pygame.Rect(WIDTH, pipe_height + pipe_gap, pipe_width, HEIGHT - pipe_height - pipe_gap)
        pipes.append((top_pipe, bottom_pipe))

    new_pipes = []
    for pipe in pipes:
        top, bottom = pipe
        top.x -= pipe_speed
        bottom.x -= pipe_speed
        if top.right > 0:
            new_pipes.append((top, bottom))
        else:
            score += 1
    pipes = new_pipes

    draw_pipes(pipes)

    # Collision
    if check_collision(bird_rect, pipes):
        print("Game Over! Final Score:", score)
        running = False

    # Score display
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
 