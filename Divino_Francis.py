import pygame
import random
import time

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 3
TITLE = "Whack The Evil Rat"

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

COLOR_GRASS_DARK = (100, 150, 70)
COLOR_GRASS_LIGHT = (140, 190, 110)
COLOR_HOLE_EDGE = (60, 40, 30)
COLOR_HOLE_OPENING = (40, 20, 10)

COLOR_SKY_HORIZON = (150, 200, 255)
COLOR_SKY_TOP = (90, 150, 200)

COLOR_RAT = (40, 40, 40)
COLOR_RAT_EYES = (255, 0, 0)
COLOR_BOMB = (50, 50, 50)
COLOR_NUKE = (255, 100, 0)

COLOR_TEXT = (20, 20, 20)
COLOR_TITLE_OUTLINE = (0, 0, 0)
COLOR_BUTTON = (90, 180, 255)
COLOR_BUTTON_HOVER = (120, 210, 255)
COLOR_RESTART = (255, 180, 90)
COLOR_NUKE_EXPLOSION = (255, 0, 0)
COLOR_SMASH_DUST = (160, 82, 45)

MAX_MISSES = 6
MAX_BOMB_STRIKES = 2
MAX_NUKE_STRIKES = 1
RAT_SCORE_VALUE = 1
BOMB_SCORE_VALUE = -2
SMASH_DURATION = 0.15

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

try:
    FONT_L = pygame.font.SysFont('Inter', 48)
    FONT_M = pygame.font.SysFont('Inter', 28)
    FONT_S = pygame.font.SysFont('Inter', 18)
except:
    FONT_L = pygame.font.Font(None, 48)
    FONT_M = pygame.font.Font(None, 28)
    FONT_S = pygame.font.Font(None, 18)

game_state = "MENU"
score = 0
misses = 0
bomb_strikes = 0
nuke_strikes = 0
active_object = None
last_spawn_time = time.time()
base_time_visible = 2.0
spawn_interval = 1.5
last_smash = None

HOLE_RADIUS = 50
HOLE_PADDING = 50
GRID_START_X = (SCREEN_WIDTH - (GRID_SIZE * 2 * HOLE_RADIUS + (GRID_SIZE - 1) * HOLE_PADDING)) // 2
GRID_START_Y = (SCREEN_HEIGHT - (GRID_SIZE * 2 * HOLE_RADIUS + (GRID_SIZE - 1) * HOLE_PADDING)) // 2 + 50

HOLE_CENTERS = []
for r in range(GRID_SIZE):
    row_centers = []
    for c in range(GRID_SIZE):
        x = GRID_START_X + c * (2 * HOLE_RADIUS + HOLE_PADDING) + HOLE_RADIUS
        y = GRID_START_Y + r * (2 * HOLE_RADIUS + HOLE_PADDING) + HOLE_RADIUS
        row_centers.append((x, y))
    HOLE_CENTERS.append(row_centers)


def draw_land():
    screen.fill(COLOR_GRASS_DARK)

    for i in range(0, SCREEN_HEIGHT, 50):
        pygame.draw.rect(screen, COLOR_GRASS_LIGHT, (0, i, SCREEN_WIDTH, 25))


def draw_sky_and_land_menu(screen_height):
    sky_height = screen_height // 2 + 50

    for y in range(sky_height):
        time_ratio = y / sky_height
        color_r = int(COLOR_SKY_TOP[0] + (COLOR_SKY_HORIZON[0] - COLOR_SKY_TOP[0]) * time_ratio)
        color_g = int(COLOR_SKY_TOP[1] + (COLOR_SKY_HORIZON[1] - COLOR_SKY_TOP[1]) * time_ratio)
        color_b = int(COLOR_SKY_TOP[2] + (COLOR_SKY_HORIZON[2] - COLOR_SKY_TOP[2]) * time_ratio)
        pygame.draw.line(screen, (color_r, color_g, color_b), (0, y), (SCREEN_WIDTH, y))

    land_start_y = sky_height
    pygame.draw.rect(screen, COLOR_GRASS_DARK, (0, land_start_y, SCREEN_WIDTH, screen_height - land_start_y))
    for i in range(land_start_y, screen_height, 50):
        pygame.draw.rect(screen, COLOR_GRASS_LIGHT, (0, i, SCREEN_WIDTH, 25))


def draw_hole(center_x, center_y):
    pygame.draw.circle(screen, COLOR_HOLE_EDGE, (center_x, center_y), HOLE_RADIUS + 8)

    pygame.draw.circle(screen, COLOR_HOLE_OPENING, (center_x, center_y), HOLE_RADIUS)

    pygame.draw.arc(screen, (90, 60, 40),
                    (center_x - HOLE_RADIUS - 8, center_y - HOLE_RADIUS - 8,
                     (HOLE_RADIUS + 8) * 2, (HOLE_RADIUS + 8) * 2),
                    3.5, 5.5, 4)


