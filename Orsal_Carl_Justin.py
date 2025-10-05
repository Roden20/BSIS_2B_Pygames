import pygame
import sys
import random
import math

pygame.init()

# ---------------- Screen ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishing")
clock = pygame.time.Clock()
FPS = 60

# ---------------- Colors ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_TOP = (100, 180, 255)
BLUE_BOTTOM = (0, 60, 150)
WATER = (28, 107, 160)
BROWN = (100, 60, 20)
GREEN = (50, 200, 100)
RED = (200, 50, 50)
GRAY = (200, 200, 200)

# ---------------- Fonts ----------------
font_big = pygame.font.SysFont(None, 64)
font = pygame.font.SysFont(None, 32)

# ---------------- States ----------------
MENU = "menu"
READY = "ready"
CASTING = "casting"
GAME_OVER = "game_over"
state = MENU

# ---------------- Menu ----------------
menu_options = ["Start", "Exit"]
menu_index = 0

# ---------------- Hook ----------------
HOOK_X = WIDTH // 2
HOOK_START_Y = 240
HOOK_BOTTOM_Y = HEIGHT - 0
hook_y = HOOK_START_Y
hook_active = False
hook_dir = 0
HOOK_SPEED = 6

# ---------------- Boat ----------------
BOAT_WIDTH = 120
BOAT_HEIGHT = 40
boat_x = WIDTH // 2 - BOAT_WIDTH // 2
boat_y = 161
boat_speed = 3


def draw_boat(x, y):
    # Hull pointing upward
    pygame.draw.polygon(screen, (139, 69, 19), [
        (x + 20, y + BOAT_HEIGHT),  # bottom-left
        (x + BOAT_WIDTH - 20, y + BOAT_HEIGHT),  # bottom-right
        (x + BOAT_WIDTH, y + 20),  # top-right
        (x, y + 20)  # top-left
    ])
    # Cabin on top
    pygame.draw.rect(screen, (160, 82, 45), (x + BOAT_WIDTH // 3, y + 0, BOAT_WIDTH // 3, BOAT_HEIGHT // 2))

    # Outline
    pygame.draw.polygon(screen, BLACK, [
        (x + 20, y + BOAT_HEIGHT),
        (x + BOAT_WIDTH - 20, y + BOAT_HEIGHT),
        (x + BOAT_WIDTH, y + 20),
        (x, y + 20)
    ], 2)
    pygame.draw.rect(screen, BLACK, (x + BOAT_WIDTH // 3, y + 0, BOAT_WIDTH // 3, BOAT_HEIGHT // 2), 2)


# ---------------- Bubbles ----------------
NUM_BUBBLES = 20
bubbles = []

for _ in range(NUM_BUBBLES):
    bubbles.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(200, HEIGHT-60),
        "radius": random.randint(2, 4),
        "speed": random.uniform(0.3, 0.8)  # slow upward speed
    })

# ---------------- Clouds ----------------
NUM_CLOUDS = 5
clouds = []
for _ in range(NUM_CLOUDS):
    clouds.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(20, 100),
        "speed": random.uniform(0.2, 0.5),
        "size": random.randint(50, 100)
    })

def draw_bubbles():
    for bubble in bubbles:
        # Move bubble upward
        bubble["y"] -= bubble["speed"]
        # Reset bubble to bottom if it goes off top
        if bubble["y"] < 200:
            bubble["y"] = HEIGHT - 60
            bubble["x"] = random.randint(0, WIDTH)
        # Draw bubble
        pygame.draw.circle(screen, (200, 220, 255, 50), (int(bubble["x"]), int(bubble["y"])), bubble["radius"])

