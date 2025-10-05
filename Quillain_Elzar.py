import pygame
import sys
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 13, 15
TILE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman Clone with Enemies & Loot")

clock = pygame.time.Clock()

# Map elements
EMPTY = 0
WALL = 1
DESTRUCTIBLE = 2
BOMB = 3
EXPLOSION = 4
LOOT = 5

# Directions for movement
DIRECTIONS = [(1,0), (-1,0), (0,1), (0,-1)]

# Create map grid with borders as walls, some destructible blocks
def create_map():
    grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    for r in range(ROWS):
        for c in range(COLS):
            if r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
                grid[r][c] = WALL
            elif r % 2 == 0 and c % 2 == 0:
                grid[r][c] = WALL
            elif (r + c) % 3 == 0:
                grid[r][c] = DESTRUCTIBLE

    # Clear starting player position
    grid[1][1] = EMPTY
    grid[1][2] = EMPTY
    grid[2][1] = EMPTY

    return grid

grid = create_map()

# Loot dict: (r,c) -> loot type ('bomb_up' here)
loot_positions = {}

# Place loot randomly in destructible boxes at game start
def place_loot():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == DESTRUCTIBLE:
                # 30% chance box has loot
                if random.random() < 0.3:
                    loot_positions[(r,c)] = 'bomb_up'

place_loot()

# Player starting position
player_r, player_c = 1, 1
bomb_power = 1  # Explosion length

# Bombs: dict with 'pos':(r,c), 'timer', 'exploded', 'power'
bombs = []

EXPLOSION_DURATION = 30
MOVE_COOLDOWN = 150
last_move_time = 0

# Enemies: each enemy is dict with 'pos':(r,c), 'move_timer'
enemy_move_interval = 1000  # ms
enemies = [{'pos': (ROWS-2, COLS-2), 'move_timer': 0}]

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if grid[r][c] == EMPTY:
                pygame.draw.rect(screen, BLACK, rect)
            elif grid[r][c] == WALL:
                pygame.draw.rect(screen, GRAY, rect)
            elif grid[r][c] == DESTRUCTIBLE:
                pygame.draw.rect(screen, ORANGE, rect)
            elif grid[r][c] == BOMB:
                pygame.draw.rect(screen, RED, rect)
            elif grid[r][c] == EXPLOSION:
                pygame.draw.rect(screen, YELLOW, rect)
            elif grid[r][c] == LOOT:
                pygame.draw.rect(screen, PURPLE, rect)

def draw_player():
    rect = pygame.Rect(player_c * TILE_SIZE + 5, player_r * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
    pygame.draw.rect(screen, BLUE, rect)

def draw_enemies():
    for enemy in enemies:
        er, ec = enemy['pos']
        rect = pygame.Rect(ec * TILE_SIZE + 5, er * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
        pygame.draw.rect(screen, GREEN, rect)

def place_bomb(r, c, power):
    if grid[r][c] == EMPTY:
        grid[r][c] = BOMB
        bombs.append({'pos': (r, c), 'timer': 120, 'exploded': False, 'power': power})

def explode_bomb(bomb):
    r, c = bomb['pos']
    power = bomb['power']

    explosion_coords = [(r, c)]

    # Add coordinates in 4 directions with range = power
    for dr, dc in DIRECTIONS:
        for i in range(1, power+1):
            nr, nc = r + dr*i, c + dc*i
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if grid[nr][nc] == WALL:
                    break  # stop explosion in this direction
                explosion_coords.append((nr, nc))
                if grid[nr][nc] == DESTRUCTIBLE:
                    break  # stop after destructible block

    # Set explosion tiles and destroy destructible blocks + reveal loot
    for er, ec in explosion_coords:
        # Destroy destructible blocks and reveal loot
        if grid[er][ec] == DESTRUCTIBLE:
            grid[er][ec] = EXPLOSION
            # Reveal loot if any
            if (er, ec) in loot_positions:
                grid[er][ec] = LOOT
        elif grid[er][ec] == BOMB:
            # Chain reaction for bombs (explode immediately)
            for b in bombs:
                if b['pos'] == (er, ec) and not b['exploded']:
                    b['timer'] = 0
        else:
            grid[er][ec] = EXPLOSION

def clear_explosions():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == EXPLOSION:
                grid[r][c] = EMPTY

def update_bombs():
    global bombs
    to_remove = []

    for bomb in bombs:
        bomb['timer'] -= 1
        if bomb['timer'] <= 0 and not bomb['exploded']:
            explode_bomb(bomb)
            bomb['exploded'] = True
            bomb['timer'] = EXPLOSION_DURATION
        elif bomb['exploded'] and bomb['timer'] <= 0:
            r, c = bomb['pos']
            if grid[r][c] == BOMB or grid[r][c] == EXPLOSION:
                grid[r][c] = EMPTY
            clear_explosions()
            to_remove.append(bomb)

    bombs = [b for b in bombs if b not in to_remove]

def can_move(r, c):
    if 0 <= r < ROWS and 0 <= c < COLS:
        return grid[r][c] in (EMPTY, LOOT)
    return False

def check_player_dead():
    if grid[player_r][player_c] == EXPLOSION:
        return True
    for enemy in enemies:
        if enemy['pos'] == (player_r, player_c):
            return True
    return False

def move_enemies():
    current_time = pygame.time.get_ticks()
    for enemy in enemies:
        if current_time - enemy['move_timer'] > enemy_move_interval:
            er, ec = enemy['pos']
            random.shuffle(DIRECTIONS)
            moved = False
            for dr, dc in DIRECTIONS:
                nr, nc = er + dr, ec + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if grid[nr][nc] in (EMPTY, LOOT):
                        # Prevent enemy from moving onto player tile directly for fairness
                        if (nr, nc) != (player_r, player_c):
                            enemy['pos'] = (nr, nc)
                            moved = True
                            break
            enemy['move_timer'] = current_time
            if not moved:
                enemy['move_timer'] = current_time  # still update timer to avoid freeze

def pick_loot():
    global bomb_power
    if (player_r, player_c) in loot_positions:
        loot = loot_positions.pop((player_r, player_c))
        if loot == 'bomb_up':
            bomb_power += 1
            print(f"Bomb power increased to {bomb_power}")
        grid[player_r][player_c] = EMPTY  # remove loot tile

def main():
    global player_r, player_c, last_move_time

    running = True
    font_gameover = pygame.font.SysFont(None, 64)
    font_info = pygame.font.SysFont(None, 28)

    while running:
        dt = clock.tick(60)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    place_bomb(player_r, player_c, bomb_power)

        keys = pygame.key.get_pressed()
        if current_time - last_move_time > MOVE_COOLDOWN:
            if keys[pygame.K_UP] and can_move(player_r - 1, player_c):
                player_r -= 1
                last_move_time = current_time
            elif keys[pygame.K_DOWN] and can_move(player_r + 1, player_c):
                player_r += 1
                last_move_time = current_time
            elif keys[pygame.K_LEFT] and can_move(player_r, player_c - 1):
                player_c -= 1
                last_move_time = current_time
            elif keys[pygame.K_RIGHT] and can_move(player_r, player_c + 1):
                player_c += 1
                last_move_time = current_time

        update_bombs()
        move_enemies()
        pick_loot()

        screen.fill(BLACK)
        draw_grid()
        draw_player()
        draw_enemies()

        # Display bomb power
        info_text = font_info.render(f"Bomb Power: {bomb_power}", True, WHITE)
        screen.blit(info_text, (10, HEIGHT - 30))

        if check_player_dead():
            text = font_gameover.render("Game Over!", True, RED)
            rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False
            continue

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
