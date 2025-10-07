import pygame
import random
import math
import os

# ------------ Configuration ------------
WIDTH, HEIGHT = 480, 700
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -9.5
HOLD_BOOST = -0.18  # extra upward while holding flap
PIPE_GAP = 180
PIPE_FREQ = 1500  # milliseconds
STAR_FREQ = 3500  # milliseconds
SCROLL_SPEED = 2.4
BG_COLOR = (90, 185, 255)
FONT_NAME = None
HIGH_SCORE_FILE = 'highscore.txt'

# ------------ Pygame Initialization ------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Birch')
clock = pygame.time.Clock()
try:
    pygame.mixer.init()
except Exception:
    pass

# ------------ Helpers ------------
def load_highscore():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(int(score)))
    except Exception:
        pass

# ------------ Sprites ------------
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.orig_image = pygame.Surface((44, 32), pygame.SRCALPHA)
        # draw a simple bird with a beak and eye
        pygame.draw.ellipse(self.orig_image, (255, 215, 120), (0, 6, 44, 22))
        pygame.draw.polygon(self.orig_image, (255, 160, 60), [(36, 14), (44, 10), (44, 18)])
        pygame.draw.circle(self.orig_image, (10,10,10), (14, 14), 3)
        self.image = self.orig_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.alive = True
        self.score = 0
        self.mult = 1
        self.flap_time = 0

    def update(self, dt, holding):
        if not self.alive:
            # fall
            self.vel.y += GRAVITY * 1.6
        else:
            # normal gravity
            self.vel.y += GRAVITY
            if holding:
                self.vel.y += HOLD_BOOST

        # apply velocity
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # rotation for visual feedback
        target_angle = max(-45, min(70, -self.vel.y * 4))
        self.angle = self.angle + (target_angle - self.angle) * 0.12
        self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

        # clamp to screen
        if self.rect.top < 0:
            self.pos.y = self.rect.height // 2
            self.vel.y = 0
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.pos.y = HEIGHT - self.rect.height // 2
            self.vel.y = 0
            self.rect.bottom = HEIGHT
            self.alive = False

    def flap(self):
        self.vel.y = FLAP_STRENGTH
        self.flap_time = pygame.time.get_ticks()


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, gap_center):
        super().__init__()
        self.width = 78
        self.x = x
        self.gap_center = gap_center
        self.wobble_phase = random.random() * 6.28
        # we will not use a simple image - draw dynamically in draw method
        self.passed = False

    def update(self, dt):
        self.x -= SCROLL_SPEED * dt
        self.wobble_phase += 0.01 * dt
        if self.x < -self.width - 50:
            self.kill()

    def draw(self, surface):
        wobble = math.sin(self.wobble_phase) * 6
        top_rect = pygame.Rect(self.x + wobble, -2000, self.width, self.gap_center - PIPE_GAP // 2 + 2000)
        bottom_rect = pygame.Rect(self.x - wobble, self.gap_center + PIPE_GAP // 2, self.width, 2000)

        # pipe body
        pygame.draw.rect(surface, (30, 120, 40), top_rect)
        pygame.draw.rect(surface, (30, 120, 40), bottom_rect)
        # pipe rim (rounded-ish)
        rim_h = 18
        pygame.draw.rect(surface, (20, 90, 30), (top_rect.x - 2, top_rect.bottom - rim_h, top_rect.width + 4, rim_h))
        pygame.draw.rect(surface, (20, 90, 30), (bottom_rect.x - 2, bottom_rect.y, bottom_rect.width + 4, rim_h))

    def collide_with(self, rect):
        # collision test by creating rects matching drawn pipes
        wobble = math.sin(self.wobble_phase) * 6
        top_rect = pygame.Rect(self.x + wobble, -2000, self.width, self.gap_center - PIPE_GAP // 2 + 2000)
        bottom_rect = pygame.Rect(self.x - wobble, self.gap_center + PIPE_GAP // 2, self.width, 2000)
        return rect.colliderect(top_rect) or rect.colliderect(bottom_rect)


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 10
        self.angle = 0
        self.collected = False

    def update(self, dt):
        self.x -= SCROLL_SPEED * dt
        self.angle += 0.08 * dt
        if self.x < -50:
            self.kill()

    def draw(self, surface):
        # draw small star by rotated polygon
        cx, cy = int(self.x), int(self.y)
        pts = []
        for i in range(5):
            a = self.angle + i * 2 * math.pi / 5
            r = self.radius if i % 2 == 0 else self.radius / 2
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        pygame.draw.polygon(surface, (255, 235, 95), pts)

    def collide_with(self, rect):
        return rect.collidepoint(self.x, self.y)


# ------------ Background Parallax ------------
class Parallax:
    def __init__(self):
        # layers: clouds, trees, mountains
        self.clouds = [{'x': random.randint(0, WIDTH), 'y': random.randint(20, 140), 's': random.uniform(0.6,1.2)} for _ in range(8)]
        self.trees_x = [i * 160 for i in range(6)]

    def update(self, dt):
        for c in self.clouds:
            c['x'] -= 0.2 * SCROLL_SPEED * c['s'] * dt
            if c['x'] < -200:
                c['x'] = WIDTH + random.randint(0,200)
                c['y'] = random.randint(20,140)
        for i in range(len(self.trees_x)):
            self.trees_x[i] -= 0.6 * SCROLL_SPEED * dt
            if self.trees_x[i] < -200:
                self.trees_x[i] = WIDTH + random.randint(20,200)

    def draw(self, surface):
        # mountains
        pygame.draw.polygon(surface, (120, 140, 160), [(-100, HEIGHT - 140), (120, HEIGHT - 340), (450, HEIGHT - 140)])
        pygame.draw.polygon(surface, (100, 120, 140), [(120, HEIGHT - 140), (300, HEIGHT - 360), (620, HEIGHT - 140)])
        # clouds
        for c in self.clouds:
            pygame.draw.ellipse(surface, (255,255,255), (c['x'], c['y'], 120 * c['s'], 50 * c['s']))
        # trees (simple birch-like trunks)
        for i,x in enumerate(self.trees_x):
            trunk = pygame.Rect(x, HEIGHT-160, 28, 120)
            pygame.draw.rect(surface, (245, 245, 240), trunk)
            # dark slashes
            pygame.draw.line(surface, (50,50,50), (x+6, HEIGHT-140), (x+10, HEIGHT-120), 2)
            pygame.draw.line(surface, (50,50,50), (x+18, HEIGHT-110), (x+6, HEIGHT-90), 2)


# ------------ UI Elements ------------
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = pygame.font.Font(FONT_NAME, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, (30,30,30), self.rect, border_radius=8)
        txt = self.font.render(self.text, True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ------------ Main Game Class ------------
class Game:
    def __init__(self):
        self.running = True
        self.playing = False
        self.bird = Bird(110, HEIGHT // 2)
        self.pipes = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.parallax = Parallax()
        self.last_pipe = pygame.time.get_ticks()
        self.last_star = pygame.time.get_ticks()
        self.font = pygame.font.Font(FONT_NAME, 32)
        self.small_font = pygame.font.Font(FONT_NAME, 18)
        self.highscore = load_highscore()
        self.score = 0
        self.mult = 1
        self.hud_fade = 255
        self.bg_shift = 0
        self.menu = True
        self.paused = False
        self.start_button = Button((WIDTH//2-70, HEIGHT//2+60, 140, 46), 'Start')

    def reset(self):
        self.bird = Bird(110, HEIGHT // 2)
        self.pipes.empty()
        self.stars.empty()
        self.last_pipe = pygame.time.get_ticks()
        self.last_star = pygame.time.get_ticks()
        self.score = 0
        self.mult = 1
        self.playing = True
        self.paused = False
        self.menu = False

    def spawn_pipe(self):
        gap_center = random.randint(160, HEIGHT - 160)
        pipe = Pipe(WIDTH + 40, gap_center)
        self.pipes.add(pipe)

    def spawn_star(self):
        y = random.randint(120, HEIGHT - 160)
        star = Star(WIDTH + 60, y)
        self.stars.add(star)

    def handle_events(self):
        holding = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not self.playing:
                        if self.menu:
                            self.reset()
                        else:
                            self.reset()
                    if self.bird.alive:
                        self.bird.flap()
                if event.key == pygame.K_p:
                    if self.playing:
                        self.paused = not self.paused
                if event.key == pygame.K_r:
                    self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.playing and self.menu:
                    if self.start_button.clicked(event.pos):
                        self.reset()
                if self.playing and self.bird.alive:
                    self.bird.flap()
        # check holding state
        keys = pygame.key.get_pressed()
        holding = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        return holding

    def update(self, dt, holding):
        if not self.playing:
            return
        if self.paused:
            return
        # update parallax
        self.parallax.update(dt)

        # spawn pipes
        now = pygame.time.get_ticks()
        if now - self.last_pipe > PIPE_FREQ:
            self.spawn_pipe()
            self.last_pipe = now
        if now - self.last_star > STAR_FREQ:
            self.spawn_star()
            self.last_star = now

        # update bird
        self.bird.update(dt, holding)

        # update pipes & stars
        for p in list(self.pipes):
            p.update(dt)
            # score when passing
            if not p.passed and p.x + p.width/2 < self.bird.rect.centerx:
                p.passed = True
                self.score += 1 * self.mult
                # small chance to increase multiplier
                if random.random() < 0.12:
                    self.mult += 1
        for s in list(self.stars):
            s.update(dt)

        # collisions
        if self.bird.alive:
            for p in self.pipes:
                if p.collide_with(self.bird.rect):
                    self.bird.alive = False
            for s in list(self.stars):
                if s.collide_with(self.bird.rect):
                    self.mult = min(5, self.mult + 1)
                    s.kill()

        # if bird died, check highscore when fully stopped
        if not self.bird.alive and self.bird.rect.bottom >= HEIGHT - 1:
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)
            self.playing = False
            self.menu = False

    def draw_hud(self, surface):
        # score
        score_surf = self.font.render(str(self.score), True, (255,255,255))
        surface.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 30))
        # multiplier
        mult_surf = self.small_font.render(f'x{self.mult}', True, (255,235,120))
        surface.blit(mult_surf, (WIDTH//2 + score_surf.get_width()//2 + 8, 36))
        # highscore
        hs = self.small_font.render(f'Best: {self.highscore}', True, (255,255,255))
        surface.blit(hs, (12, 12))

    def draw(self, surface):
        # background sky
        surface.fill(BG_COLOR)
        # parallax
        self.parallax.draw(surface)

        # draw pipes
        for p in self.pipes:
            p.draw(surface)
        # draw stars
        for s in self.stars:
            s.draw(surface)
        # draw ground
        pygame.draw.rect(surface, (85, 58, 30), (0, HEIGHT-60, WIDTH, 60))
        # tree stump pattern
        for i in range(0, WIDTH, 30):
            pygame.draw.rect(surface, (95,75,40), (i, HEIGHT-60, 10, 60))

        # bird
        surface.blit(self.bird.image, self.bird.rect)

        # HUD
        if self.playing:
            self.draw_hud(surface)
        else:
            if self.menu:
                title = self.font.render('Flappy Birch', True, (255,255,255))
                surface.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
                subtitle = self.small_font.render('Hold space for a longer lift. Collect stars for multipliers!', True, (240,240,240))
                surface.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
                self.start_button.draw(surface)
                hs = self.small_font.render(f'Best: {self.highscore}', True, (255,255,255))
                surface.blit(hs, hs.get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))
            else:
                # game over
                go = self.font.render('Game Over', True, (255, 40, 40))
                surface.blit(go, go.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
                sc = self.small_font.render(f'Score: {self.score}   Best: {self.highscore}', True, (230,230,230))
                surface.blit(sc, sc.get_rect(center=(WIDTH//2, HEIGHT//2 + 6)))
                retry = self.small_font.render('Press R to Retry or Space to Start', True, (210,210,210))
                surface.blit(retry, retry.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

        # if paused overlay
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((10,10,10,150))
            surface.blit(overlay, (0,0))
            ptxt = self.font.render('Paused', True, (255,255,255))
            surface.blit(ptxt, ptxt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    def run(self):
        while self.running:
            dt = clock.tick(FPS) / 16.6667  # approx speed normalization so 1 unit ~ 60fps frame
            holding = self.handle_events()
            self.update(dt, holding)
            self.draw(screen)
            pygame.display.flip()
        pygame.quit()


# ------------ Main ------------
if '_main_':
    game = Game()
    game.run()