# number_puzzle.py
import pygame, sys, random, time # type: ignore
from copy import deepcopy

pygame.init()
pygame.display.set_caption("Number Puzzle — 9×9")

# ---------- Config ----------
WIDTH, HEIGHT = 820, 920
FPS = 60

PANEL_LEFT = 40
PANEL_TOP = 120
GRID_SIZE = 720  # square grid
CELL = GRID_SIZE // 9

# Colors
BG = (244, 246, 250)
PANEL = (255, 255, 255)
LINE = (60, 67, 80)
SUBLINE = (120, 130, 145)
HIGHLIGHT = (220, 241, 255)
FIXED_COLOR = (30, 33, 40)
USER_COLOR = (18, 100, 177)
ERROR_COLOR = (200, 70, 70)
PENCIL_COLOR = (90, 95, 105)
BUTTON_BG = (235, 238, 245)
BUTTON_BORDER = (200, 205, 215)

# Fonts
F_SMALL = pygame.font.SysFont("freesansbold", 14)
F_MED = pygame.font.SysFont("freesansbold", 22)
F_LRG = pygame.font.SysFont("freesansbold", 40)
F_BIG = pygame.font.SysFont("freesansbold", 56)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ---------- Sudoku logic ----------
def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def valid(board, num, pos):
    r, c = pos
    # row
    for j in range(9):
        if j != c and board[r][j] == num:
            return False
    # col
    for i in range(9):
        if i != r and board[i][c] == num:
            return False
    # box
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if (i,j) != (r,c) and board[i][j] == num:
                return False
    return True

def solve_backtrack(board):
    em = find_empty(board)
    if not em:
        return True
    r,c = em
    for n in range(1,10):
        if valid(board, n, (r,c)):
            board[r][c] = n
            if solve_backtrack(board):
                return True
            board[r][c] = 0
    return False

def generate_full():
    board = [[0]*9 for _ in range(9)]
    def fill():
        em = find_empty(board)
        if not em:
            return True
        r,c = em
        nums = list(range(1,10))
        random.shuffle(nums)
        for n in nums:
            if valid(board, n, (r,c)):
                board[r][c] = n
                if fill(): return True
                board[r][c] = 0
        return False
    fill()
    return board

def make_puzzle(full, removals=45):
    puzzle = deepcopy(full)
    coords = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for (r,c) in coords:
        if removed >= removals:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        # skip uniqueness test for speed
        removed += 1
    return puzzle

# ---------- UI classes ----------
class Cell:
    def __init__(self, r, c, v=0, fixed=False):
        self.r = r; self.c = c
        self.value = v
        self.fixed = fixed
        self.pencils = set()

