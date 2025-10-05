import pygame, sys, random
import numpy as np


pygame.init()
# Game area 600 wide + HUD 200 wide
GAME_W, GAME_H = 600, 400
HUD_W = 200
WIDTH, HEIGHT = GAME_W + HUD_W, GAME_H

pygame.mixer.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Background for game area
bg = pygame.Surface((GAME_W, GAME_H))
bg.fill((20, 20, 40))

def make_beep(frequency=440, duration_ms=200, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms/1000, n_samples, False)
    wave = 32767 * np.sin(2 * np.pi * frequency * t)  # sine wave
    wave = wave.astype(np.int16)
    wave = np.column_stack((wave, wave))  # convert to stereo
    sound = pygame.sndarray.make_sound(wave)
    sound.set_volume(volume)
    return sound


player = pygame.Rect(280, 200, 40, 40)
bullets = []
enemies = []
score = 0
level = 1
game_over = False
shoot_sound = make_beep(600, 100, 0.4)      # short high beep
explosion_sound = make_beep(200, 300, 0.6)  # deeper boom
spawn_timer = pygame.USEREVENT
spawn_delay = 1000
pygame.time.set_timer(spawn_timer, spawn_delay)

enemy_speed = 3

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if not game_over:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx-2, player.top, 4, 10))
            if e.type == spawn_timer:
                enemies.append(pygame.Rect(random.randint(0, GAME_W-40), 0, 40, 40))
        else:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                # restart game
                player = pygame.Rect(280, 200, 40, 40)
                bullets = []
                enemies = []
                score = 0
                level = 1
                enemy_speed = 3
                spawn_delay = 1000
                pygame.time.set_timer(spawn_timer, spawn_delay)
                game_over = False

    if not game_over:
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 5
        if keys[pygame.K_RIGHT] and player.right < GAME_W: player.x += 5
        if keys[pygame.K_UP] and player.top > 0: player.y -= 5
        if keys[pygame.K_DOWN] and player.bottom < GAME_H: player.y += 5

        # Bullets
        for b in bullets[:]:
            b.y -= 6
            if b.bottom < 0: bullets.remove(b)

        # Enemies
        for en in enemies[:]:
            en.y += enemy_speed
            if en.top > GAME_H: enemies.remove(en)

            if player.colliderect(en):
                game_over = True

        # Bullet vs Enemy
        for b in bullets[:]:
            for en in enemies[:]:
                if b.colliderect(en):
                    bullets.remove(b)
                    enemies.remove(en)
                    score += 1
                    explosion_sound.play()  # 🔊 play explosion beep
                break


        # Level system
        new_level = score // 10 + 1
        if new_level != level:
            level = new_level
            enemy_speed += 1
            if spawn_delay > 200:
                spawn_delay -= 100
                pygame.time.set_timer(spawn_timer, spawn_delay)

    # Draw game background
    screen.blit(bg, (0, 0))

    if not game_over:
        pygame.draw.rect(screen, (0,255,0), player)
        for b in bullets:
            pygame.draw.rect(screen, (255,255,0), b)
        for en in enemies:
            pygame.draw.rect(screen, (255,0,0), en)
    else:
        over_txt = font.render("GAME OVER", True, (255,0,0))
        info_txt = font.render("Press R to Restart", True, (255,255,255))
        screen.blit(over_txt, (200, 160))
        screen.blit(info_txt, (180, 200))

# HUD Panel (right side)
    pygame.draw.rect(screen, (0, 0, 200), (GAME_W, 0, HUD_W, HEIGHT))  # blue panel background
    pygame.draw.line(screen, (200,200,200), (GAME_W, 0), (GAME_W, HEIGHT), 2)  # divider line

# Title
    title_font = pygame.font.Font(None, 30)
    title_txt = title_font.render("UPDOWN SHOOTER", True, (240,255,255))
    title_rect = title_txt.get_rect(center=(GAME_W + HUD_W//2,30))
    screen.blit(title_txt, title_rect)

# Score + Level box
    box_rect = pygame.Rect(GAME_W + 20, 80, HUD_W - 40, 100)
    pygame.draw.rect(screen, (255,255,255), box_rect, 3, border_radius=8)  # white outline box

    # Score inside box
    txt = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(txt, (box_rect.x + 10, box_rect.y + 20))

    # Level inside box
    lvl_txt = font.render(f"Level: {level}", True, (255,255,0))
    screen.blit(lvl_txt, (box_rect.x + 10, box_rect.y + 60))

   

    pygame.display.flip()
    clock.tick(60)
