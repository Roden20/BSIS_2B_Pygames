import pygame
import sys
import time
import math
import random

# --- Constants ---
# Screen dimensions for a 28x24 tile grid
TILE_SIZE = 24
GRID_WIDTH = 28
GRID_HEIGHT = 24
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + 60
FPS = 60

# --- Colors ---
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)      # Blinky's Color
PINK = (255, 192, 203) # Pinky's Color
CYAN = (0, 255, 255)   # Inky's Color
ORANGE = (255, 165, 0) # Clyde's Color
FRIGHTENED_BLUE = (0, 0, 255) 

# --- Maze Data (The Board) ---
# Codes: 0: Path, 1: Wall, 2: Dot, 3: Power Pellet, 4: Ghost Gate
MAZE_TEMPLATE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1],
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 1, 1, 2, 1, 0, 0, 0, 0, 0], # Tunnel Row / Ghost Gate
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
    [1, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 1],
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class Pacman:
    def __init__(self, start_grid_x, start_grid_y, speed):
        self.start_grid_x = start_grid_x
        self.start_grid_y = start_grid_y
        self.grid_x = float(start_grid_x)
        self.grid_y = float(start_grid_y)
        self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.speed = speed
        self.direction = (0, 0)
        self.requested_direction = (0, 0)
        self.last_non_zero_direction = (1, 0)
        self.score = 0
        self.lives = 3
        self.is_powered_up = False
        self.powerup_end_time = 0
        self.animation_timer = 0
        self.mouth_state = 0
        self.is_dead = False # New state for game over animation

    def get_grid_coords(self):
        return int(self.pixel_x // TILE_SIZE), int(self.pixel_y // TILE_SIZE)
    
    def check_turn(self, maze_data):
        if self.requested_direction != self.direction:
            dx, dy = self.requested_direction
            next_grid_x = self.get_grid_coords()[0] + dx
            next_grid_y = self.get_grid_coords()[1] + dy
            
            if 0 <= next_grid_y < len(maze_data) and 0 <= next_grid_x < len(maze_data[0]):
                if maze_data[next_grid_y][next_grid_x] != 1:
                    current_grid_x, current_grid_y = self.get_grid_coords()
                    center_x = current_grid_x * TILE_SIZE + TILE_SIZE // 2
                    center_y = current_grid_y * TILE_SIZE + TILE_SIZE // 2
                    
                    if dx != 0 and abs(self.pixel_y - center_y) < self.speed:
                        # Snap to center before turning horizontally
                        self.pixel_y = center_y
                        self.direction = self.requested_direction
                        return True
                    
                    elif dy != 0 and abs(self.pixel_x - center_x) < self.speed:
                        # Snap to center before turning vertically
                        self.pixel_x = center_x
                        self.direction = self.requested_direction
                        return True
        return False
    
    def check_collision(self, dx, dy, maze_data):
        new_pixel_x = self.pixel_x + dx * self.speed
        new_pixel_y = self.pixel_y + dy * self.speed
        
        target_grid_x = int((new_pixel_x + dx * TILE_SIZE / 2) // TILE_SIZE)
        target_grid_y = int((new_pixel_y + dy * TILE_SIZE / 2) // TILE_SIZE)
        
        if 0 <= target_grid_y < len(maze_data) and 0 <= target_grid_x < len(maze_data[0]):
            if maze_data[target_grid_y][target_grid_x] != 1:
                return False
        
        if target_grid_x < 0 or target_grid_x >= len(maze_data[0]):
            return False
            
        return True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.requested_direction = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.requested_direction = (1, 0)
        elif keys[pygame.K_UP]:
            self.requested_direction = (0, -1)
        elif keys[pygame.K_DOWN]:
            self.requested_direction = (0, 1)

    def update(self, maze_data):
        if self.is_dead:
            return

        # Update powerup status
        if self.is_powered_up and time.time() > self.powerup_end_time:
            self.is_powered_up = False
        
        # 1. Check for possible turn/direction change
        self.check_turn(maze_data)
        
        # 2. Check collision with the current direction
        dx, dy = self.direction
        
        if self.direction != (0, 0):
            self.last_non_zero_direction = self.direction
            
        if self.check_collision(dx, dy, maze_data):
            self.direction = (0, 0)
            current_grid_x, current_grid_y = self.get_grid_coords()
            self.pixel_x = current_grid_x * TILE_SIZE + TILE_SIZE // 2
            self.pixel_y = current_grid_y * TILE_SIZE + TILE_SIZE // 2
            return

        # 3. Move the Player!
        self.pixel_x += dx * self.speed
        self.pixel_y += dy * self.speed
        
        # Check for tunnel wrap
        if self.pixel_x < -TILE_SIZE/2:
            self.pixel_x = SCREEN_WIDTH + TILE_SIZE/2
        elif self.pixel_x > SCREEN_WIDTH + TILE_SIZE/2:
            self.pixel_x = -TILE_SIZE/2
        
        # 4. Scoring and 'Eating' The dots and powerups!
        current_grid_x, current_grid_y = self.get_grid_coords()
        
        if 0 <= current_grid_y < len(maze_data) and 0 <= current_grid_x < len(maze_data[0]):
            tile_type = maze_data[current_grid_y][current_grid_x]
            
            if tile_type == 2: # Dot
                maze_data[current_grid_y][current_grid_x] = 0
                self.score += 10
                return True # Indicates a dot was eaten
            elif tile_type == 3: # Power Pellet
                maze_data[current_grid_y][current_grid_x] = 0
                self.score += 50
                
                # Activate power up and trigger ghost reversal
                if not self.is_powered_up:
                    self.is_powered_up = True
                    self.powerup_end_time = time.time() + 8.0 # Power up lasts 8 seconds
                    return 'POWERUP' # Indicates a powerup was eaten
        return False # Nothing important eaten

    def draw(self, surface):
        center_x = int(self.pixel_x)
        center_y = int(self.pixel_y)
        radius = TILE_SIZE // 2
        
        pacman_color = YELLOW
        # Simple flashing effect when powered up
        if self.is_powered_up and (int(time.time() * 10) % 2 == 0):
            pacman_color = WHITE
            
        pygame.draw.circle(surface, pacman_color, (center_x, center_y), radius)

        # Only animate mouth if not dead
        if not self.is_dead:
            # Animation logic for mouth
            self.animation_timer += 1
            if self.animation_timer > (5 if self.direction != (0, 0) else 10): 
                self.mouth_state = 1 - self.mouth_state
                self.animation_timer = 0
                
            # Draw the mouth cut-out if the mouth is "open"
            if self.mouth_state == 1:
                dx, dy = self.last_non_zero_direction
                
                mouth_size_factor = 0.6
                
                P0 = (center_x, center_y)
                
                # Determine the direction of the opening
                perp_dx = -dy * radius * mouth_size_factor
                perp_dy = dx * radius * mouth_size_factor
                
                dir_dx = dx * radius
                dir_dy = dy * radius
                
                P1 = (center_x + dir_dx + perp_dx, center_y + dir_dy + perp_dy)
                P2 = (center_x + dir_dx - perp_dx, center_y + dir_dy - perp_dy)
                
                mouth_points = [P0, P1, P2]
                pygame.draw.polygon(surface, BLACK, mouth_points)

# --- GHOST CLASS ---
class Ghost:
    def __init__(self, start_grid_x, start_grid_y, speed, color, name):
        self.start_grid_x = start_grid_x
        self.start_grid_y = start_grid_y
        self.grid_x = float(start_grid_x)
        self.grid_y = float(start_grid_y)
        # Ghost starts on an integer tile, centered, just like Pacman.
        self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.base_speed = speed
        self.speed = speed
        self.color = color
        self.name = name 
        # Blinky (the first ghost) starts moving immediately, others wait in the house.
        self.direction = (0, -1) if name == "Blinky" else (0, 0)
        self.target = (0, 0)
        self.is_eaten = False 
        self.is_frightened = False 

    def get_grid_coords(self):
        return int(self.pixel_x // TILE_SIZE), int(self.pixel_y // TILE_SIZE)

    def is_centered(self):
        """Checks if the ghost is centered enough on the tile to make a turn decision."""
        current_grid_x, current_grid_y = self.get_grid_coords()
        center_x = current_grid_x * TILE_SIZE + TILE_SIZE // 2
        center_y = current_grid_y * TILE_SIZE + TILE_SIZE // 2
        
        # The tolerance for centering must be slightly less than half the speed to ensure snapping happens.
        return abs(self.pixel_x - center_x) < self.speed / 2 and abs(self.pixel_y - center_y) < self.speed / 2

    def get_valid_moves(self, maze_data):
        """Returns a list of valid (dx, dy) directions from the current tile."""
        x, y = self.get_grid_coords()
        valid_moves = {}
        
        possible_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in possible_directions:
            # Ghost rule: Cannot reverse direction unless frightened
            if self.direction != (0, 0) and (dx * -1, dy * -1) == self.direction and not self.is_frightened:
                continue

            next_x, next_y = x + dx, y + dy
            
            # Check maze bounds and wall collision (1)
            if 0 <= next_y < len(maze_data) and 0 <= next_x < len(maze_data[0]):
                tile = maze_data[next_y][next_x]
                
                # Ghosts cannot enter wall (1)
                if tile == 1:
                    continue
                
                # Ghost gate (4) logic: 
                # Normal/Frightened ghosts cannot pass the gate from below (i.e., move UP into it from inside the box).
                if tile == 4 and not self.is_eaten and next_y > 9: 
                    continue

                valid_moves[(dx, dy)] = (next_x, next_y)
            
            # Allow tunnel warp
            elif next_x < 0 or next_x >= len(maze_data[0]):
                valid_moves[(dx, dy)] = (next_x, next_y)

        return valid_moves

    def calculate_distance(self, p1, p2):
        """Calculate squared Euclidean distance (faster than square root)"""
        return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

    def set_frightened_state(self, is_powered_up):
        """Set the state and determine if the ghost needs to reverse direction."""
        if is_powered_up and not self.is_frightened:
            # Immediately reverse direction when power-up starts
            self.direction = (self.direction[0] * -1, self.direction[1] * -1)
        
        self.is_frightened = is_powered_up
    
    def calculate_target(self, pacman_grid_pos, pacman_direction, blinky_grid_pos):
        """Calculates the target tile based on ghost AI logic (Chase/Scatter)."""
        pacman_x, pacman_y = pacman_grid_pos
        pacman_dx, pacman_dy = pacman_direction
        blinky_x, blinky_y = blinky_grid_pos

        if self.name == "Blinky":
            # Chase: Targets Pac-Man's tile
            return pacman_x, pacman_y
        
        elif self.name == "Pinky":
            # Ambush: Targets 4 tiles ahead of Pac-Man (uses Pac-Man's last non-zero direction)
            return pacman_x + 4 * pacman_dx, pacman_y + 4 * pacman_dy
            
        elif self.name == "Inky":
            # Scatter: Bottom right corner (26, 22)
            scatter_target = (GRID_WIDTH - 2, GRID_HEIGHT - 2) 
            
            # Inky's complex target: Go two tiles ahead of Pac-Man, draw a vector from Blinky to that tile, and extend it again.
            pacman_2_ahead_x = pacman_x + 2 * pacman_dx
            pacman_2_ahead_y = pacman_y + 2 * pacman_dy
            
            vector_x = pacman_2_ahead_x - blinky_x
            vector_y = pacman_2_ahead_y - blinky_y
            
            chase_target = pacman_2_ahead_x + vector_x, pacman_2_ahead_y + vector_y
            
            # Currently always chasing for simplicity until more advanced logic is implemented
            return chase_target

        elif self.name == "Clyde":
            # Scatter target (bottom left corner): (1, 22)
            scatter_target = (1, GRID_HEIGHT - 2) 
            
            ghost_x_grid, ghost_y_grid = self.get_grid_coords()
            distance_to_pacman_sq = self.calculate_distance(pacman_grid_pos, (ghost_x_grid, ghost_y_grid))
            
            if distance_to_pacman_sq > 8**2: 
                # Chase: Targets Pac-Man's tile if more than 8 tiles away
                return pacman_x, pacman_y
            else:
                # Scatter: Targets bottom-left corner if within 8 tiles
                return scatter_target


    def update(self, maze_data, pacman_grid_pos, pacman_direction, blinky_grid_pos, pacman_powerup_end_time):
        
        is_powered_up = time.time() < pacman_powerup_end_time
        self.set_frightened_state(is_powered_up)

        # 0. Set speed and target based on state
        if self.is_eaten:
            # Target the respawn point (center of the ghost house gate: 13, 9)
            self.target = (13, 9) 
            self.speed = 3.5 
            
            # Check if the eaten ghost has reached the respawn tile
            if self.get_grid_coords() == (13, 9):
                self.is_eaten = False 
                # Snap to center of gate tile
                self.pixel_x = 13 * TILE_SIZE + TILE_SIZE // 2 
                self.pixel_y = 9 * TILE_SIZE + TILE_SIZE // 2
                self.direction = (0, 0) # Stops at the gate
        
        elif self.is_frightened:
            self.target = (0, 0) # Target is irrelevant for random movement
            self.speed = 1.0 # Slow speed
            
        else:
            self.speed = self.base_speed
            # Calculate Chase/Scatter target
            self.target = self.calculate_target(pacman_grid_pos, pacman_direction, blinky_grid_pos)


        # 1. Decision Point: Only check for new direction when centered on a tile
        if self.is_centered():
            x, y = self.get_grid_coords()
            
            # Snap to center (Crucial for consistent grid-based movement)
            self.pixel_x = x * TILE_SIZE + TILE_SIZE // 2
            self.pixel_y = y * TILE_SIZE + TILE_SIZE // 2

            valid_moves = self.get_valid_moves(maze_data)
            
            # Check for turn (intersection, start, or frightened)
            if self.direction == (0, 0) or len(valid_moves) > 1 or self.is_frightened:
                
                if self.is_frightened:
                    # Frightened: Choose a random valid move
                    if valid_moves:
                        self.direction = random.choice(list(valid_moves.keys()))
                else:
                    # Chase/Scatter: Choose the path that gets closest to the target
                    best_direction = self.direction
                    min_distance = float('inf')

                    for direction, (next_x, next_y) in valid_moves.items():
                        distance = self.calculate_distance((next_x, next_y), self.target)
                        
                        if distance < min_distance:
                            min_distance = distance
                            best_direction = direction
                    
                    self.direction = best_direction
            
            # Special case for ghosts inside the house (Pinky, Inky, Clyde) to start moving
            elif len(valid_moves) == 1 and self.direction == (0, 0):
                self.direction = list(valid_moves.keys())[0]


        # 2. Movement
        dx, dy = self.direction
        self.pixel_x += dx * self.speed
        self.pixel_y += dy * self.speed
        
        self.grid_x = self.pixel_x / TILE_SIZE
        self.grid_y = self.pixel_y / TILE_SIZE
        
        # Check for tunnel wrap
        if self.pixel_x < -TILE_SIZE/2:
            self.pixel_x = SCREEN_WIDTH + TILE_SIZE/2
        elif self.pixel_x > SCREEN_WIDTH + TILE_SIZE/2:
            self.pixel_x = -TILE_SIZE/2

    def draw(self, surface, pacman_powerup_end_time):
        """Simulates the ghost asset using Pygame drawing primitives."""
        center_x = int(self.pixel_x)
        center_y = int(self.pixel_y)
        
        if self.is_eaten:
            ghost_color = BLACK
        else:
            ghost_color = self.color 
            if self.is_frightened:
                time_left = pacman_powerup_end_time - time.time()
                
                # Flashing white/blue warning in the last 2 seconds
                if time_left < 2.0 and (int(time.time() * 10) % 2 == 0):
                    ghost_color = WHITE
                else:
                    ghost_color = FRIGHTENED_BLUE

        body_width = TILE_SIZE - 2
        body_height = TILE_SIZE - 2
        head_radius = body_width // 2
        
        # 1. Draw the main body
        rect_height = body_height // 2 + 4
        rect_y = center_y - 2
        rect = pygame.Rect(center_x - body_width // 2, rect_y, body_width, rect_height)
        pygame.draw.rect(surface, ghost_color, rect, border_top_left_radius=0, border_top_right_radius=0)
        pygame.draw.circle(surface, ghost_color, (center_x, center_y - head_radius + 4), head_radius)
        
        # 2. Draw the 'Skirt' (Tentacles at the bottom)
        skirt_y = center_y + rect_height - 2
        tentacle_count = 4
        tentacle_width = body_width / tentacle_count
        
        for i in range(tentacle_count):
            start_x = center_x - body_width // 2 + i * tentacle_width
            points = [
                (start_x, skirt_y),
                (start_x + tentacle_width / 2, skirt_y + 4),
                (start_x + tentacle_width, skirt_y),
                (start_x + tentacle_width, rect_y + rect_height), 
                (start_x, rect_y + rect_height) 
            ]
            pygame.draw.polygon(surface, ghost_color, points)
            
            if not self.is_frightened and not self.is_eaten and i > 0:
                pygame.draw.line(surface, BLACK, (start_x, skirt_y), (start_x, skirt_y + 2), 1)

        # 3. Draw Eyes
        eye_radius = TILE_SIZE // 8
        eye_offset_x = TILE_SIZE // 6
        eye_offset_y = -TILE_SIZE // 8 
        
        left_eye_pos = (center_x - eye_offset_x, center_y + eye_offset_y)
        right_eye_pos = (center_x + eye_offset_x, center_y + eye_offset_y)
        
        if self.is_eaten:
            eye_offset_y -= TILE_SIZE // 4 # Draw eyes higher up
            eaten_left_eye_pos = (center_x - eye_offset_x, center_y + eye_offset_y)
            eaten_right_eye_pos = (center_x + eye_offset_x, center_y + eye_offset_y)
            
            pygame.draw.circle(surface, WHITE, eaten_left_eye_pos, eye_radius)
            pygame.draw.circle(surface, WHITE, eaten_right_eye_pos, eye_radius)
            
            pupil_radius = TILE_SIZE // 16
            target_x_pixel = 13 * TILE_SIZE + TILE_SIZE // 2
            target_y_pixel = 9 * TILE_SIZE + TILE_SIZE // 2
            
            angle = math.atan2(target_y_pixel - center_y, target_x_pixel - center_x)
            
            pupil_offset = TILE_SIZE // 12
            pupil_dx = int(math.cos(angle) * pupil_offset / 2)
            pupil_dy = int(math.sin(angle) * pupil_offset / 2)
            
            pygame.draw.circle(surface, (0, 0, 0), (eaten_left_eye_pos[0] + pupil_dx, eaten_left_eye_pos[1] + pupil_dy), pupil_radius)
            pygame.draw.circle(surface, (0, 0, 0), (eaten_right_eye_pos[0] + pupil_dx, eaten_right_eye_pos[1] + pupil_dy), pupil_radius)
            
        elif self.is_frightened:
            pygame.draw.circle(surface, WHITE, left_eye_pos, eye_radius)
            pygame.draw.circle(surface, WHITE, right_eye_pos, eye_radius)
            
        else:
            pygame.draw.circle(surface, WHITE, left_eye_pos, eye_radius)
            pygame.draw.circle(surface, WHITE, right_eye_pos, eye_radius)
            
            pupil_radius = TILE_SIZE // 16
            dx, dy = self.direction if self.direction != (0, 0) else (1, 0) 
            
            pupil_offset = TILE_SIZE // 12
            pupil_dx = int(dx * pupil_offset / 2)
            pupil_dy = int(dy * pupil_offset / 2)
            
            pygame.draw.circle(surface, (0, 0, 0), (left_eye_pos[0] + pupil_dx, left_eye_pos[1] + pupil_dy), pupil_radius)
            pygame.draw.circle(surface, (0, 0, 0), (right_eye_pos[0] + pupil_dx, right_eye_pos[1] + pupil_dy), pupil_radius)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Pac-Man Clone")
        self.clock = pygame.time.Clock()
        
        self.pacman_start_pos = (1.0, 1.0)
        # FIX: Changed fractional start coordinates to integer coordinates (full tiles)
        # to align with the grid-based movement and centering logic (is_centered).
        # (13, 8) is the intersection right above the gate.
        self.ghost_start_data = [
            (13, 8, 1.6, RED, "Blinky"),   
            (13, 11, 1.5, PINK, "Pinky"),  
            (11, 11, 1.4, CYAN, "Inky"),   
            (15, 11, 1.4, ORANGE, "Clyde") 
        ]
        
        self.font = pygame.font.Font(None, 36)
        self.level = 1
        self.is_running = True
        self.is_game_over = False
        self.setup_level()

    def setup_level(self):
        """Initializes the maze, Pacman, and Ghosts for a new level."""
        self.maze = [row[:] for row in MAZE_TEMPLATE] # Reset the maze
        self.pacman = Pacman(*self.pacman_start_pos, 2)
        self.reset_ghosts()

    def reset_ghosts(self):
         # Initialize all four ghosts
        self.ghosts = [Ghost(*data) for data in self.ghost_start_data]

    def reset_game_state(self, pacman_died=True):
        """Resets Pacman and ghosts to start positions."""
        
        if pacman_died:
            self.pacman.lives -= 1
            if self.pacman.lives <= 0:
                self.is_game_over = True
                return

        # Reset Pacman state
        self.pacman.grid_x, self.pacman.grid_y = self.pacman_start_pos
        self.pacman.pixel_x = self.pacman_start_pos[0] * TILE_SIZE + TILE_SIZE // 2
        self.pacman.pixel_y = self.pacman_start_pos[1] * TILE_SIZE + TILE_SIZE // 2
        self.pacman.direction = (0, 0)
        self.pacman.requested_direction = (0, 0)
        self.pacman.last_non_zero_direction = (1, 0)
        self.pacman.is_powered_up = False
        self.pacman.powerup_end_time = 0
        self.pacman.is_dead = False
        
        # Reset Ghosts
        self.reset_ghosts()
        
    def check_level_complete(self):
        """Checks if all dots and power pellets have been eaten."""
        for row in self.maze:
            if 2 in row or 3 in row:
                return False
        return True

    def check_collisions(self):
        # Allow a slightly smaller hit box for Pacman to avoid accidental wall contact
        pacman_rect = pygame.Rect(
            self.pacman.pixel_x - TILE_SIZE // 4, 
            self.pacman.pixel_y - TILE_SIZE // 4, 
            TILE_SIZE // 2, 
            TILE_SIZE // 2
        )
        
        # Iterate backward to allow safe removal/state change
        for i in range(len(self.ghosts)):
            ghost = self.ghosts[i]

            if ghost.is_eaten:
                continue

            ghost_rect = pygame.Rect(
                ghost.pixel_x - TILE_SIZE // 4, 
                ghost.pixel_y - TILE_SIZE // 4, 
                TILE_SIZE // 2, 
                TILE_SIZE // 2
            )

            if pacman_rect.colliderect(ghost_rect):
                if self.pacman.is_powered_up:
                    # Pacman eats ghost
                    ghost.is_eaten = True
                    self.pacman.score += 200 
                    ghost.direction = (0, 0) 
                    # Pause briefly for the player to register the score
                    pygame.time.delay(100) 
                else:
                    # Ghost eats Pacman
                    self.pacman.is_dead = True # Set flag for death animation
                    pygame.time.delay(500) 
                    self.reset_game_state(pacman_died=True)
                    return 

    def draw_board(self):
        """Drawing Each Tile Type onto the board."""
        for y, row in enumerate(self.maze):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if tile == 1: # Wall
                    pygame.draw.rect(self.screen, BLUE, rect)
                
                elif tile == 2: # Dot
                    pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE // 8)
                    
                elif tile == 3: # Power Pellet
                    # Flashing Power Pellet
                    if (int(time.time() * 5) % 2 == 0):
                        pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE // 4)
                
                elif tile == 4: # Ghost Gate
                    pygame.draw.line(self.screen, RED, rect.topleft, rect.topright, 2)

    def draw_ui(self):
        ui_y = GRID_HEIGHT * TILE_SIZE + 15
        
        score_text = self.font.render(f"Score: {self.pacman.score}", True, WHITE)
        self.screen.blit(score_text, (10, ui_y))
        
        lives_text = self.font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 10 - lives_text.get_width(), ui_y))
        
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, ui_y - 15))
        self.screen.blit(level_text, level_rect)

        if self.pacman.is_powered_up:
            time_left = max(0, self.pacman.powerup_end_time - time.time())
            power_text = self.font.render(f"POWER UP ({time_left:.1f}s)", True, RED)
            power_rect = power_text.get_rect(center=(SCREEN_WIDTH // 2, ui_y + 10))
            self.screen.blit(power_text, power_rect)
        
        if self.is_game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            
            if self.is_game_over:
                self.screen.fill(BLACK)
                self.draw_ui()
                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            self.pacman.handle_input()
            
            # --- Game Update ---
            self.pacman.update(self.maze)
            
            self.check_collisions()

            # Check if all pellets are cleared (Level Complete)
            if self.check_level_complete():
                self.level += 1
                self.pacman.score += 1000 # Bonus points for level completion
                pygame.time.delay(1000)
                self.setup_level() # Advance to next level!
                
            # Find Blinky's current grid position for Inky's targeting logic
            blinky = next((g for g in self.ghosts if g.name == "Blinky"), None)
            blinky_grid_pos = blinky.get_grid_coords() if blinky else (13, 8)
            
            # Update all Ghosts
            pacman_grid_pos = self.pacman.get_grid_coords()
            pacman_direction = self.pacman.last_non_zero_direction
            powerup_end_time = self.pacman.powerup_end_time

            for ghost in self.ghosts:
                ghost.update(self.maze, pacman_grid_pos, pacman_direction, blinky_grid_pos, powerup_end_time)

            # --- Drawing ---
            self.screen.fill(BLACK)
            self.draw_board()
            self.pacman.draw(self.screen)
            
            for ghost in self.ghosts:
                ghost.draw(self.screen, powerup_end_time)
                
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()