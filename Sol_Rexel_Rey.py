import pygame
import random
import math

# --- 1. CONFIGURATION AND INITIALIZATION ---
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Slither.io Single-Player"
FPS = 60
WORLD_SIZE = 3000  # The actual game world is this large x this large

# Minimap Constants
MINIMAP_SIZE = 150
MINIMAP_MARGIN = 10
MAP_SCALE = MINIMAP_SIZE / WORLD_SIZE # How much smaller the map is than the world

# Colors (Defined as R, G, B tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
BORDER_COLOR = WHITE 
FOOD_COLORS = [RED, GREEN, BLUE, YELLOW, (255, 0, 255), (0, 255, 255)]

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- 2. GAME OBJECT CLASSES ---

class Snake:
    """Represents the player's snake or an AI snake."""
    def __init__(self, start_pos, color, is_player=False):
        self.segments = [start_pos]
        self.length = 10  # Initial length in segments
        self.color = color
        self.radius = 10
        self.speed = 3.0
        self.direction = random.uniform(0, 2 * math.pi)  # Angle in radians
        self.is_player = is_player
        self.boost_speed = 6.0
        self.is_boosting = False
        self.turn_rate = math.pi / 60  # Rate of angle change

    def change_direction(self, target_angle):
        """Smoothly turns the snake towards a target angle."""
        current_angle = self.direction
        
        # Calculate the difference between the target and current angle
        diff = target_angle - current_angle
        
        # Normalize the difference to the range (-pi, pi)
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi

        # Limit the turn rate
        if abs(diff) > self.turn_rate:
            if diff > 0:
                self.direction += self.turn_rate
            else:
                self.direction -= self.turn_rate
        else:
            self.direction = target_angle
            
        # Keep direction within 0 to 2*pi range
        self.direction %= (2 * math.pi)

    def move(self):
        """Updates the snake's position based on its speed and direction."""
        
        # Determine actual speed
        current_speed = self.boost_speed if self.is_boosting and self.is_player else self.speed

        # Calculate new head position
        head_x, head_y = self.segments[0]
        new_x = head_x + current_speed * math.cos(self.direction)
        new_y = head_y + current_speed * math.sin(self.direction)
        
        # Add new head segment
        self.segments.insert(0, (new_x, new_y))
        
        # Trim the tail to maintain length
        while len(self.segments) > self.length:
            self.segments.pop()
            
        # Player specific boost cost
        if self.is_boosting and self.is_player and self.length > 10:
            self.length -= 0.05  # Gradually shrink while boosting
        elif self.length < 10:
            self.is_boosting = False # Stop boosting if too small

    def grow(self, amount):
        """Increases the snake's length."""
        self.length += amount

    def get_head_rect(self):
        """Returns the bounding rectangle for the snake's head."""
        head_x, head_y = self.segments[0]
        return pygame.Rect(head_x - self.radius, head_y - self.radius, 2 * self.radius, 2 * self.radius)

    def draw(self, surface, offset_x, offset_y):
        """Draws the snake on the screen, applying the camera offset."""
        
        # Draw the main body segments
        for i, (x, y) in enumerate(self.segments):
            # Calculate screen position
            draw_x = int(x - offset_x)
            draw_y = int(y - offset_y)
            
            # Draw the segment.
            if i > 0:
                # Use the base color, slightly decreasing radius for trailing effect
                pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.radius - (i * 0.1))

        # Draw the head last for visibility
        head_x, head_y = self.segments[0]
        head_draw_x = int(head_x - offset_x)
        head_draw_y = int(head_y - offset_y)
        pygame.draw.circle(surface, self.color, (head_draw_x, head_draw_y), self.radius)
        pygame.draw.circle(surface, WHITE, (head_draw_x, head_draw_y), self.radius // 2)

class Food:
    """Represents a single food pellet."""
    def __init__(self, pos, color, size=4):
        self.x, self.y = pos
        self.color = color
        self.radius = size
        self.growth_amount = size * 0.5

    def draw(self, surface, offset_x, offset_y):
        """Draws the food pellet on the screen with camera offset."""
        draw_x = int(self.x - offset_x)
        draw_y = int(self.y - offset_y)
        
        # Only draw if on screen
        if 0 < draw_x < SCREEN_WIDTH and 0 < draw_y < SCREEN_HEIGHT:
            pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.radius)
            pygame.draw.circle(surface, WHITE, (draw_x, draw_y), self.radius // 2, 1)

# --- 3. AI LOGIC ---

def ai_control(ai_snake, player_snake, food_list):
    """
    Simple AI logic for the bot snake.
    The AI attempts to move towards the nearest food, while avoiding the player.
    """
    head_x, head_y = ai_snake.segments[0]
    
    # 1. FIND TARGET (Nearest Food)
    min_dist = float('inf')
    target_food = None
    for food in food_list:
        dist = math.hypot(food.x - head_x, food.y - head_y)
        if dist < min_dist:
            min_dist = dist
            target_food = food
            
    target_x, target_y = head_x, head_y
    if target_food:
        target_x, target_y = target_food.x, target_food.y

    # 2. CALCULATE TARGET ANGLE
    target_angle = math.atan2(target_y - head_y, target_x - head_x)
    
    # 3. COLLISION AVOIDANCE (Simple)
    # Check if the player is dangerously close and try to turn away
    player_head_x, player_head_y = player_snake.segments[0]
    dist_to_player = math.hypot(player_head_x - head_x, player_head_y - head_y)
    
    if dist_to_player < 200:
        # If the player is too close, check if the AI is moving towards the player
        angle_to_player = math.atan2(player_head_y - head_y, player_head_x - head_x)
        angle_diff = abs(target_angle - angle_to_player)
        
        # If the angle to the player is roughly the current direction, turn away
        if angle_diff < math.pi / 4: # If player is in a 45 degree cone ahead
             target_angle += random.choice([-math.pi/3, math.pi/3]) # Make a sharp turn

    # 4. APPLY MOVEMENT
    ai_snake.change_direction(target_angle)
    ai_snake.move()


# --- 4. GAME FUNCTIONS ---

def generate_food(count, food_list):
    """Populates the world with food pellets."""
    for _ in range(count):
        x = random.uniform(0, WORLD_SIZE)
        y = random.uniform(0, WORLD_SIZE)
        color = random.choice(FOOD_COLORS)
        size = random.randint(3, 6)
        food_list.append(Food((x, y), color, size))

# Helper function to generate food from a dead snake's segments
def generate_food_from_snake(snake, food_list):
    """Generates a large number of food pellets from a dead snake's body segments."""
    for x, y in snake.segments:
        if random.random() < 0.2: # Only convert a fraction of segments to large food
            size = random.randint(5, 8)
            growth = size * 1.5
        else: # Convert the rest to smaller food
            size = random.randint(3, 5)
            growth = size * 0.5
            
        color = snake.color # Food keeps the color of the dead snake
        
        # Add a slight random offset to scatter the food
        scatter_x = x + random.uniform(-15, 15)
        scatter_y = y + random.uniform(-15, 15)
        
        new_food = Food((scatter_x, scatter_y), color, size)
        new_food.growth_amount = growth
        food_list.append(new_food)


def check_collisions(player, ai_snake, food_list):
    """Handles all in-game collisions."""
    player_head_rect = player.get_head_rect()
    
    # 1. Food Collision
    food_eaten = []
    for food in food_list:
        food_rect = pygame.Rect(food.x - food.radius, food.y - food.radius, 2*food.radius, 2*food.radius)
        if player_head_rect.colliderect(food_rect):
            player.grow(food.growth_amount)
            food_eaten.append(food)
            
    # Remove eaten food
    for food in food_eaten:
        food_list.remove(food)

    # Replenish food to keep the world populated
    if len(food_list) < 500:
        generate_food(10, food_list)
        
    # 2. Player Self-Collision (Player Head vs. Player Body)
    for i in range(10, len(player.segments)): # Start checking 10 segments back
        seg_x, seg_y = player.segments[i]
        seg_dist = math.hypot(seg_x - player.segments[0][0], seg_y - player.segments[0][1])
        if seg_dist < player.radius * 1.5:
            return "PLAYER_DIES"

    # 3. Player Head vs. AI Body (Player Dies)
    for seg_x, seg_y in ai_snake.segments:
        seg_dist = math.hypot(seg_x - player.segments[0][0], seg_y - player.segments[0][1])
        if seg_dist < player.radius + ai_snake.radius:
            return "PLAYER_DIES"

    # 4. AI Head vs. Player Body (AI Dies)
    ai_head_x, ai_head_y = ai_snake.segments[0]
    
    # Check AI head against player body segments
    for i in range(len(player.segments)):
        seg_x, seg_y = player.segments[i]
        seg_dist = math.hypot(seg_x - ai_head_x, seg_y - ai_head_y)
        if seg_dist < player.radius + ai_snake.radius:
            return "AI_DIES" # AI has hit the player's body

    # 5. World Boundary Collision
    head_x, head_y = player.segments[0]
    if not (0 < head_x < WORLD_SIZE and 0 < head_y < WORLD_SIZE):
        return "PLAYER_DIES"
        
    return "NONE" # No deaths

def draw_grid(surface, offset_x, offset_y):
    """Draws a simple grid and the world border on the screen."""
    grid_size = 100
    
    # --- Draw Internal Grid ---
    start_x = int(-offset_x) % grid_size - grid_size
    start_y = int(-offset_y) % grid_size - grid_size
    
    # Draw vertical lines
    for i in range(SCREEN_WIDTH // grid_size + 3):
        x = start_x + i * grid_size
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        
    # Draw horizontal lines
    for i in range(SCREEN_HEIGHT // grid_size + 3):
        y = start_y + i * grid_size
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
        
    # --- Draw World Border ---
    border_x = 0 - offset_x
    border_y = 0 - offset_y
    border_width = WORLD_SIZE
    border_height = WORLD_SIZE
    border_thickness = 10 

    world_rect = pygame.Rect(border_x, border_y, border_width, border_height)
    pygame.draw.rect(surface, BORDER_COLOR, world_rect, border_thickness)


def draw_minimap(surface, player, ai_snake):
    """Draws the minimap in the top right corner."""
    
    # Define the minimap surface area
    map_rect = pygame.Rect(
        SCREEN_WIDTH - MINIMAP_SIZE - MINIMAP_MARGIN, 
        MINIMAP_MARGIN, 
        MINIMAP_SIZE, 
        MINIMAP_SIZE
    )
    
    # Draw the minimap background and border
    pygame.draw.rect(surface, BLACK, map_rect)
    pygame.draw.rect(surface, WHITE, map_rect, 2)
    
    map_left_x = map_rect.left
    map_top_y = map_rect.top

    # Helper function to convert world coordinates to minimap coordinates
    def world_to_map(world_x, world_y):
        map_x = map_left_x + world_x * MAP_SCALE
        map_y = map_top_y + world_y * MAP_SCALE
        return int(map_x), int(map_y)

    # 1. Draw AI Snake (as a dot)
    ai_head_x, ai_head_y = ai_snake.segments[0]
    map_ai_x, map_ai_y = world_to_map(ai_head_x, ai_head_y)
    pygame.draw.circle(surface, ai_snake.color, (map_ai_x, map_ai_y), 3)

    # 2. Draw Player Snake (as a slightly larger dot)
    player_head_x, player_head_y = player.segments[0]
    map_player_x, map_player_y = world_to_map(player_head_x, player_head_y)
    pygame.draw.circle(surface, player.color, (map_player_x, map_player_y), 4)

    # 3. Draw Player's Viewport (the screen area currently visible)
    # The viewport represents the center of the screen
    viewport_width = SCREEN_WIDTH * MAP_SCALE
    viewport_height = SCREEN_HEIGHT * MAP_SCALE
    
    # Calculate the top-left corner of the viewport rectangle on the minimap
    view_x = map_left_x + player_head_x * MAP_SCALE - viewport_width / 2
    view_y = map_top_y + player_head_y * MAP_SCALE - viewport_height / 2
    
    viewport_rect = pygame.Rect(view_x, view_y, viewport_width, viewport_height)
    pygame.draw.rect(surface, WHITE, viewport_rect, 1)


# --- 5. GAME LOOP & MAIN EXECUTION ---

def main():
    player_snake = Snake((WORLD_SIZE / 2, WORLD_SIZE / 2), WHITE, is_player=True)
    current_ai_snake = Snake((WORLD_SIZE / 2 + 500, WORLD_SIZE / 2 + 500), RED, is_player=False)
    current_ai_snake.length = 50 # Make the AI snake start large

    food_list = []
    generate_food(1000, food_list) # Initial food population

    game_over = False
    running = True

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Player Boosting (Spacebar/Mouse click)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_snake.is_boosting = True
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                player_snake.is_boosting = False
                
            # Restart game
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main() # Re-call main to restart the game
                return 

        if not game_over:
            # --- Input/Movement ---
            
            # Player turns towards the mouse cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_angle = math.atan2(mouse_y - SCREEN_HEIGHT / 2, mouse_x - SCREEN_WIDTH / 2)
            player_snake.change_direction(target_angle)
            player_snake.move()
            
            # AI Logic
            ai_control(current_ai_snake, player_snake, food_list)

            # --- Camera Update (Follow the player) ---
            head_x, head_y = player_snake.segments[0]
            offset_x = head_x - SCREEN_WIDTH / 2
            offset_y = head_y - SCREEN_HEIGHT / 2

            # --- Collision Check ---
            collision_result = check_collisions(player_snake, current_ai_snake, food_list)

            if collision_result == "PLAYER_DIES":
                game_over = True
            elif collision_result == "AI_DIES":
                # AI Death Logic: Convert AI to food and respawn
                generate_food_from_snake(current_ai_snake, food_list)
                
                # Respawn AI snake at a random location
                new_x = random.uniform(0, WORLD_SIZE)
                new_y = random.uniform(0, WORLD_SIZE)
                current_ai_snake = Snake((new_x, new_y), RED, is_player=False)
                current_ai_snake.length = 50 # Start AI large again

            # --- Drawing ---
            screen.fill(BLACK)
            
            # 1. Draw Grid/Background and Border
            draw_grid(screen, offset_x, offset_y)
            
            # 2. Draw Food
            for food in food_list:
                food.draw(screen, offset_x, offset_y)
            
            # 3. Draw AI Snake
            current_ai_snake.draw(screen, offset_x, offset_y)

            # 4. Draw Player Snake
            player_snake.draw(screen, offset_x, offset_y)

            # 5. Draw UI (Score/Length)
            score_text = font.render(f"Length: {int(player_snake.length)}", True, WHITE)
            screen.blit(score_text, (10, 10))

            # 6. Draw Minimap (LAST so it overlaps everything)
            draw_minimap(screen, player_snake, current_ai_snake)

        else:
            # --- Game Over Screen ---
            game_over_text = font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Length: {int(player_snake.length)}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH / 2 - game_over_text.get_width() / 2, SCREEN_HEIGHT / 2 - 50))
            screen.blit(final_score_text, (SCREEN_WIDTH / 2 - final_score_text.get_width() / 2, SCREEN_HEIGHT / 2))
            screen.blit(restart_text, (SCREEN_WIDTH / 2 - restart_text.get_width() / 2, SCREEN_HEIGHT / 2 + 50))

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
