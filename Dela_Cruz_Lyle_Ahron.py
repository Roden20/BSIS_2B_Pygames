import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 540, 600  
ROWS, COLS = 9, 9
CELL_SIZE = WIDTH // COLS
FPS = 60

BG_COLOR = (30, 30, 40)
GRID_COLOR = (50, 50, 70)
TEXT_COLOR = (230, 230, 230)
HIGHLIGHT_COLOR = (255, 255, 255)

CELL_COLORS = [
    (255, 99, 71),   
    (60, 179, 113),  
    (65, 105, 225),   
    (238, 130, 238), 
    (255, 215, 0),    
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Connect - 9x9 Grid")

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36, bold=True)

clock = pygame.time.Clock()

grid = [[random.choice(CELL_COLORS) for _ in range(COLS)] for _ in range(ROWS)]

selected_cells = []
selected_color = None
score = 0
animating = False
animation_timer = 0
animation_duration = 300  

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            color = grid[r][c]
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if color:
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (20, 20, 20), rect, 2)
            else:
                pygame.draw.rect(screen, BG_COLOR, rect)
            if (r, c) in selected_cells:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 4)

    for i in range(ROWS + 1):
        pygame.draw.line(screen, GRID_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
    for j in range(COLS + 1):
        pygame.draw.line(screen, GRID_COLOR, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT - 60), 2)

def get_cell_at_pos(pos):
    x, y = pos
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT - 60:
        return None
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return (row, col)

def are_adjacent(cell1, cell2):
    r1, c1 = cell1
    r2, c2 = cell2
    return abs(r1 - r2) + abs(c1 - c2) == 1

def remove_cells(cells):
    global score
    for r, c in cells:
        grid[r][c] = None
    score += len(cells) * 10

def drop_cells():
    for c in range(COLS):
        col_cells = [grid[r][c] for r in range(ROWS)]
        filtered = [color for color in col_cells if color is not None]
        empties = ROWS - len(filtered)
        new_cells = [random.choice(CELL_COLORS) for _ in range(empties)]
        new_col = new_cells + filtered
        for r in range(ROWS):
            grid[r][c] = new_col[r]

def draw_score():
    score_surf = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_surf, (10, HEIGHT - 50))

def main():
    global selected_cells, selected_color, animating, animation_timer

    running = True
    mouse_down = False

    while running:
        dt = clock.tick(FPS)
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if animating:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    cell = get_cell_at_pos(pos)
                    if cell and grid[cell[0]][cell[1]] is not None:
                        selected_cells = [cell]
                        selected_color = grid[cell[0]][cell[1]]
                        mouse_down = True

            elif event.type == pygame.MOUSEMOTION and mouse_down:
                pos = pygame.mouse.get_pos()
                cell = get_cell_at_pos(pos)
                if cell and grid[cell[0]][cell[1]] == selected_color:
                    if cell not in selected_cells:
                        if are_adjacent(cell, selected_cells[-1]):
                            selected_cells.append(cell)
                    elif len(selected_cells) > 1 and cell == selected_cells[-2]:
                        selected_cells.pop()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and mouse_down:
                    mouse_down = False
                    if len(selected_cells) >= 3:
                        animating = True
                        animation_timer = 0
                    else:
                        selected_cells = []
                        selected_color = None

        if animating:
            animation_timer += dt
            if animation_timer >= animation_duration:
                remove_cells(selected_cells)
                drop_cells()
                selected_cells = []
                selected_color = None
                animating = False

        draw_grid()
        draw_score()

        instr = font.render("Connect 3+ same colors by dragging mouse", True, TEXT_COLOR)
        screen.blit(instr, (10, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
