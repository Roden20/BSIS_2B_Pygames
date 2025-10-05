import pygame
import sys
import random

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
START_FPS = 5
MAX_FPS = 20

GREEN_BG = (50, 200, 50)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
APPLE_RED = (255, 0, 0)
APPLE_STEM = (100, 50, 0)
TONGUE_COLOR = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pink Snake Game with Apple")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def random_food():
    return (random.randrange(0, WIDTH, CELL_SIZE), random.randrange(0, HEIGHT, CELL_SIZE))

def reset_game():
    global snake, direction, score, food, game_over, fps
    snake = [(WIDTH//2, HEIGHT//2)]
    direction = (CELL_SIZE, 0)
    score = 0
    food = random_food()
    game_over = False
    fps = START_FPS


reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                    direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                    direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                    direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                    direction = (CELL_SIZE, 0)
            else:
                if event.key == pygame.K_SPACE:  
                    reset_game()

    if not game_over:
        
        head_x, head_y = snake[-1]
        new_head = (head_x + direction[0], head_y + direction[1])
        snake.append(new_head)

        
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in snake[:-1]):
            game_over = True

        if new_head == food:
            score += 1
            food = random_food()
            fps = min(START_FPS + score // 2, MAX_FPS)
        else:
            snake.pop(0)

    screen.fill(GREEN_BG)

    
    for i, segment in enumerate(snake):
        center_x = segment[0] + CELL_SIZE // 2
        center_y = segment[1] + CELL_SIZE // 2
        pygame.draw.circle(screen, PINK, (center_x, center_y), CELL_SIZE // 2)
        if i == len(snake) - 1:  
            
            eye_radius = CELL_SIZE // 6
            eye_y = center_y - CELL_SIZE // 6
            left_eye_x = center_x - CELL_SIZE // 4
            right_eye_x = center_x + CELL_SIZE // 4
            pygame.draw.circle(screen, BLACK, (left_eye_x, eye_y), eye_radius)
            pygame.draw.circle(screen, BLACK, (right_eye_x, eye_y), eye_radius)
    apple_rect = pygame.Rect(food[0], food[1] + 4, CELL_SIZE, CELL_SIZE // 2)
    pygame.draw.ellipse(screen, APPLE_RED, apple_rect)
    pygame.draw.line(screen, APPLE_STEM, (food[0] + CELL_SIZE//2, food[1] + 4),
                     (food[0] + CELL_SIZE//2, food[1]), 2)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    if game_over:
        over_text = font.render("GAME OVER!", True, APPLE_RED)
        screen.blit(over_text, (WIDTH//2 - 200, HEIGHT//2 - 20))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()




