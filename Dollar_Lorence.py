import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Tank Battle")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (34, 177, 76)
GRAY = (100, 100, 100)

# Fonts
font = pygame.font.SysFont("Arial", 28, bold=True)


class Tank:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3
        self.rot_speed = 4
        self.color = color
        self.controls = controls
        self.bullets = []
        self.health = 5

    def move(self, keys, walls):
        old_x, old_y = self.x, self.y

        if keys[self.controls["left"]]:
            self.angle += self.rot_speed
        if keys[self.controls["right"]]:
            self.angle -= self.rot_speed
        if keys[self.controls["forward"]]:
            self.x += self.speed * math.cos(math.radians(-self.angle))
            self.y += self.speed * math.sin(math.radians(-self.angle))
        if keys[self.controls["backward"]]:
            self.x -= self.speed * math.cos(math.radians(-self.angle))
            self.y -= self.speed * math.sin(math.radians(-self.angle))

        # Keep inside screen
        self.x = max(20, min(WIDTH - 20, self.x))
        self.y = max(20, min(HEIGHT - 20, self.y))

        # Tank rectangle for collision
        rect = pygame.Rect(self.x - 20, self.y - 20, 40, 40)
        for wall in walls:
            if rect.colliderect(wall):
                self.x, self.y = old_x, old_y  # undo move

    def fire(self):
        # Bullet starts at tank center, moves in facing direction
        dx = math.cos(math.radians(-self.angle))
        dy = math.sin(math.radians(-self.angle))
        bullet = {"x": self.x, "y": self.y, "dx": dx, "dy": dy}
        self.bullets.append(bullet)

    def update_bullets(self, opponent, walls):
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"] * 8
            bullet["y"] += bullet["dy"] * 8

            # Remove if off screen
            if bullet["x"] < 0 or bullet["x"] > WIDTH or bullet["y"] < 0 or bullet["y"] > HEIGHT:
                self.bullets.remove(bullet)
                continue

            # Wall collision
            hit_wall = False
            for wall in walls:
                if wall.collidepoint(bullet["x"], bullet["y"]):
                    hit_wall = True
                    break
            if hit_wall:
                self.bullets.remove(bullet)
                continue

            # Opponent collision
            opp_rect = pygame.Rect(opponent.x - 20, opponent.y - 20, 40, 40)
            if opp_rect.collidepoint(bullet["x"], bullet["y"]):
                opponent.health -= 1
                self.bullets.remove(bullet)

    def draw(self):
        # Draw tank body
        rect = pygame.Rect(self.x - 20, self.y - 20, 40, 40)
        pygame.draw.rect(screen, self.color, rect)

        # Draw gun (rotated line)
        gun_length = 30
        end_x = self.x + gun_length * math.cos(math.radians(-self.angle))
        end_y = self.y + gun_length * math.sin(math.radians(-self.angle))
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 5)

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, BLACK, (int(bullet["x"]), int(bullet["y"])), 5)

        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 35, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 35, 8 * self.health, 5))


# Controls
controls_p1 = {"left": pygame.K_a, "right": pygame.K_d,
               "forward": pygame.K_w, "backward": pygame.K_s, "fire": pygame.K_SPACE}
controls_p2 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT,
               "forward": pygame.K_UP, "backward": pygame.K_DOWN, "fire": pygame.K_RETURN}

# Tanks
player1 = Tank(150, HEIGHT // 2, BLUE, controls_p1)
player2 = Tank(WIDTH - 150, HEIGHT // 2, RED, controls_p2)

# Walls
walls = [
    pygame.Rect(350, 150, 60, 200),
    pygame.Rect(500, 100, 80, 120)
]


def draw_background():
    screen.fill((180, 220, 180))  # battlefield green
    for wall in walls:
        pygame.draw.rect(screen, GRAY, wall)


# Main loop
running = True
winner = None
while running:
    clock.tick(60)
    draw_background()

    keys = pygame.key.get_pressed()
    player1.move(keys, walls)
    player2.move(keys, walls)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == player1.controls["fire"]:
                player1.fire()
            if event.key == player2.controls["fire"]:
                player2.fire()

    # Update bullets
    player1.update_bullets(player2, walls)
    player2.update_bullets(player1, walls)

    # Draw tanks
    player1.draw()
    player2.draw()

    # Winner check
    if player1.health <= 0:
        winner = "Player 2 Wins!"
        running = False
    elif player2.health <= 0:
        winner = "Player 1 Wins!"
        running = False

    pygame.display.flip()

# End screen
screen.fill(BLACK)
msg = font.render(winner, True, WHITE)
screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()
sys.exit()