class Board:
    def __init__(self, puzzle):
        self.cells = [[None]*9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                v = puzzle[r][c]
                self.cells[r][c] = Cell(r,c,v, fixed=(v!=0))
        self.solution = None

    def values(self):
        return [[self.cells[r][c].value for c in range(9)] for r in range(9)]

    def set_solution(self, sol):
        self.solution = sol

    def place(self, r,c,num):
        cell = self.cells[r][c]
        if cell.fixed: return False, "Fixed"
        if num==0:
            cell.value = 0
            cell.pencils.clear()
            return True, ""
        # check validity vs current board
        b = self.values()
        if not valid(b, num, (r,c)):
            return False, "Invalid"
        cell.value = num
        cell.pencils.clear()
        return True, ""

    def toggle_pencil(self, r,c,num):
        cell=self.cells[r][c]
        if cell.fixed or cell.value!=0: return
        if num in cell.pencils: cell.pencils.remove(num)
        else: cell.pencils.add(num)

    def is_solved(self):
        for r in range(9):
            for c in range(9):
                v = self.cells[r][c].value
                if v==0 or not valid(self.values(), v, (r,c)): return False
        return True

class Button:
    def __init__(self, x,y,w,h,text):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
    def draw(self, surf):
        pygame.draw.rect(surf, BUTTON_BG, self.rect, border_radius=10)
        pygame.draw.rect(surf, BUTTON_BORDER, self.rect, 2, border_radius=10)
        txt = F_MED.render(self.text, True, (20,20,20))
        surf.blit(txt, txt.get_rect(center=self.rect.center))
    def clicked(self,pos): return self.rect.collidepoint(pos)

# ---------- Game helpers ----------
def new_game(difficulty="medium"):
    full = generate_full()
    if difficulty=="easy": removals=36
    elif difficulty=="hard": removals=52
    else: removals=45
    puzzle = make_puzzle(full, removals)
    b = Board(puzzle)
    b.set_solution(full)
    return b

def draw_header():
    t = F_BIG.render("Number Puzzle", True, (20,20,30))
    screen.blit(t, (PANEL_LEFT, 24))
    sub = F_MED.render("Click cell, type 1-9. N toggles Pencil. Arrow keys to move.", True, (80,80,90))
    screen.blit(sub, (PANEL_LEFT, 84))

def draw_grid(board, selected, pencil_mode, mistakes):
    # background panel
    panel = pygame.Rect(PANEL_LEFT-8, PANEL_TOP-8, GRID_SIZE+16, GRID_SIZE+16)
    pygame.draw.rect(screen, PANEL, panel, border_radius=14)
    # highlights
    if selected:
        sr,sc = selected
        # row
        pygame.draw.rect(screen, (248,255,255), (PANEL_LEFT, PANEL_TOP + sr*CELL, GRID_SIZE, CELL))
        # column
        pygame.draw.rect(screen, (248,255,255), (PANEL_LEFT + sc*CELL, PANEL_TOP, CELL, GRID_SIZE))
        # cell
        pygame.draw.rect(screen, HIGHLIGHT, (PANEL_LEFT + sc*CELL, PANEL_TOP + sr*CELL, CELL, CELL))
    # grid lines
    for i in range(10):
        w = 4 if i%3==0 else 1
        # vertical
        x = PANEL_LEFT + i*CELL
        pygame.draw.line(screen, LINE, (x, PANEL_TOP), (x, PANEL_TOP+GRID_SIZE), w)
        # horizontal
        y = PANEL_TOP + i*CELL
        pygame.draw.line(screen, LINE, (PANEL_LEFT, y), (PANEL_LEFT+GRID_SIZE, y), w)

    # numbers & pencils
    for r in range(9):
        for c in range(9):
            cell = board.cells[r][c]
            x = PANEL_LEFT + c*CELL
            y = PANEL_TOP + r*CELL
            if cell.value!=0:
                col = FIXED_COLOR if cell.fixed else USER_COLOR
                txt = F_LRG.render(str(cell.value), True, col)
                screen.blit(txt, txt.get_rect(center=(x+CELL/2, y+CELL/2)))
                # incorrect highlight vs solution
                if board.solution and cell.value != board.solution[r][c]:
                    pygame.draw.rect(screen, (255, 220, 220), (x+2, y+2, CELL-4, CELL-4), 3)
            else:
                # draw pencil marks (3x3 grid)
                if cell.pencils:
                    for p in list(cell.pencils):
                        pr = (p-1)//3; pc = (p-1)%3
                        px = x + (pc * CELL/3) + CELL/6
                        py = y + (pr * CELL/3) + CELL/6
                        ptxt = F_SMALL.render(str(p), True, PENCIL_COLOR)
                        screen.blit(ptxt, ptxt.get_rect(center=(px,py)))

    # footer: mistakes & pencil
    mtxt = F_MED.render(f"Mistakes: {mistakes}", True, ERROR_COLOR if mistakes>0 else (60,60,70))
    screen.blit(mtxt, (PANEL_LEFT, PANEL_TOP+GRID_SIZE+14))
    ptxt = F_MED.render("Pencil: ON" if pencil_mode else "Pencil: OFF", True, (60,60,70))
    screen.blit(ptxt, (PANEL_LEFT+240, PANEL_TOP+GRID_SIZE+14))

def draw_side_panel(start_time):
    # right-side stats & buttons
    pygame.draw.rect(screen, (250,250,250), (PANEL_LEFT+GRID_SIZE+20, PANEL_TOP-10, 220, 380), border_radius=12)
    # Timer
    elapsed = int(time.time() - start_time)
    timer = F_MED.render(f"Time: {elapsed//60:02d}:{elapsed%60:02d}", True, (50,50,60))
    screen.blit(timer, (PANEL_LEFT+GRID_SIZE+40, PANEL_TOP+20))
    # Buttons
    b_x = PANEL_LEFT+GRID_SIZE+40
    b_y = PANEL_TOP+80
    for b in buttons:
        b.draw(screen)
    # instructions small
    s = F_SMALL.render("N: Pencil  |  S: Solve  |  Backspace: Clear", True, (90,90,100))
    screen.blit(s, (PANEL_LEFT+GRID_SIZE+38, PANEL_TOP+320))

# ---------- Initialize ----------
board = new_game("medium")
start_time = time.time()
selected = (0,0)
pencil_mode = False
mistakes = 0
history = []  # store (r,c,old_value,old_pencils) for undo

# Buttons (placed on side)
buttons = [
    Button(PANEL_LEFT+GRID_SIZE+40, PANEL_TOP+110, 140, 44, "New Puzzle"),
    Button(PANEL_LEFT+GRID_SIZE+40, PANEL_TOP+170, 140, 44, "Solve"),
    Button(PANEL_LEFT+GRID_SIZE+40, PANEL_TOP+230, 140, 44, "Check"),
    Button(PANEL_LEFT+GRID_SIZE+40, PANEL_TOP+290, 140, 44, "Undo"),
]

# ---------- Main loop ----------
def main():
    global board, start_time, selected, pencil_mode, mistakes, history
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                # grid click?
                gx, gy = PANEL_LEFT, PANEL_TOP
                if gx <= mx <= gx+GRID_SIZE and gy <= my <= gy+GRID_SIZE:
                    col = (mx-gx)//CELL
                    row = (my-gy)//CELL
                    selected = (int(row), int(col))
                else:
                    # check buttons
                    for b in buttons:
                        if b.clicked((mx,my)):
                            if b.text=="New Puzzle":
                                board = new_game("medium")
                                start_time = time.time()
                                mistakes = 0
                                history=[]
                                selected = (0,0)
                            elif b.text=="Solve":
                                if board.solution:
                                    for r in range(9):
                                        for c in range(9):
                                            board.cells[r][c].value = board.solution[r][c]
                                            board.cells[r][c].pencils.clear()
                            elif b.text=="Check":
                                # mark mistakes by counting mismatches to solution
                                if board.solution:
                                    wrong = 0
                                    for r in range(9):
                                        for c in range(9):
                                            val = board.cells[r][c].value
                                            if val!=0 and val != board.solution[r][c]:
                                                wrong += 1
                                    mistakes += wrong
                            elif b.text=="Undo":
                                if history:
                                    r,c,old_val,old_pencils = history.pop()
                                    board.cells[r][c].value = old_val
                                    board.cells[r][c].pencils = old_pencils
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    pencil_mode = not pencil_mode
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    r,c = selected
                    if event.key==pygame.K_UP: r = (r-1)%9
                    if event.key==pygame.K_DOWN: r = (r+1)%9
                    if event.key==pygame.K_LEFT: c = (c-1)%9
                    if event.key==pygame.K_RIGHT: c = (c+1)%9
                    selected = (r,c)
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    r,c = selected
                    cell = board.cells[r][c]
                    if not cell.fixed:
                        # save history
                        history.append((r,c, cell.value, set(cell.pencils)))
                        board.place(r,c,0)
                elif event.key == pygame.K_s:
                    # solve
                    if board.solution:
                        for r in range(9):
                            for c in range(9):
                                board.cells[r][c].value = board.solution[r][c]
                                board.cells[r][c].pencils.clear()
                elif event.unicode and event.unicode.isdigit():
                    ch = event.unicode
                    if ch != '0':
                        num = int(ch)
                        r,c = selected
                        cell = board.cells[r][c]
                        if cell.fixed: 
                            pass
                        else:
                            # record history
                            history.append((r,c, cell.value, set(cell.pencils)))
                            if pencil_mode:
                                board.toggle_pencil(r,c,num)
                            else:
                                ok,msg = board.place(r,c,num)
                                if not ok:
                                    mistakes += 1

        # draw everything
        screen.fill(BG)
        draw_header()
        draw_grid(board, selected, pencil_mode, mistakes)
        # draw side panel (buttons & timer)
        for b in buttons:
            b.draw(screen)
        elapsed = int(time.time() - start_time)
        timer_txt = F_MED.render(f"Time: {elapsed//60:02d}:{elapsed%60:02d}", True, (40,40,40))
        screen.blit(timer_txt, (PANEL_LEFT+GRID_SIZE+48, PANEL_TOP+30))

        # success message
        if board.is_solved():
            msg = F_BIG.render("Solved! 🎉", True, (20,140,60))
            screen.blit(msg, (PANEL_LEFT+GRID_SIZE//2 - msg.get_width()//2, PANEL_TOP + GRID_SIZE + 36))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=='__main__':
    main()