def draw_clouds():
    for cloud in clouds:
        # Draw cloud (simple ellipses for puff)
        cloud_rects = [
            (cloud["x"], cloud["y"], cloud["size"], cloud["size"]//2),
            (cloud["x"] + cloud["size"]*0.3, cloud["y"] - cloud["size"]*0.1, cloud["size"]*0.6, cloud["size"]//2),
            (cloud["x"] + cloud["size"]*0.6, cloud["y"], cloud["size"]*0.4, cloud["size"]//2)
        ]
        for rect in cloud_rects:
            pygame.draw.ellipse(screen, WHITE, rect)

        # Move cloud
        cloud["x"] += cloud["speed"]
        if cloud["x"] - cloud["size"] > WIDTH:
            cloud["x"] = -cloud["size"]
            cloud["y"] = random.randint(20, 100)
            cloud["speed"] = random.uniform(0.2, 0.5)


# ---------------- Fish ----------------
NUM_FISH = 5

def draw_fish(fish):
    x, y, w, h = fish["rect"]
    color = fish["color"]

    # Body (oval)
    body_rect = pygame.Rect(x, y, w, h)
    pygame.draw.ellipse(screen, BLACK, body_rect.inflate(2, 2))  # outline
    pygame.draw.ellipse(screen, color, body_rect)

    # Tail (triangle)
    tail_points = [
        (x, y + h//2),
        (x - w//3, y),
        (x - w//3, y + h)
    ]
    pygame.draw.polygon(screen, color, tail_points)
    pygame.draw.polygon(screen, BLACK, tail_points, 2)  # outline

    # Eye
    eye_radius = max(2, w//10)
    eye_x = x + int(w * 0.75)
    eye_y = y + h//3
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), eye_radius, 1)

def spawn_fish():
    fish_type = random.choices(
        population=[
            {"color": RED, "size": (44, 22), "speed": random.choice([-2, -1, 1, 2]), "points": 1},       # common
            {"color": GREEN, "size": (34, 18), "speed": random.choice([-3, -2, 2, 3]), "points": 2},     # uncommon
            {"color": (255, 200, 0), "size": (24, 14), "speed": random.choice([-4, -3, 3, 4]), "points": 3} # rare
        ],
        weights=[60, 30, 10],  # probability of each fish type
        k=1
    )[0]
    rect = pygame.Rect(random.randint(80, WIDTH - 220),
                       random.randint(220, HEIGHT - 100),
                       fish_type["size"][0], fish_type["size"][1])
    return {"rect": rect, "vel": fish_type["speed"], "color": fish_type["color"], "points": fish_type["points"]}


fish_list = [spawn_fish() for _ in range(NUM_FISH)]

# ---------------- Ready Timer ----------------
ready_start = 0
READY_DELAY = 1500  # ms

# ---------------- Helper Functions ----------------
def draw_gradient_bg():
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(BLUE_TOP[0] * (1 - t) + BLUE_BOTTOM[0] * t)
        g = int(BLUE_TOP[1] * (1 - t) + BLUE_BOTTOM[1] * t)
        b = int(BLUE_TOP[2] * (1 - t) + BLUE_BOTTOM[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


def draw_waves(offset):
    for base in range(0, HEIGHT, 36):
        pts = []
        for x in range(0, WIDTH + 1, 12):
            y = base + math.sin((x * 0.04) + (offset * 0.06)) * 8
            pts.append((x, y))
        pygame.draw.lines(screen, (255, 255, 255, 40), False, pts, 1)

# Fight minigame
def fight_minigame():
    area_x = WIDTH - 220
    area_y = 140
    area_w = 160
    area_h = HEIGHT - 260

    catch_h = 80
    bar_y = area_y + (area_h // 2) - (catch_h // 2)
    bar_vel = 0.0
    bar_gravity = 0.5
    bar_up_force = 0.6
    bounce_factor = 0.28

    fish_r = pygame.Rect(area_x + 20, random.randint(area_y + 10, area_y + area_h - 30), 24, 14)
    fish_vel = random.choice([-2, 2])

    PROGRESS_MAX = 200
    progress = 0
    fight_time_frames = FPS * 10
    frame = 0
    wave_off = 0

    fight_clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            bar_vel -= bar_up_force
        else:
            bar_vel += bar_gravity

        bar_y += bar_vel
        top_limit = area_y
        bottom_limit = area_y + area_h - catch_h
        if bar_y < top_limit:
            bar_y = top_limit
            bar_vel = 0
        if bar_y > bottom_limit:
            bar_y = bottom_limit
            bar_vel = -bar_vel * bounce_factor

        fish_r.y += fish_vel
        if fish_r.top < area_y:
            fish_r.top = area_y
            fish_vel *= -1
        if fish_r.bottom > area_y + area_h:
            fish_r.bottom = area_y + area_h
            fish_vel *= -1
        if random.random() < 0.06:
            fish_vel += random.choice([-1, 0, 1])
            fish_vel = max(-4, min(4, fish_vel))

        catch_rect = pygame.Rect(area_x + 8, int(bar_y), area_w - 16, catch_h)
        if catch_rect.colliderect(fish_r):
            progress += 2
        else:
            progress -= 1
        progress = max(0, min(PROGRESS_MAX, progress))

        frame += 1
        if progress >= PROGRESS_MAX:
            return True
        if frame >= fight_time_frames:
            return False

        # ---------------- Draw Ocean-Themed UI ----------------
        draw_gradient_bg()
        draw_waves(wave_off)
        wave_off += 2

        # Fight area panel
        pygame.draw.rect(screen, (0, 50, 80, 200), (area_x, area_y, area_w, area_h), border_radius=8)
        pygame.draw.rect(screen, (0, 100, 150, 150), catch_rect, border_radius=6)
        pygame.draw.rect(screen, GREEN, catch_rect.inflate(-6, -6))

        # Fish with outline
        pygame.draw.rect(screen, BLACK, fish_r.inflate(2, 2))
        pygame.draw.rect(screen, RED, fish_r)

        # Progress bar (top-left)
        bar_back = pygame.Rect(40, 40, 260, 24)
        pygame.draw.rect(screen, (0, 0, 50), bar_back, border_radius=6)
        fill_w = int((progress / PROGRESS_MAX) * (bar_back.width - 4))
        if fill_w > 0:
            # Gradient effect
            color = (50, 200, 150)  # light ocean green
            pygame.draw.rect(screen, color, (bar_back.x + 2, bar_back.y + 2, fill_w, bar_back.height - 4), border_radius=4)

        # Instructions panel
        pygame.draw.rect(screen, (0, 0, 50, 120), (40, HEIGHT-70, 380, 50), border_radius=6)
        inst = font.render("Hold SPACE to raise the green bar", True, WHITE)
        screen.blit(inst, (50, HEIGHT-60))

        # Timer panel
        time_left = max(0, int((fight_time_frames - frame) / FPS))
        pygame.draw.rect(screen, (0, 0, 50, 120), (WIDTH-160, 40, 120, 30), border_radius=6)
        tlabel = font.render(f"Time: {time_left}s", True, WHITE)
        screen.blit(tlabel, (WIDTH-150, 45))

        pygame.display.flip()
        fight_clock.tick(FPS)

# Reset game
def reset_game():
    global score, health, fish_list, state, hook_active, hook_dir, hook_y
    score = 0
    health = 3
    fish_list = [spawn_fish() for _ in range(NUM_FISH)]
    state = MENU
    hook_active = False
    hook_dir = 0
    hook_y = HOOK_START_Y

# Draw hearts
def draw_hearts(x, y, health):
    for i in range(health):
        cx = x + i * 30
        pygame.draw.polygon(screen, RED, [
            (cx + 10, y),
            (cx + 20, y + 10),
            (cx + 10, y + 20),
            (cx, y + 10)
        ])

# Draw menu
def draw_menu():
    screen.fill((20, 30, 60))

    # Title
    title = font_big.render("Fishing Game", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    # Start option
    for i, opt in enumerate(menu_options):
        col = WHITE if i != menu_index else GREEN
        txt = font.render(opt, True, col)
        # Adjust Y positions: add extra space for high score
        if i == 1:  # Exit option
            y_pos = 280 + i * 48 + 40  # shift down to make space for High Score
        else:
            y_pos = 280 + i * 48
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y_pos))

    # High Score (displayed between Start and Exit)
    if high_score > 0:
        hs_text = font.render(f"High Score: {high_score}", True, WHITE)
        # Position it between the options
        hs_y = 280 + 48  # right between Start (i=0) and Exit (i=1)
        screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, hs_y))

    # Hint
    hint = font.render("Use UP/DOWN to move, ENTER to select", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))

# Draw casting screen
def draw_casting_screen():
    # ---------------- Background ----------------
    draw_gradient_bg()
    draw_waves(pygame.time.get_ticks() * 0.02)

    # Shoreline at bottom
    pygame.draw.rect(screen, (194, 178, 128), (0, HEIGHT-40, WIDTH, 40))
    pygame.draw.line(screen, (210, 190, 150), (0, HEIGHT-40), (WIDTH, HEIGHT-40), 2)

    # ---------------- Sky ----------------
    for y in range(0, 200):  # top part is sky
        t = y / 199
        r = int(135 * (1 - t) + 100 * t)
        g = int(206 * (1 - t) + 180 * t)
        b = int(235 * (1 - t) + 255 * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Draw moving clouds
    draw_clouds()

    # ---------------- Fish ----------------
    for fish in fish_list:
        draw_fish(fish)  # Use improved fish function with tail and eye

    # ---------------- Water ----------------
    # Optional semi-transparent water overlay for depth
    water_overlay = pygame.Surface((WIDTH, HEIGHT-200), pygame.SRCALPHA)
    water_overlay.fill((28, 107, 160, 60))
    screen.blit(water_overlay, (0, 200))

    # ---------------- Bubbles ----------------
    draw_bubbles()


    # ---------------- Hook collision rectangle ----------------
    hook_rect = pygame.Rect(HOOK_X - 6, int(hook_y), 12, 12)

    # Hook with glow and subtle trail
    hook_color = (255, 255, 255) if hook_active else (200, 200, 255)
    pygame.draw.circle(screen, hook_color, (HOOK_X, int(hook_y)), 8)
    pygame.draw.circle(screen, (255, 255, 255, 50), (HOOK_X, int(hook_y)), 12, 2)
    if hook_active:
        for i in range(3):
            trail_y = int(hook_y - i * 6)
            pygame.draw.circle(screen, (200, 200, 255, 40), (HOOK_X, trail_y), 5 - i, 1)

    # Draw boat
    draw_boat(boat_x, boat_y)

    # Rod base and tip relative to boat
    rod_base = (boat_x + BOAT_WIDTH // 2 - 28, boat_y + 20)
    rod_tip = (boat_x + BOAT_WIDTH // 2, boat_y + 48)
    pygame.draw.line(screen, BROWN, rod_base, rod_tip, 6)
    pygame.draw.line(screen, BLACK, rod_tip, (HOOK_X, hook_y), 2)

    # ---------------- Panels ----------------
    # Score panel (top-right)
    panel_color = (0, 0, 50, 180)
    pygame.draw.rect(screen, panel_color, (WIDTH-210, 20, 190, 70), border_radius=8)
    score_txt = font.render(f"Score: {score}", True, WHITE)
    high_score_txt = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_txt, (WIDTH-200, 30))
    screen.blit(high_score_txt, (WIDTH-200, 60))

    # Health hearts panel (top-left)
    draw_hearts(20, 20, health)

    inst_return = font.render("Press ESC to Return to Menu", True, WHITE)
    screen.blit(inst_return, (20, 160))

    # Instruction panel (bottom-left)
    inst_panel_color = (0, 0, 50, 140)
    pygame.draw.rect(screen, inst_panel_color, (20, HEIGHT-70, 380, 50), border_radius=6)
    inst = font.render("Press SPACE to cast when Ready", True, WHITE)
    screen.blit(inst, (30, HEIGHT-60))

# ---------------- Leaderboard ----------------
LEADERBOARD_FILE = "leaderboard.txt"

def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            scores = [int(line.strip()) for line in f.readlines()]
        scores.sort(reverse=True)
        return scores[:5]
    except FileNotFoundError:
        return []

def save_leaderboard(score):
    scores = load_leaderboard()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        for s in scores:
            f.write(f"{s}\n")

high_score = 0
leaderboard = load_leaderboard()
if leaderboard:
    high_score = leaderboard[0]

# ---------------- Game Variables ----------------
score = 0
health = 3


# ---------------- Main Loop ----------------
running = True
ready_start = 0

while running:
    dt = clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        if state == MENU:
            if ev.type == pygame.KEYDOWN:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_DOWN:
                        menu_index = (menu_index + 1) % len(menu_options)
                    elif ev.key == pygame.K_UP:
                        menu_index = (menu_index - 1) % len(menu_options)
                    elif ev.key == pygame.K_RETURN:
                        choice = menu_options[menu_index]
                        if choice == "Start":
                            state = READY
                            ready_start = pygame.time.get_ticks()
                        elif choice == "Exit":
                            running = False

        elif state == CASTING:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE and not hook_active and health > 0:
                    hook_active = True
                    hook_dir = 1
                    hook_y = HOOK_START_Y

                if ev.key == pygame.K_ESCAPE:
                    reset_game()
                    state = MENU

        elif state == GAME_OVER:
            if ev.type == pygame.KEYDOWN:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        reset_game()

    # ---------------- State updates ----------------
    if state == MENU:
        draw_menu()

    elif state == READY:
        screen.fill((20, 30, 60))
        txt = font_big.render("Ready...", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))
        if pygame.time.get_ticks() - ready_start >= READY_DELAY:
            state = CASTING

    elif state == CASTING:
        # --- Update boat movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            boat_x -= boat_speed
            boat_x = max(40, boat_x)
        if keys[pygame.K_RIGHT]:
            boat_x += boat_speed
            boat_x = min(WIDTH - 40 - BOAT_WIDTH, boat_x)
        HOOK_X = boat_x + BOAT_WIDTH // 2

        # --- Update fish positions ---
        for fish in fish_list:
            fish["rect"].x += fish["vel"]
            if fish["rect"].left < 80:
                fish["rect"].left = 80
                fish["vel"] *= -1
            if fish["rect"].right > WIDTH - 80:
                fish["rect"].right = WIDTH - 80
                fish["vel"] *= -1

        # --- Update hook ---
        if hook_active:
            hook_y += HOOK_SPEED * hook_dir
            if hook_y >= HOOK_BOTTOM_Y:
                hook_dir = -1
            if hook_y <= HOOK_START_Y:
                hook_active = False
                hook_dir = 0
                hook_y = HOOK_START_Y

            # --- Hook collision check ---
            if hook_dir == 1:  # only when going down
                hook_rect = pygame.Rect(HOOK_X - 6, int(hook_y), 12, 12)
                hit_index = None
                for idx, fish in enumerate(fish_list):
                    if hook_rect.colliderect(fish["rect"]):
                        hit_index = idx
                        break

                if hit_index is not None:
                    result = fight_minigame()

                    # ---------------- Score & Health ----------------
                    if result:
                        score += fish_list[hit_index]["points"]
                        fish_list[hit_index] = spawn_fish()
                    else:
                        health -= 1

                    # Update high score immediately
                    if score > high_score:
                        high_score = score

                    # Reset hook
                    hook_active = False
                    hook_dir = 0
                    hook_y = HOOK_START_Y

                    # Check game over
                    if health <= 0:
                        if score > high_score:
                            high_score = score
                        state = GAME_OVER
                        save_leaderboard(high_score)

        # --- Draw Casting Screen ---
        draw_casting_screen()


    elif state == GAME_OVER:
        save_leaderboard(high_score)  # now it should work
        leaderboard = load_leaderboard()
        screen.fill((30, 10, 10))
        over = font_big.render("GAME OVER", True, RED)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 80))
        hint = font.render("Press R to Restart or ESC to Quit", True, WHITE)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2))
        best_txt = font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(best_txt, (WIDTH//2 - best_txt.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()

pygame.quit()
sys.exit()