def draw_evil_rat(center_x, center_y):
    rat_radius = HOLE_RADIUS * 0.7

    pygame.draw.circle(screen, COLOR_RAT, (center_x, center_y), rat_radius)

    for side in [-1, 1]:
        ear_x = center_x + side * rat_radius * 0.4
        ear_y = center_y - rat_radius * 0.8
        pygame.draw.circle(screen, COLOR_RAT, (ear_x, ear_y), rat_radius * 0.3)

    eye_offset_y = -rat_radius * 0.3
    eye_size = 5
    pygame.draw.circle(screen, COLOR_RAT_EYES, (center_x - rat_radius * 0.3, center_y + eye_offset_y), eye_size)
    pygame.draw.circle(screen, COLOR_RAT_EYES, (center_x + rat_radius * 0.3, center_y + eye_offset_y), eye_size)

    pygame.draw.line(screen, COLOR_RAT_EYES, (center_x - 10, center_y + 15), (center_x + 10, center_y + 15), 3)


def draw_bomb(center_x, center_y):
    bomb_radius = HOLE_RADIUS * 0.7
    pygame.draw.circle(screen, COLOR_BOMB, (center_x, center_y), bomb_radius)
    pygame.draw.line(screen, (255, 255, 0), (center_x, center_y - bomb_radius),
                     (center_x + 10, center_y - bomb_radius - 15), 3)


def draw_nuke(center_x, center_y):
    nuke_radius = HOLE_RADIUS * 0.7
    pygame.draw.circle(screen, COLOR_NUKE, (center_x, center_y), nuke_radius)
    line_length = nuke_radius * 0.8
    line_color = (0, 200, 0)
    for i in range(3):
        angle = i * (360 / 3)
        rad = pygame.math.Vector2(line_length, 0).rotate(-angle)
        start_pos = (center_x + rad.x * 0.2, center_y + rad.y * 0.2)
        end_pos = (center_x + rad.x, center_y + rad.y)
        pygame.draw.line(screen, line_color, start_pos, end_pos, 4)


def draw_grid():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            draw_hole(HOLE_CENTERS[r][c][0], HOLE_CENTERS[r][c][1])


def draw_button(text, rect, color, hover_color, font):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)

    shadow_offset = 5
    shadow_color = (color[0] * 0.6, color[1] * 0.6, color[2] * 0.6)

    current_offset = 2 if is_hovered else shadow_offset
    current_color = hover_color if is_hovered else color

    base_rect = rect.move(0, shadow_offset)
    pygame.draw.rect(screen, shadow_color, base_rect, border_radius=15)

    button_surface_rect = rect.move(0, current_offset - shadow_offset)
    pygame.draw.rect(screen, current_color, button_surface_rect, border_radius=15)

    text_surface = font.render(text, True, COLOR_WHITE)
    text_rect = text_surface.get_rect(center=button_surface_rect.center)
    screen.blit(text_surface, text_rect)

    return rect


def draw_hammer(x, y):
    pygame.draw.line(screen, (139, 69, 19), (x, y), (x + 45, y + 45), 6)

    pygame.draw.rect(screen, (100, 100, 100), (x - 25, y - 5, 30, 15), border_radius=3)

    pygame.draw.polygon(screen, COLOR_BLACK, [
        (x - 25, y - 5),
        (x - 30, y - 10),
        (x - 30, y)
    ])


def draw_smash_effect(current_time):
    global last_smash

    if last_smash:
        smash_x, smash_y, smash_time = last_smash

        if current_time - smash_time < SMASH_DURATION:
            time_ratio = (current_time - smash_time) / SMASH_DURATION

            alpha = int(255 * (1 - time_ratio))
            radius = 10 + time_ratio * 40

            s = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)

            impact_color = COLOR_SMASH_DUST + (alpha,)
            pygame.draw.circle(s, impact_color, (int(radius), int(radius)), int(radius))

            screen.blit(s, (int(smash_x - radius), int(smash_y - radius)))

            line_alpha = int(255 * (1 - time_ratio * 2))

            if line_alpha > 0:
                line_color = COLOR_WHITE + (line_alpha,)

                pygame.draw.line(screen, line_color, (smash_x - 10, smash_y - 10), (smash_x + 10, smash_y + 10), 2)
                pygame.draw.line(screen, line_color, (smash_x + 10, smash_y - 10), (smash_x - 10, smash_y + 10), 2)
        else:
            last_smash = None


