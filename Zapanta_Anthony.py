import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Fish Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)

# Fonts
font = pygame.font.SysFont("Arial", 30)

# --- Bigger Fish ---
fish_img = pygame.Surface((90, 50), pygame.SRCALPHA)  # Bigger size
pygame.draw.ellipse(fish_img, (255, 200, 0), [0, 10, 70, 30])   # Fish body
pygame.draw.polygon(fish_img, (255, 150, 0), [(70, 25), (90, 5), (90, 45)])  # Tail

# --- Bigger Garbage ---
garbage_img = pygame.Surface((60, 60), pygame.SRCALPHA)  # Bigger size
pygame.draw.rect(garbage_img, (100, 100, 100), [10, 10, 40, 40])  # Garbage box
pygame.draw.line(garbage_img, (50, 50, 50), (10, 10), (50, 50), 5)
pygame.draw.line(garbage_img, (50, 50, 50), (50, 10), (10, 50), 5)

# Game variables
objects = []
spawn_timer = 0
missed_fish = 0
caught_garbage = 0
score = 0

# Difficulty scaling
base_speed = 3
extra_speed = 0  # increases as score increases

# Clock
clock = pygame.time.Clock()

def draw_ui():
    screen.fill(BLUE)  # Background like sea
    score_text = font.render(f"Score: {score}", True, WHITE)
    miss_text = font.render(f"Missed Fish: {missed_fish}/8", True, WHITE)
    garbage_text = font.render(f"Garbage: {caught_garbage}/4", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(miss_text, (10, 50))
    screen.blit(garbage_text, (10, 90))

class FallingObject:
    def __init__(self, kind, speed_boost):
        self.kind = kind  # "fish" or "garbage"
        if kind == "fish":
            self.image = fish_img
        else:
            self.image = garbage_img
        self.x = random.randint(50, WIDTH - 100)
        self.y = -70
        self.speed = random.randint(base_speed, base_speed + 3) + speed_boost

    def move(self):
        self.y += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Main game loop
running = True
while running:
    clock.tick(60)
    spawn_timer += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for obj in objects[:]:
                rect = obj.image.get_rect(topleft=(obj.x, obj.y))
                if rect.collidepoint(mx, my):
                    if obj.kind == "fish":
                        score += 1
                        extra_speed = score // 5  # every 5 fish, game speeds up
                    else:
                        caught_garbage += 1
                    objects.remove(obj)

    # Spawn new objects
    if spawn_timer > 40:
        kind = random.choice(["fish"] * 3 + ["garbage"])  # More fish than garbage
        objects.append(FallingObject(kind, extra_speed))
        spawn_timer = 0

    # Update objects
    for obj in objects[:]:
        obj.move()
        if obj.y > HEIGHT:
            if obj.kind == "fish":
                missed_fish += 1
            objects.remove(obj)

    # Check game over
    if missed_fish >= 8 or caught_garbage >= 4:
        screen.fill(BLUE)
        msg = "Game Over!"
        over_text = font.render(msg, True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        running = False
        break

    # Draw everything
    draw_ui()
    for obj in objects:
        obj.draw()

    pygame.display.update()
