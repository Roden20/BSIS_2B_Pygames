import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Race Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)

clock = pygame.time.Clock()
FPS = 60

car_width, car_height = 50, 80

font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 60)

LEADERBOARD_FILE = "leaderboard.txt"


def draw_game(player_car, enemies, score):
    screen.fill(WHITE)

    pygame.draw.rect(screen, BLUE, player_car)

    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.update()


def save_score(new_score):
    scores = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            scores = [int(line.strip()) for line in f.readlines()]

    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]

    with open(LEADERBOARD_FILE, "w") as f:
        for s in scores:
            f.write(str(s) + "\n")

    return scores


def show_leaderboard(scores):
    screen.fill(WHITE)
    title = big_font.render("GAME OVER", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    lb_title = font.render("Leaderboard", True, BLACK)
    screen.blit(lb_title, (WIDTH // 2 - lb_title.get_width() // 2, 130))

    for i, s in enumerate(scores):
        text = font.render(f"{i + 1}. {s}", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 170 + i * 40))

    restart_text = font.render("Press R to Restart or Q to Quit", True, GREEN)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 400))

    pygame.display.update()


def game_loop():
    player_car = pygame.Rect(WIDTH // 2 - car_width // 2, HEIGHT - 100, car_width, car_height)
    enemies = []
    car_speed = 5
    enemy_speed = 5
    score = 0

    running = True
    game_over = False
    top_scores = []

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True
                    if event.key == pygame.K_q:
                        return False

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_car.left > 0:
                player_car.x -= car_speed
            if keys[pygame.K_RIGHT] and player_car.right < WIDTH:
                player_car.x += car_speed

            if random.randint(1, 30) == 1:
                enemy_x = random.randint(0, WIDTH - car_width)
                enemies.append(pygame.Rect(enemy_x, -car_height, car_width, car_height))

            for enemy in enemies[:]:
                enemy.y += enemy_speed
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    score += 1

                    if score % 5 == 0:
                        enemy_speed += 1

            for enemy in enemies:
                if player_car.colliderect(enemy):
                    top_scores = save_score(score)
                    show_leaderboard(top_scores)
                    game_over = True

            draw_game(player_car, enemies, score)

    return False


while True:
    restart = game_loop()
    if not restart:
        break

pygame.quit()