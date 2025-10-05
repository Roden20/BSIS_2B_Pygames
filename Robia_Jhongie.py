import pygame
import random
import sys

# --- Pygame Initialization and Setup ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocket Shooter - Asteroid Blast")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Game state variables
GAME_LEVEL = 1
MAX_LEVEL = 6
SCORE = 0
BULLET_LEVEL = 1
BULLET_LEVEL_UP_SCORE = 30 # Score threshold for the first bullet upgrade
 ###
####
### note if the game is not firing just resart the game 
### if the firing is stop just restart be patient 
### because it having a bug only
# Game Clock
clock = pygame.time.Clock()
FPS = 60

# --- Utility Functions ---

def draw_text(surface, text, size, x, y, color=WHITE):
    """Utility function to draw text on the screen."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def get_level_attributes(level):
    """Determines enemy size, speed, color, and spawn count based on the game level."""
    base_speed = 2.0
    base_size = 20
    
    # Speed increases by 0.5 for each level
    speed = base_speed + (level * 0.5)
    
    # Size increases by 5 pixels for each level (max 50 pixels at level 6)
    size = base_size + (level * 5)
    
    # Different enemy colors for visual difference per level (Asteroid appearance)
    colors = [
        (100, 100, 100), # Level 1: Grey (Basic)
        (150, 75, 0),    # Level 2: Brown/Rock
        (100, 50, 0),    # Level 3: Dark Brown/Dense
        (150, 150, 0),   # Level 4: Yellowish/Cracked
        (0, 100, 100),   # Level 5: Cyan/Icy
        (50, 50, 50)     # Level 6: Black/Very Dense
    ]
    # Ensure index doesn't exceed the list length
    color = colors[min(level, MAX_LEVEL) - 1]
    
    # Number of enemies to spawn
    num_enemies = 5 + (level * 2)
    
    return size, speed, color, num_enemies

# --- Game Objects (Sprites) ---

class Player(pygame.sprite.Sprite):
    """The player controlled rocket ship."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([40, 40], pygame.SRCALPHA) # Transparent surface
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 7
        self.health = 100
        
        # Draw the rocket (a simple white triangle)
        self.points = [(20, 0), (0, 40), (40, 40)]
        pygame.draw.polygon(self.image, WHITE, self.points)

    def update(self):
        """Update player position based on key presses."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            
        # Keep player within screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

    def shoot(self, bullet_level):
        """Creates two new bullet instances, one from the left and one from the right gun."""
        # Calculate offset positions for the two guns (10 pixels left/right of center)
        left_x = self.rect.centerx - 10
        right_x = self.rect.centerx + 10

        # Bullet 1 (Left Gun)
        bullet1 = Bullet(left_x, self.rect.top, bullet_level)
        all_sprites.add(bullet1)
        bullets.add(bullet1)
        
        # Bullet 2 (Right Gun)
        bullet2 = Bullet(right_x, self.rect.top, bullet_level)
        all_sprites.add(bullet2)
        bullets.add(bullet2)

class Bullet(pygame.sprite.Sprite):
    """A bullet fired by the player."""
    def __init__(self, x, y, level):
        super().__init__()
        
        # Bullet size scales with BULLET_LEVEL
        base_radius = 4
        self.radius = base_radius + (level * 2) 
        
        # Create a surface for the bullet
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        # Draw a bright yellow circle
        pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -12 # Moves up fast
        
    def update(self):
        """Move the bullet up and kill it if it goes off screen."""
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """An enemy asteroid that falls from the top."""
    def __init__(self, level):
        super().__init__()
        
        self.level = level
        self.size, self.speed, self.color, _ = get_level_attributes(level)
        
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Draw an irregular asteroid shape using polygon
        center = self.size // 2
        points = [
            (center, 0), 
            (self.size, center * 0.5), 
            (self.size * 0.75, self.size), 
            (center * 0.25, self.size * 0.8),
            (0, center * 0.5)
        ]
        pygame.draw.polygon(self.image, self.color, points)
        
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randrange(-150, -50) # Start off-screen
        
    def update(self):
        """Move the asteroid down and reset it if it goes off screen."""
        self.rect.y += self.speed
        
        # If asteroid goes off bottom, reset it to give the player a chance
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()
            
    def reset_position(self):
        """Reset asteroid to the top with random x position, maintaining level attributes."""
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randrange(-150, -50)

# --- Background Stars ---
stars = []
for _ in range(150): # More stars for a better space look
    stars.append({
        'x': random.randrange(0, SCREEN_WIDTH),
        'y': random.randrange(0, SCREEN_HEIGHT),
        'size': random.randrange(1, 4), # Size/brightness
        'speed': random.uniform(0.1, 0.5) # Slight downward drift
    })

def draw_stars(surface):
    """Draws the space background stars and makes them slowly drift down."""
    for star in stars:
        # Move star down (slow drift)
        star['y'] += star['speed']
        
        # Reset star to top if it goes off screen
        if star['y'] > SCREEN_HEIGHT:
            star['y'] = 0
            star['x'] = random.randrange(0, SCREEN_WIDTH)
            
        pygame.draw.circle(surface, WHITE, (int(star['x']), int(star['y'])), star['size'])

# --- Game Setup and Enemy Spawning ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def spawn_enemies(level):
    """Spawns enemies based on the current level, clearing existing ones."""
    global enemies, all_sprites
    
    # Clear existing enemies to switch to the new, tougher level enemies
    for enemy in enemies:
        enemy.kill() 
        
    _, _, _, num_enemies = get_level_attributes(level)
    
    for _ in range(num_enemies):
        enemy = Enemy(level)
        all_sprites.add(enemy)
        enemies.add(enemy)

# Initial enemy spawn
spawn_enemies(GAME_LEVEL)

# --- Main Game Loop ---
running = True
game_over = False
can_shoot = True # Control shooting rate

while running:
    # 1. Process Input/Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle game restart when game is over
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r: 
            # Reset game state
            GAME_LEVEL = 1
            SCORE = 0
            BULLET_LEVEL = 1
            player = Player() # Recreate player
            all_sprites.add(player)
            spawn_enemies(GAME_LEVEL)
            game_over = False

    # Shooting control (Unlimited bullets on hold)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not game_over:
        # Simple fire rate limiting using a custom attribute
        if can_shoot:
            player.shoot(BULLET_LEVEL)
            can_shoot = False
            # Use a timer or a simple frame delay to prevent instant firing
            pygame.time.set_timer(pygame.USEREVENT + 1, 150, 1) # Fire every 150ms

    if event.type == pygame.USEREVENT + 1:
        can_shoot = True


    if game_over:
        # If game is over, only draw the screen and wait for restart
        screen.fill(BLACK)
        draw_stars(screen)
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED)
        draw_text(screen, f"Final Score: {SCORE}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "Press R to Restart", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, YELLOW)
        pygame.display.flip()
        clock.tick(FPS)
        continue # Skip the rest of the game logic

    # 2. Update
    all_sprites.update()
    
    # --- Collision Detection ---
    
    # Collision: Bullet vs. Enemy
    # The 'True, True' arguments mean both the bullet and the enemy sprite are killed on collision.
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        SCORE += 1 # Increase score for each hit
        
        # Check for permanent bullet level up at the score threshold
        if SCORE >= BULLET_LEVEL_UP_SCORE and BULLET_LEVEL == 3:
            global BULLET_LEVEL_
            BULLET_LEVEL = 6
            
        # Spawn a new enemy to replace the destroyed one, keeping the current level
        new_enemy = Enemy(GAME_LEVEL)
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)
        
    # Collision: Player vs. Enemy
    # Player takes damage, enemy is destroyed
    player_hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in player_hits:
        player.health -= 30 # Player takes 25 damage
        
        # Spawn a new enemy to replace the destroyed one
        new_enemy = Enemy(GAME_LEVEL)
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)
        
        if player.health <= 0:
            game_over = True
            player.kill() # Remove player from the screen
            
    # --- Level Up Logic (based on score threshold) ---
    # Advance to the next level every 20 points
    level_threshold_kills = 20
    next_level = (SCORE // level_threshold_kills) + 1
    
    if next_level > GAME_LEVEL and next_level <= MAX_LEVEL:
        GAME_LEVEL = next_level
        print(f"Level Up! Now on Level {GAME_LEVEL}")
        
        # Restore player health to 100 on level up
        player.health = 100

        # When leveling up, clear all enemies and spawn a fresh wave of new, harder enemies
        spawn_enemies(GAME_LEVEL) # This function clears and respawns

    # 3. Draw/Render
    screen.fill(BLACK) # Black background for space

    # Draw stars
    draw_stars(screen)

    # Draw all sprites
    all_sprites.draw(screen)

    # --- Draw UI/HUD ---
    
    # Score
    draw_text(screen, f"Score: {SCORE}", 30, SCREEN_WIDTH - 80, 20)
    
    # Level
    draw_text(screen, f"Level: {GAME_LEVEL} / {MAX_LEVEL}", 30, 100, 20, GREEN)

    # Bullet Power Level
    power_color = YELLOW if BULLET_LEVEL > 1 else WHITE
    draw_text(screen, f"Bullet Power: {'MAX' if BULLET_LEVEL == 2 else '1'}", 30, SCREEN_WIDTH // 2, 20, power_color)

    # Health Bar 
    # Check if player is still in the sprite group (i.e., not dead) before drawing the health bar
    if player in all_sprites:
        bar_width = 100
        bar_height = 10
        fill = (player.health / 100) * bar_width
        outline_rect = pygame.Rect(10, SCREEN_HEIGHT - 30, bar_width, bar_height)
        fill_rect = pygame.Rect(10, SCREEN_HEIGHT - 30, fill, bar_height)
        
        pygame.draw.rect(screen, GREEN, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)
        draw_text(screen, "HP", 20, 30, SCREEN_HEIGHT - 45)


    # 4. Flip the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()

### note if the game is not firing just resart the game 
### if the firing is stop just restart be patient 
### because it having a bug only




