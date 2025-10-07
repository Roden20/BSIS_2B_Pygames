import pygame
import time
import random

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# Clock & speed
clock = pygame.time.Clock()
SPEED = 20 # Increase for difficulty

# Snake settings
block_size = 5
font = pygame.font.SysFont(None, 35)

# Score function
def draw_score(score):
    value = font.render(f"Score: {score}", True, WHITE)
    win.blit(value, [10, 10])

# Game over message
def message(msg, color):
    mesg = font.render(msg, True, color)
    win.blit(mesg, [WIDTH // 6, HEIGHT // 3])

# Main game loop
def gameLoop():
    game_over = False
    game_close = False

    # Snake start position
    x = WIDTH // 2
    y = HEIGHT // 2

    x_change = 0
    y_change = 0

    snake = []
    length = 1

    # Food position
    foodx = round(random.randrange(0, WIDTH - block_size) / 20.0) * 20.0
    foody = round(random.randrange(0, HEIGHT - block_size) / 20.0) * 20.0

    while not game_over:

        while game_close:
            win.fill(BLACK)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            draw_score(length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = block_size
                    x_change = 0

        # Boundary check
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += x_change
        y += y_change
        win.fill(BLACK)

        pygame.draw.rect(win, RED, [foodx, foody, block_size, block_size])

        head = []
        head.append(x)
        head.append(y)
        snake.append(head)

        if len(snake) > length:
            del snake[0]

        # Collision with self
        for segment in snake[:-1]:
            if segment == head:
                game_close = True

        # Draw snake
        for seg in snake:
            pygame.draw.rect(win, WHITE, [seg[0], seg[1], block_size, block_size])

        draw_score(length - 1)
        pygame.display.update()

        # Eating food
        if x == foodx and y == foody:
            foodx = round(random.randrange(0, WIDTH - block_size) / 20.0) * 20.0
            foody = round(random.randrange(0, HEIGHT - block_size) / 20.0) * 20.0
            length += 1

        clock.tick(SPEED)

    pygame.quit()
    quit()

# Start the game
gameLoop()



