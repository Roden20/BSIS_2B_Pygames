import pygame, sys

pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()

# Colors
WHITE = (255,255,255)
GREEN = (34, 177, 76)
RED = (200,0,0)

# Player
player = pygame.Rect(100, 300, 40, 40)
y_vel = 0
on_ground = False

# Platforms
platforms = [
    pygame.Rect(0, 360, 800, 40),
    pygame.Rect(200, 280, 100, 20),
    pygame.Rect(400, 220, 100, 20),
    pygame.Rect(600, 160, 100, 20)
]

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= 5
    if keys[pygame.K_RIGHT]: player.x += 5
    if keys[pygame.K_SPACE] and on_ground:
        y_vel = -12
        on_ground = False

    # Gravity
    y_vel += 0.5
    player.y += int(y_vel)

    # Platform collision
    on_ground = False
    for plat in platforms:
        if player.colliderect(plat) and y_vel >= 0:
            player.bottom = plat.top
            y_vel = 0
            on_ground = True

    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, player)
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, plat)

    pygame.display.flip()
    clock.tick(60)