def spawn_object():
    global active_object, last_spawn_time
    roll = random.randint(1, 10)
    if roll <= 7:
        obj_type = 0
    elif roll <= 9:
        obj_type = 1
    else:
        obj_type = 2

    r = random.randint(0, GRID_SIZE - 1)
    c = random.randint(0, GRID_SIZE - 1)

    active_object = (r, c, obj_type, time.time())
    last_spawn_time = time.time()


def update_difficulty():
    global base_time_visible, spawn_interval

    difficulty_level = score // 4

    base_time_visible = max(0.3, 2.0 - difficulty_level * 0.15)
    spawn_interval = max(0.4, 1.5 - difficulty_level * 0.1)

    if base_time_visible < spawn_interval:
        base_time_visible = spawn_interval * 1.1


def check_click(pos):
    global active_object, score, bomb_strikes, nuke_strikes, misses, game_state

    clicked_hole = None
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            center_x, center_y = HOLE_CENTERS[r][c]
            if (pos[0] - center_x) ** 2 + (pos[1] - center_y) ** 2 < HOLE_RADIUS ** 2:
                clicked_hole = (r, c)
                break
        if clicked_hole:
            break

    if active_object and clicked_hole and (active_object[0], active_object[1]) == clicked_hole:
        obj_type = active_object[2]
        if obj_type == 0:
            score += RAT_SCORE_VALUE
        elif obj_type == 1:
            bomb_strikes += 1
            score += BOMB_SCORE_VALUE
        elif obj_type == 2:
            nuke_strikes += 1

        active_object = None
        check_game_over()


def check_game_over():
    global game_state

    if misses >= MAX_MISSES:
        game_state = "GAME_OVER_MISS"
    elif bomb_strikes >= MAX_BOMB_STRIKES:
        game_state = "GAME_OVER_BOMB"
    elif nuke_strikes >= MAX_NUKE_STRIKES:
        game_state = "GAME_OVER_NUKE"


def reset_game():
    global score, misses, bomb_strikes, nuke_strikes, active_object, base_time_visible, spawn_interval, last_smash
    score = 0
    misses = 0
    bomb_strikes = 0
    nuke_strikes = 0
    active_object = None
    last_smash = None
    base_time_visible = 2.0
    spawn_interval = 1.5
    global game_state
    game_state = "GAME"


def draw_score_and_strikes():
    score_text = FONT_M.render(f"Score: {score}", True, COLOR_TEXT)
    screen.blit(score_text, (20, 20))

    miss_text = FONT_M.render(f"Misses: {misses}/{MAX_MISSES}", True, COLOR_TEXT)
    screen.blit(miss_text, (20, 60))

    bomb_text = FONT_M.render(f"Bomb Strikes: {bomb_strikes}/{MAX_BOMB_STRIKES}", True, COLOR_TEXT)
    screen.blit(bomb_text, (SCREEN_WIDTH - bomb_text.get_width() - 20, 20))

    nuke_text = FONT_M.render(f"Nuke Strikes: {nuke_strikes}/{MAX_NUKE_STRIKES}", True, COLOR_TEXT)
    screen.blit(nuke_text, (SCREEN_WIDTH - nuke_text.get_width() - 20, 60))


def menu_screen():
    button_width = 250
    button_height = 60

    start_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2, button_width, button_height)
    exit_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2 + button_height + 20, button_width,
                            button_height)

    while game_state == "MENU":
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    reset_game()
                    return "GAME"
                if exit_rect.collidepoint(event.pos):
                    return "EXIT"

        draw_sky_and_land_menu(SCREEN_HEIGHT)

        title_text = FONT_L.render(TITLE, True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 30))

        for dx, dy in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            shadow_rect = title_rect.move(dx, dy)
            shadow_surface = FONT_L.render(TITLE, True, COLOR_TITLE_OUTLINE)
            screen.blit(shadow_surface, shadow_rect)

        screen.blit(title_text, title_rect)

        subtitle_text = FONT_M.render("Grab your hammer and squash that evil rat!", True, COLOR_TEXT)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 30))
        screen.blit(subtitle_text, subtitle_rect)

        draw_button("START GAME", start_rect, COLOR_BUTTON, COLOR_BUTTON_HOVER, FONT_M)
        draw_button("EXIT", exit_rect, COLOR_RESTART, COLOR_BUTTON_HOVER, FONT_M)

        draw_hammer(mouse_pos[0], mouse_pos[1])

        pygame.display.flip()
        clock.tick(30)
    return "MENU"


