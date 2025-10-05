

import pygame
import sys
import math
import random
import time
from collections import namedtuple

pygame.init()

# Window
WIDTH, HEIGHT = 900, 760
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Checkers — Single Player vs AI")
FPS = 60
CLOCK = pygame.time.Clock()

# Board
ROWS, COLS = 8, 8
SQUARE = 74
BOARD_ORIGIN = ((WIDTH - SQUARE * COLS) // 2, 40)

# Colors
LIGHT = (238, 217, 196)
DARK = (129, 94, 60)
WOOD = (100, 60, 30)
BG = (230, 230, 230)
HUD_BG = (245, 245, 245)
HIGHLIGHT = (255, 215, 120)
HIGHLIGHT_MOVE = (120, 200, 255)

RED = (200, 50, 50)
BLACK = (30, 30, 30)

# Fonts
FONT = pygame.font.SysFont(None, 22)
FONT_LG = pygame.font.SysFont(None, 32)
FONT_XL = pygame.font.SysFont(None, 44)

# Piece structure
Piece = namedtuple('Piece', ['color', 'king'])  # color: 'red' or 'black'

# Difficulty modes
DIFFICULTIES = ['Easy', 'Medium', 'Hard']

class CheckersAI:
    def __init__(self, game):
        self.game = game
        self.difficulty_idx = 1  # default Medium

    @property
    def difficulty(self):
        return DIFFICULTIES[self.difficulty_idx]

    def cycle_difficulty(self):
        self.difficulty_idx = (self.difficulty_idx + 1) % len(DIFFICULTIES)

    def choose_move(self):
        color = 'black'
        moves_dict = self.game.all_moves_for(color)
        if not moves_dict:
            return None
        # flatten moves
        all_moves = []
        for fr, moves in moves_dict.items():
            for m in moves:
                tr, tc, caps = m
                all_moves.append((fr, (tr, tc), caps))

        if self.difficulty == 'Easy':
            return random.choice(all_moves)
        elif self.difficulty == 'Medium':
            # prefer capturing moves, prefer more captures
            caps_moves = [m for m in all_moves if m[2]]
            if caps_moves:
                # choose one with max captures, tie-breaker random
                maxk = max(len(m[2]) for m in caps_moves)
                cand = [m for m in caps_moves if len(m[2]) == maxk]
                return random.choice(cand)
            # otherwise random
            return random.choice(all_moves)
        else:  # Hard: minimax with alpha-beta
            depth = 4
            best = None
            best_score = -1e9
            alpha = -1e9
            beta = 1e9
            start = time.time()
            for fr, moves in moves_dict.items():
                for m in moves:
                    tr, tc, caps = m
                    # simulate
                    state = self.game.copy_state()
                    state.execute_move(fr, (tr,tc), caps)
                    score = self.minimax(state, depth-1, False, alpha, beta)
                    if score > best_score:
                        best_score = score
                        best = (fr, (tr,tc), caps)
                    alpha = max(alpha, best_score)
            return best

    def minimax(self, state, depth, maximizing, alpha, beta):
        winner = state.winner()
        if winner == 'black':
            return 1e6
        if winner == 'red':
            return -1e6
        if depth == 0:
            return self.evaluate(state)
        if maximizing:
            max_eval = -1e9
            moves = state.all_moves_for('black')
            if not moves:
                return self.evaluate(state)
            for fr, ms in moves.items():
                for m in ms:
                    tr, tc, caps = m
                    ns = state.copy_state()
                    ns.execute_move(fr, (tr,tc), caps)
                    ev = self.minimax(ns, depth-1, False, alpha, beta)
                    max_eval = max(max_eval, ev)
                    alpha = max(alpha, ev)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = 1e9
            moves = state.all_moves_for('red')
            if not moves:
                return self.evaluate(state)
            for fr, ms in moves.items():
                for m in ms:
                    tr, tc, caps = m
                    ns = state.copy_state()
                    ns.execute_move(fr, (tr,tc), caps)
                    ev = self.minimax(ns, depth-1, True, alpha, beta)
                    min_eval = min(min_eval, ev)
                    beta = min(beta, ev)
                    if beta <= alpha:
                        break
            return min_eval

    def evaluate(self, state):
        # simple heuristic: piece count + king weight + mobility
        red_score = 0
        black_score = 0
        for r in range(ROWS):
            for c in range(COLS):
                p = state.get_piece(r, c)
                if p:
                    val = 3 if p.king else 1
                    if p.color == 'red':
                        red_score += val
                    else:
                        black_score += val
        # mobility
        red_moves = sum(len(ms) for ms in state.all_moves_for('red').values())
        black_moves = sum(len(ms) for ms in state.all_moves_for('black').values())
        score = (black_score - red_score) * 100 + (black_moves - red_moves)
        return score

class Checkers:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = 'red'
        self.selected = None
        self.valid_moves = {}
        self.captured_counts = {'red':0, 'black':0}
        self.generate_board()
        self.message = "Red to move"

    def generate_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                if (r + c) % 2 == 1:
                    if r < 3:
                        self.board[r][c] = Piece('black', False)
                    elif r > 4:
                        self.board[r][c] = Piece('red', False)
                    else:
                        self.board[r][c] = None
                else:
                    self.board[r][c] = None

    def inside(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def get_piece(self, r, c):
        return self.board[r][c]

    def set_piece(self, r, c, piece):
        self.board[r][c] = piece

    def remove_piece(self, r, c):
        self.board[r][c] = None

    def copy_state(self):
        # shallow copy that is safe for minimax simulation
        ns = Checkers()
        ns.board = [row[:] for row in self.board]
        ns.turn = self.turn
        ns.selected = None
        ns.valid_moves = {}
        ns.captured_counts = dict(self.captured_counts)
        ns.message = self.message
        return ns

    def execute_move(self, from_rc, to_rc, captures):
        fr, fc = from_rc
        tr, tc = to_rc
        piece = self.get_piece(fr, fc)
        self.set_piece(tr, tc, piece)
        self.remove_piece(fr, fc)
        if captures:
            for (cr, cc) in captures:
                self.remove_piece(cr, cc)
                if piece:
                    # increment capture count for mover
                    self.captured_counts[piece.color] += 1
        # kinging
        if piece and not piece.king:
            if piece.color == 'red' and tr == 0:
                self.set_piece(tr, tc, Piece(piece.color, True))
            elif piece.color == 'black' and tr == ROWS-1:
                self.set_piece(tr, tc, Piece(piece.color, True))
        # switch turn or allow multi-capture
        moved_piece = self.get_piece(tr, tc)
        further_caps = []
        if captures:
            temp = self._moves_for_piece(tr, tc, moved_piece)
            further_caps = [m for m in temp if m[2]]
        if captures and further_caps:
            # same player must continue (in simulation we don't alternate)
            # to emulate continuation, we simply allow next call to operate from same state
            pass
        else:
            self.turn = 'black' if self.turn == 'red' else 'red'

    def all_moves_for(self, color):
        moves = {}
        captures_exist = False
        for r in range(ROWS):
            for c in range(COLS):
                p = self.get_piece(r,c)
                if p and p.color == color:
                    ms = self._moves_for_piece(r,c, p)
                    if ms:
                        moves[(r,c)] = ms
                        for m in ms:
                            if m[2]:
                                captures_exist = True
        if captures_exist:
            cap_moves = {}
            for k, v in moves.items():
                caps = [m for m in v if m[2]]
                if caps:
                    cap_moves[k] = caps
            return cap_moves
        return moves

    def _moves_for_piece(self, r, c, piece):
        # Note: Normal non-king pieces move forward only, but **can capture backward**.
        # Directions for simple moves: forward only for non-king
        moves = []
        capture_moves = []

        forward_dirs = []
        if piece.color == 'red' or piece.king:
            forward_dirs.append((-1, -1))
            forward_dirs.append((-1, 1))
        if piece.color == 'black' or piece.king:
            forward_dirs.append((1, -1))
            forward_dirs.append((1, 1))

        # For capturing, allow all four diagonal directions (backward captures allowed)
        capture_dirs = [(-1,-1), (-1,1), (1,-1), (1,1)]

        # check captures first
        for dr, dc in capture_dirs:
            nr, nc = r + dr, c + dc
            jr, jc = r + 2*dr, c + 2*dc
            if self.inside(jr, jc) and self.inside(nr, nc):
                target = self.get_piece(nr, nc)
                landing = self.get_piece(jr, jc)
                if target and target.color != piece.color and landing is None:
                    # found capture; now explore chains
                    chains = self._chain_captures(r, c, r, c, piece, [], set())
                    return chains  # chains include the first capture outcomes

        # if no captures, check simple forward moves
        for dr, dc in forward_dirs:
            nr, nc = r + dr, c + dc
            if self.inside(nr, nc) and self.get_piece(nr, nc) is None:
                moves.append((nr, nc, []))
        return moves

    def _chain_captures(self, orr, occ, r, c, piece, caps_so_far, captured_set):
        # Recursive chain-capture finder. Returns list of (tr,tc, captures_list)
        results = []
        found_extension = False
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            nr, nc = r + dr, c + dc
            jr, jc = r + 2*dr, c + 2*dc
            if not self.inside(jr, jc) or not self.inside(nr, nc):
                continue
            if (nr,nc) in captured_set:
                continue
            target = self.get_piece(nr, nc)
            landing = self.get_piece(jr, jc)
            # consider pieces already captured in this chain as removed
            if target and target.color != piece.color and landing is None:
                # simulate capture by marking (nr,nc) as captured in this path
                new_caps = list(caps_so_far) + [(nr, nc)]
                new_captured = set(captured_set)
                new_captured.add((nr,nc))
                # temporarily remove captured piece for deeper search
                saved = self.board[nr][nc]
                self.board[nr][nc] = None
                deeper = self._chain_captures(orr, occ, jr, jc, piece, new_caps, new_captured)
                # restore
                self.board[nr][nc] = saved
                if deeper:
                    for d in deeper:
                        results.append(d)
                else:
                    results.append((jr, jc, new_caps))
                found_extension = True
        if not found_extension:
            # no further captures from current pos; return empty to indicate none
            return []
        return results

    def select(self, r, c):
        p = self.get_piece(r, c)
        if p and p.color == self.turn:
            self.selected = (r, c)
            self.valid_moves = self.all_moves_for(self.turn)
            return True
        return False

    def get_selected_moves(self):
        if self.selected and self.selected in self.valid_moves:
            return self.valid_moves[self.selected]
        return []

    def move(self, from_rc, to_rc, captures):
        fr, fc = from_rc
        tr, tc = to_rc
        piece = self.get_piece(fr, fc)
        self.set_piece(tr, tc, piece)
        self.remove_piece(fr, fc)
        if captures:
            for (cr, cc) in captures:
                self.remove_piece(cr, cc)
                if piece:
                    self.captured_counts[piece.color] += 1
        # kinging
        if piece and not piece.king:
            if piece.color == 'red' and tr == 0:
                self.set_piece(tr, tc, Piece(piece.color, True))
            elif piece.color == 'black' and tr == ROWS-1:
                self.set_piece(tr, tc, Piece(piece.color, True))
        # after capture, check for continuation
        moved_piece = self.get_piece(tr, tc)
        further_caps = []
        if captures:
            temp_caps = self._moves_for_piece(tr, tc, moved_piece)
            further_caps = [m for m in temp_caps if m[2]]
        if captures and further_caps:
            # same player continues with this piece
            self.selected = (tr, tc)
            # restrict valid moves to continuation captures
            self.valid_moves = {self.selected: further_caps}
            self.message = f"{self.turn.capitalize()} continues capturing"
        else:
            self.selected = None
            self.turn = 'black' if self.turn == 'red' else 'red'
            self.valid_moves = self.all_moves_for(self.turn)
            self.message = f"{self.turn.capitalize()} to move"

    def winner(self):
        reds = sum(1 for r in range(ROWS) for c in range(COLS) if self.get_piece(r,c) and self.get_piece(r,c).color=='red')
        blacks = sum(1 for r in range(ROWS) for c in range(COLS) if self.get_piece(r,c) and self.get_piece(r,c).color=='black')
        if reds == 0:
            return 'black'
        if blacks == 0:
            return 'red'
        red_moves = self.all_moves_for('red')
        black_moves = self.all_moves_for('black')
        if not red_moves:
            return 'black'
        if not black_moves:
            return 'red'
        return None

# Drawing utilities

def board_to_pixel(r, c):
    ox, oy = BOARD_ORIGIN
    x = ox + c * SQUARE
    y = oy + r * SQUARE
    return x, y


def draw_board(surface):
    ox, oy = BOARD_ORIGIN
    pygame.draw.rect(surface, WOOD, (ox-12, oy-12, SQUARE*COLS+24, SQUARE*ROWS+24), border_radius=12)
    for r in range(ROWS):
        for c in range(COLS):
            x, y = board_to_pixel(r, c)
            rect = pygame.Rect(x, y, SQUARE, SQUARE)
            color = DARK if (r + c) % 2 else LIGHT
            pygame.draw.rect(surface, color, rect)


def draw_piece(surface, r, c, piece, selected=False):
    x, y = board_to_pixel(r, c)
    cx = x + SQUARE//2
    cy = y + SQUARE//2
    radius = SQUARE//2 - 12

    base = RED if piece.color=='red' else BLACK
    # rim
    rim = tuple(max(0, min(255,int(ch*0.6))) for ch in base)
    pygame.draw.circle(surface, rim, (cx, cy+5), radius+8)
    # layered circles to simulate shading
    for i in range(5):
        frac = i / 5.0
        color = tuple(int(base[j] * (0.45 + 0.55*(1-frac))) for j in range(3))
        pygame.draw.circle(surface, color, (cx, cy - i//2), int(radius * (1 - i*0.06)))
    # highlight
    highlight_rect = pygame.Rect(0,0, int(radius*1.0), int(radius*0.45))
    highlight_rect.center = (cx - radius//3, cy - radius//2)
    s = pygame.Surface((highlight_rect.w, highlight_rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (255,255,255,120), s.get_rect())
    surface.blit(s, highlight_rect.topleft)

    if piece.king:
        points = [
            (cx - 16, cy - 8),
            (cx - 8, cy - 26),
            (cx, cy - 8),
            (cx + 8, cy - 26),
            (cx + 16, cy - 8)
        ]
        pygame.draw.polygon(surface, (255, 223, 0), points)
        pygame.draw.polygon(surface, (160,120,0), points, 2)

    if selected:
        pygame.draw.circle(surface, HIGHLIGHT, (cx, cy), radius+10, 4)


def draw_valid_moves(surface, game, from_rc):
    moves = game.valid_moves.get(from_rc, [])
    for tr, tc, caps in moves:
        x, y = board_to_pixel(tr, tc)
        center = (x + SQUARE//2, y + SQUARE//2)
        rad = 12 if not caps else 26
        pygame.draw.circle(surface, HIGHLIGHT_MOVE, center, rad)


def draw_ui(surface, game, ai):
    panel_h = 120
    panel_rect = pygame.Rect(0, HEIGHT - panel_h, WIDTH, panel_h)
    pygame.draw.rect(surface, HUD_BG, panel_rect)

    turn_text = FONT_LG.render(f"Turn: {game.turn.capitalize()}", True, (30,30,30))
    surface.blit(turn_text, (30, HEIGHT - panel_h + 16))

    diff_text = FONT.render(f"Difficulty: {ai.difficulty}", True, (20,20,20))
    surface.blit(diff_text, (30, HEIGHT - panel_h + 56))

    cap_text = FONT.render(f"Captured - You(Black taken): {game.captured_counts['black']}   AI(You taken): {game.captured_counts['red']}", True, (40,40,40))
    surface.blit(cap_text, (260, HEIGHT - panel_h + 56))

    msg = FONT.render(game.message, True, (80,80,80))
    surface.blit(msg, (WIDTH//2 - 60, HEIGHT - panel_h + 18))

    # buttons
    btn_restart = pygame.Rect(WIDTH-170, HEIGHT - panel_h + 16, 140, 44)
    pygame.draw.rect(surface, (230,230,230), btn_restart, border_radius=8)
    txt = FONT.render("Restart (R)", True, (30,30,30))
    surface.blit(txt, txt.get_rect(center=btn_restart.center))

    btn_diff = pygame.Rect(WIDTH-170, HEIGHT - panel_h + 72, 140, 36)
    pygame.draw.rect(surface, (230,230,230), btn_diff, border_radius=8)
    txt2 = FONT.render("Change Difficulty", True, (30,30,30))
    surface.blit(txt2, txt2.get_rect(center=btn_diff.center))

    return btn_restart, btn_diff

def mouse_to_cell(mx, my):
    ox, oy = BOARD_ORIGIN
    if ox <= mx < ox + SQUARE*COLS and oy <= my < oy + SQUARE*ROWS:
        c = (mx - ox) // SQUARE
        r = (my - oy) // SQUARE
        return int(r), int(c)
    return None

# Main game & AI setup

game = Checkers()
ai_agent = CheckersAI(game)

# We'll have a small delay for AI thinking on Hard to show it's thinking
AI_THINK_DELAY = 0.3
ai_thinking = False
ai_move_to_play = None
ai_move_time = 0

running = True
while running:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                game.reset()
                ai_agent = CheckersAI(game)
                ai_thinking = False
                ai_move_to_play = None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # check UI clicks
            btn_restart, btn_diff = draw_ui(SCREEN, game, ai_agent)
            if btn_restart.collidepoint((mx,my)):
                game.reset()
                ai_agent = CheckersAI(game)
                ai_thinking = False
                ai_move_to_play = None
                continue
            if btn_diff.collidepoint((mx,my)):
                ai_agent.cycle_difficulty()
                continue
            # if it's player's turn
            if game.turn == 'red' and not ai_thinking:
                sel = mouse_to_cell(mx, my)
                if sel:
                    r, c = sel
                    piece = game.get_piece(r, c)
                    if piece and piece.color == 'red':
                        game.select(r, c)
                    elif game.selected:
                        moves = game.get_selected_moves()
                        moved = False
                        for tr, tc, caps in moves:
                            if tr == r and tc == c:
                                game.move(game.selected, (tr, tc), caps)
                                moved = True
                                break
                        if moved:
                            w = game.winner()
                            if w:
                                game.message = f"{w.capitalize()} wins!"
                            else:
                                # after player move, trigger AI move
                                if game.turn == 'black':
                                    ai_thinking = True
                                    ai_move_time = time.time() + (AI_THINK_DELAY if ai_agent.difficulty=='Hard' else 0.05)
                                    ai_move_to_play = None
                        else:
                            # invalid click: deselect
                            game.selected = None

    # AI move handling
    if ai_thinking and game.turn == 'black':
        if ai_move_to_play is None and time.time() >= ai_move_time - (AI_THINK_DELAY if ai_agent.difficulty=='Hard' else 0):
            # compute move (can take a bit for Hard)
            ai_move_to_play = ai_agent.choose_move()
            # schedule execution slightly later to simulate thinking
            ai_move_time = time.time() + AI_THINK_DELAY
        if ai_move_to_play and time.time() >= ai_move_time:
            fr, to_rc, caps = ai_move_to_play
            game.move(fr, to_rc, caps)
            ai_thinking = False
            ai_move_to_play = None
            w = game.winner()
            if w:
                game.message = f"{w.capitalize()} wins!"

    # draw
    SCREEN.fill(BG)
    draw_board(SCREEN)

    # pieces
    for r in range(ROWS):
        for c in range(COLS):
            p = game.get_piece(r,c)
            if p:
                sel = (game.selected == (r,c))
                draw_piece(SCREEN, r, c, p, selected=sel)

    # valid moves highlight
    if game.selected:
        draw_valid_moves(SCREEN, game, game.selected)

    # UI (drawn after pieces so buttons are on top)
    btn_restart, btn_diff = draw_ui(SCREEN, game, ai_agent)

    # display difficulty small hint
    hint = FONT.render("You play Red — Click your pieces to move. Captures can go backward.", True, (60,60,60))
    SCREEN.blit(hint, (20, HEIGHT - 140))

    pygame.display.flip()

pygame.quit()
sys.exit()
