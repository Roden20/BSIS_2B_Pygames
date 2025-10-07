import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bug Dodge")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 0, 0)
BLUE  = (0, 100, 255)
BG_COLOR = (30, 30, 30)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 60)

# Player settings
player_width = 60
player_height = 20
player_speed = 7

# Enemy settings
enemy_width = 40
enemy_height = 40
enemy_spawn_rate = 25  # lower = more enemies
enemy_speed = 4
enemy_acceleration = 0.002  # speed up over time

# Score
score = 0
start_ticks = pygame.time.get_ticks()

# Game state
game_over = False

# Background
def draw_background():
    screen.fill(BG_COLOR)

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), (player_width, player_height))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += player_speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)

# Enemy class
class Enemy:
    def __init__(self):
        x = random.randint(0, SCREEN_WIDTH - enemy_width)
        self.rect = pygame.Rect(x, 0, enemy_width, enemy_height)

    def update(self):
        global enemy_speed
        self.rect.y += int(enemy_speed)

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

# Game Over screen
def show_game_over():
    draw_background()
    game_over_text = large_font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    retry_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 250))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 350))
    screen.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, 400))
    pygame.display.update()

# Reset function
def reset_game():
    global enemies, score, start_ticks, game_over, enemy_speed
    enemies = []
    score = 0
    start_ticks = pygame.time.get_ticks()
    enemy_speed = 4
    game_over = False
    player.rect.x = SCREEN_WIDTH // 2

# Initialize player and enemies
player = Player()
enemies = []

# Game loop
running = True
frame_count = 0

while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        frame_count += 1
        draw_background()

        # Move and draw player
        player.move(keys)
        player.draw()

        # Spawn enemies
        if frame_count % enemy_spawn_rate == 0:
            enemies.append(Enemy())

        # Update and draw enemies
        for enemy in enemies[:]:
            enemy.update()
            enemy.draw()

            # Check collision
            if enemy.rect.colliderect(player.rect):
                game_over = True

            # Remove enemies off screen
            if enemy.rect.top > SCREEN_HEIGHT:
                enemies.remove(enemy)

        # Update score and difficulty
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        score = int(seconds)
        enemy_speed += enemy_acceleration  # Speed increases over time

        # Show score
        score_display = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_display, (10, 10))

    else:
        show_game_over()
        if keys[pygame.K_r]:
            reset_game()
        elif keys[pygame.K_q]:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()