def game_loop():
    global active_object, misses, game_state, last_spawn_time, last_smash

    running = True

    restart_rect = pygame.Rect(10, SCREEN_HEIGHT - 50, 100, 40)
    exit_game_rect = pygame.Rect(10 + 100 + 10, SCREEN_HEIGHT - 50, 100, 40)

    while running and game_state == "GAME":

        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"

            if event.type == pygame.MOUSEBUTTONDOWN:
                last_smash = (event.pos[0], event.pos[1], current_time)

                check_click(event.pos)

                if restart_rect.collidepoint(event.pos):
                    reset_game()
                    return "GAME"

                if exit_game_rect.collidepoint(event.pos):
                    return "EXIT"

        if active_object and current_time - active_object[3] > base_time_visible:
            obj_type = active_object[2]

            if obj_type == 0:
                misses += 1

            active_object = None
            check_game_over()

        if not active_object and current_time - last_spawn_time > spawn_interval:
            spawn_object()

        update_difficulty()

        draw_land()
        draw_grid()

        if active_object:
            r, c, obj_type, spawn_time = active_object
            center_x, center_y = HOLE_CENTERS[r][c]
            time_passed = current_time - spawn_time

            scale_factor = min(1.0, 0.5 + 0.5 * (time_passed / base_time_visible))

            surfacing_offset = int(HOLE_RADIUS * (1 - scale_factor) * 0.5)

            if obj_type == 0:
                draw_evil_rat(center_x, center_y + surfacing_offset)
            elif obj_type == 1:
                draw_bomb(center_x, center_y + surfacing_offset)
            elif obj_type == 2:
                draw_nuke(center_x, center_y + surfacing_offset)

        draw_score_and_strikes()

        draw_button("Restart", restart_rect, COLOR_RESTART, COLOR_BUTTON_HOVER, FONT_S)
        draw_button("Exit", exit_game_rect, COLOR_BUTTON, COLOR_BUTTON_HOVER, FONT_S)

        draw_smash_effect(current_time)
        draw_hammer(mouse_pos[0], mouse_pos[1])

        pygame.display.flip()
        clock.tick(60)

    return "GAME_OVER"


def game_over_screen(fail_type):
    global game_state

    if fail_type == "NUKE":
        message = "GAME OVER: NUCLEAR MISSILE DETONATED!"
        subtitle = "You struck the Nuke! The world is gone. Final Score: "
        message_color = COLOR_WHITE
        fill_color = COLOR_NUKE_EXPLOSION
    elif fail_type == "BOMB":
        message = "GAME OVER: Too many Bomb Strikes!"
        subtitle = "Avoid the explosives! Final Score: "
        message_color = COLOR_WHITE
        fill_color = COLOR_BOMB
    elif fail_type == "MISS":
        message = "GAME OVER: Too many Misses!"
        subtitle = "You were too slow hitting the Rats! Final Score: "
        message_color = COLOR_WHITE
        fill_color = COLOR_HOLE_EDGE
    else:
        message = "GAME OVER"
        subtitle = "Final Score: "
        message_color = COLOR_WHITE
        fill_color = COLOR_BLACK

    button_width = 200
    button_height = 50
    restart_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2, button_width, button_height)
    exit_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, SCREEN_HEIGHT // 2 + button_height + 20, button_width,
                            button_height)

    while game_state.startswith("GAME_OVER"):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    reset_game()
                    return "GAME"
                if exit_rect.collidepoint(event.pos):
                    return "EXIT"

        screen.fill(fill_color)

        msg_text = FONT_L.render(message, True, message_color)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(msg_text, msg_rect)

        score_text = FONT_M.render(f"{subtitle} {score}", True, message_color)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))
        screen.blit(score_text, score_rect)

        draw_button("PLAY AGAIN", restart_rect, COLOR_RESTART, COLOR_BUTTON_HOVER, FONT_M)
        draw_button("EXIT", exit_rect, COLOR_BUTTON, COLOR_BUTTON_HOVER, FONT_M)

        draw_hammer(mouse_pos[0], mouse_pos[1])

        pygame.display.flip()
        clock.tick(30)
    return "MENU"


def main():
    global game_state

    current_state = "MENU"
    next_state = "MENU"

    running = True
    while running:
        if current_state == "MENU":
            next_state = menu_screen()
        elif current_state == "GAME":
            next_state = game_loop()
        elif current_state.startswith("GAME_OVER"):
            fail_type = current_state.split('_')[-1]
            next_state = game_over_screen(fail_type)
        elif current_state == "EXIT":
            running = False

        current_state = next_state

    pygame.quit()


if __name__ == "__main__":
    main()