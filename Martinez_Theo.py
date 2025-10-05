import pygame, sys, random, time

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Catch the Drops")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28, bold=True)

BLUE = (50, 150, 255)
WHITE = (255, 255, 255)
GRAY = (230, 230, 230)
RED = (255, 80, 80)
YELLOW = (255, 200, 0)

player = pygame.Rect(300, 340, 100, 40)

drops = [pygame.Rect(random.randint(0, 580), random.randint(-150, -50), 20, 20) for _ in range(3)]

score = 0
lives = 3
drop_speed = 4

dragging = False
offset_x = 0

game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not game_over and player.collidepoint((mx, my)):
                dragging = True
                offset_x = mx - player.x

            
            if game_over:
                score = 0
                lives = 3
                drop_speed = 4
                for drop in drops:
                    drop.y = random.randint(-200, -50)
                    drop.x = random.randint(0, 580)
                game_over = False

        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        if event.type == pygame.MOUSEMOTION and dragging:
            mx, my = event.pos
            player.x = mx - offset_x
            player.x = max(0, min(player.x, 600 - player.width))

    
    if not game_over:
        for drop in drops:
            drop.y += drop_speed

            
            if player.colliderect(drop):
                score += 1
                drop.y = random.randint(-200, -50)
                drop.x = random.randint(0, 580)

            
            elif drop.y > 400:
                lives -= 1
                drop.y = random.randint(-200, -50)
                drop.x = random.randint(0, 580)

                if lives <= 0:
                    game_over = True

        if score > 0 and score % 10 == 0:
            drop_speed = 4 + (score // 10)

    
    screen.fill(GRAY)
    pygame.draw.rect(screen, BLUE, player, border_radius=10)

    for drop in drops:
        pygame.draw.circle(screen, YELLOW, drop.center, drop.width // 2)
        pygame.draw.circle(screen, WHITE, drop.center, drop.width // 4)

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    lives_text = font.render(f"Lives: {lives}", True, RED)
    screen.blit(score_text, (20, 10))
    screen.blit(lives_text, (480, 10))

    if game_over:
        over_text = font.render("GAME OVER!", True, RED)
        restart_text = font.render("Tap to Restart", True, (0, 0, 0))
        screen.blit(over_text, (280, 160))
        screen.blit(restart_text, (270, 200))

    pygame.display.flip()
    clock.tick(60)