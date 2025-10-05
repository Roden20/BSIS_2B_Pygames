import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Aether Drift"

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)

# --- Game Physics Settings ---
THRUST_POWER = 0.15      # Rate of acceleration
DRAG_COEFFICIENT = 0.99  # Applied to velocity each frame (slows momentum)
MAX_SPEED = 8.0          # Cap speed to keep things manageable
FUEL_CONSUMPTION_RATE = 0.05 # Fuel consumed per frame when thrusting
ASTEROID_SPAWN_INTERVAL = 60 # Spawn a new asteroid every 60 frames (1 second)

# --- Ship Class (Player) ---
class Player(pygame.sprite.Sprite):
    """
    The player ship, which is NOT fully compatible with pygame.sprite.Group.draw().
    It uses a custom draw() method for a dynamic, non-rectangular shape.
    """
    def __init__(self):
        super().__init__()
        self.radius = 12
        self.color = WHITE
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 90  # Facing up
        self.fuel = 100.0
        self.score = 0
        self.thrusting = False
        
        # NOTE: Player does not use self.image and self.rect, 
        # so it must be drawn manually (self.player.draw())

    def get_points(self):
        """Calculates the three points for the ship's triangular body based on its angle."""
        points = []
        # Nose point (2 * radius distance from center)
        points.append((
            self.pos.x + math.cos(math.radians(self.angle)) * self.radius * 2,
            self.pos.y - math.sin(math.radians(self.angle)) * self.radius * 2
        ))
        # Left wing point
        points.append((
            self.pos.x + math.cos(math.radians(self.angle + 135)) * self.radius,
            self.pos.y - math.sin(math.radians(self.angle + 135)) * self.radius
        ))
        # Right wing point
        points.append((
            self.pos.x + math.cos(math.radians(self.angle - 135)) * self.radius,
            self.pos.y - math.sin(math.radians(self.angle - 135)) * self.radius
        ))
        return points

    def rotate(self, direction):
        """Handles rotation input."""
        if direction == "left":
            self.angle += 4
        elif direction == "right":
            self.angle -= 4

    def thrust(self):
        """Applies force in the direction the ship is currently facing."""
        if self.fuel > 0:
            self.thrusting = True
            
            # Calculate thrust vector
            thrust_x = math.cos(math.radians(self.angle)) * THRUST_POWER
            thrust_y = -math.sin(math.radians(self.angle)) * THRUST_POWER # Negative because y-axis is inverted
            
            # Apply thrust to velocity
            self.vel.x += thrust_x
            self.vel.y += thrust_y
            
            # Consume fuel
            self.fuel -= FUEL_CONSUMPTION_RATE
            if self.fuel < 0:
                self.fuel = 0
        else:
            self.thrusting = False

    def update(self):
        """Updates position based on velocity (inertia) and applies drag."""
        
        self.thrusting = False # Reset thrust state for drawing
        
        # 1. Apply Drag (Damping)
        self.vel *= DRAG_COEFFICIENT

        # 2. Limit Max Speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        # 3. Apply Velocity to Position (The Drift)
        self.pos += self.vel

        # 4. Wrap around screen edges (space travel)
        if self.pos.x < 0: self.pos.x += SCREEN_WIDTH
        if self.pos.x > SCREEN_WIDTH: self.pos.x -= SCREEN_WIDTH
        if self.pos.y < 0: self.pos.y += SCREEN_HEIGHT
        if self.pos.y > SCREEN_HEIGHT: self.pos.y -= SCREEN_HEIGHT

    def draw(self, screen):
        """Draws the ship (triangle) and the thrust flame manually."""
        points = self.get_points()
        
        # 1. Draw Thrust Flame
        if self.thrusting:
            flame_angle = self.angle - 180
            flame_color = (255, random.randint(100, 160), 0)
            
            # Calculate flame tip point
            flame_x = self.pos.x + math.cos(math.radians(flame_angle)) * (self.radius * 2 + random.randint(5, 15))
            flame_y = self.pos.y - math.sin(math.radians(flame_angle)) * (self.radius * 2 + random.randint(5, 15))
            
            # Draw the flame polygon using the back points of the ship
            pygame.draw.polygon(screen, flame_color, points[1:] + [(flame_x, flame_y)])
            
        # 2. Draw Ship Body
        pygame.draw.polygon(screen, self.color, points, 2)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 1) # Center dot

# --- Asteroid Class ---
class Asteroid(pygame.sprite.Sprite):
    """
    An asteroid that is fully compatible with pygame.sprite.Group.draw().
    It renders its jagged shape onto a surface (self.image) and uses a rect (self.rect).
    """
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_radius = random.randint(15, 40)
        self.color = (150, 150, 150)
        self.vel = pygame.math.Vector2(0, 0)
        
        # Sprite requirements for Group.draw()
        self.image = None 
        self.rect = None
        self.original_image = None
        
        # Rotation and Movement
        self.rotation_angle = 0.0
        self.rotation_speed = random.uniform(-1, 1) # Slower rotation speed
        self.angle_offset = random.uniform(0, 360) # Initial orientation
        
        # Create jagged shape points (offsets from center)
        self.points_offsets = self._generate_jagged_points()
        
        # 1. Spawn off-screen
        self._initial_spawn()
        
        # 2. Render the initial image and rect
        self._render_shape()
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _generate_jagged_points(self):
        """Generates the offsets for the irregular polygon shape."""
        offsets = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = math.radians(360 / num_points * i + self.angle_offset)
            # Jitter radius slightly
            current_radius = self.base_radius * random.uniform(0.8, 1.2) 
            x_offset = math.cos(angle) * current_radius
            y_offset = math.sin(angle) * current_radius
            offsets.append((x_offset, y_offset))
        return offsets

    def _render_shape(self):
        """
        FIX: Draws the jagged shape onto a transparent surface (self.image).
        This makes it compatible with pygame.sprite.Group.draw().
        """
        # Determine the size of the surface needed (2x radius buffer)
        size = self.base_radius * 2.5
        self.original_image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.original_image.fill((0, 0, 0, 0)) # Make it transparent
        center = (size // 2, size // 2)

        # Convert offsets to absolute points on the new surface
        polygon_points = []
        for x_offset, y_offset in self.points_offsets:
            polygon_points.append((center[0] + x_offset, center[1] + y_offset))
            
        # Draw the filled and outlined asteroid
        pygame.draw.polygon(self.original_image, self.color, polygon_points)
        pygame.draw.polygon(self.original_image, WHITE, polygon_points, 1) # Outline
        
        # Set the initial image to the original unrotated image
        self.image = self.original_image
        
    def _initial_spawn(self):
        """Determines initial position and velocity off-screen."""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            self.pos = pygame.math.Vector2(random.randint(0, self.screen_width), -self.base_radius)
            self.vel.y = random.uniform(1.5, 3.5)
            self.vel.x = random.uniform(-1, 1)
        elif side == 'bottom':
            self.pos = pygame.math.Vector2(random.randint(0, self.screen_width), self.screen_height + self.base_radius)
            self.vel.y = random.uniform(-3.5, -1.5)
            self.vel.x = random.uniform(-1, 1)
        elif side == 'left':
            self.pos = pygame.math.Vector2(-self.base_radius, random.randint(0, self.screen_height))
            self.vel.x = random.uniform(1.5, 3.5)
            self.vel.y = random.uniform(-1, 1)
        else: # right
            self.pos = pygame.math.Vector2(self.screen_width + self.base_radius, random.randint(0, self.screen_height))
            self.vel.x = random.uniform(-3.5, -1.5)
            self.vel.y = random.uniform(-1, 1)


    def update(self):
        """Move the asteroid and handle rotation (by rotating the image)."""
        self.pos += self.vel
        
        # 1. Update position of the rect
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # 2. Update rotation and rotate the image surface
        self.rotation_angle += self.rotation_speed
        if abs(self.rotation_angle) > 360:
            self.rotation_angle %= 360
            
        # Rotate the original surface and make it the current image
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        
        # Get a new rect for the rotated image, keeping the center point the same
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)
        
    def is_off_screen(self):
        """Checks if the asteroid is far enough off-screen to be deleted."""
        buffer = self.base_radius * 2
        return (self.pos.x < -buffer or self.pos.x > self.screen_width + buffer or
                self.pos.y < -buffer or self.pos.y > self.screen_height + buffer)

# --- Game Class ---
class AetherDrift:
    def __init__(self):
        # Set up screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 72)

        # Game state
        self.player = Player()
        self.asteroids = pygame.sprite.Group()
        self.is_running = True
        self.game_active = True
        self.asteroid_spawn_timer = ASTEROID_SPAWN_INTERVAL
        self.time_survived = 0.0

    def spawn_asteroid(self):
        """Spawns a new asteroid."""
        self.asteroids.add(Asteroid(SCREEN_WIDTH, SCREEN_HEIGHT))

    def check_collisions(self):
        """Handles collision detection between the ship and all asteroids."""
        for asteroid in self.asteroids:
            # Simple circle-to-circle collision check using base_radius
            distance = self.player.pos.distance_to(asteroid.pos)
            if distance < self.player.radius + asteroid.base_radius * 0.8: # Use 80% of base radius for better collision feel
                # Collision detected!
                self.game_active = False

    def handle_input(self):
        """Processes keyboard input for ship movement and game control."""
        keys = pygame.key.get_pressed()
        
        if self.game_active:
            # Rotation
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.rotate("left")
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.rotate("right")
            
            # Thrust
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.thrust()
        
        # General controls (Reset)
        if keys[pygame.K_r] and not self.game_active:
            self.reset_game()

    def update(self):
        """Core game logic update."""
        if self.game_active:
            # --- Update Player ---
            self.player.update()

            # --- Fuel Check ---
            if self.player.fuel <= 0:
                self.game_active = False # Out of fuel!

            # --- Update Asteroids ---
            self.asteroids.update()
            
            # Remove off-screen asteroids and update score
            new_asteroids = pygame.sprite.Group()
            for asteroid in self.asteroids:
                if asteroid.is_off_screen():
                    self.player.score += 10 # Reward for dodging
                else:
                    new_asteroids.add(asteroid)
            self.asteroids = new_asteroids
            
            # --- Spawning ---
            self.asteroid_spawn_timer -= 1
            if self.asteroid_spawn_timer <= 0:
                self.spawn_asteroid()
                # Decrease interval slightly to increase difficulty
                self.asteroid_spawn_timer = max(30, ASTEROID_SPAWN_INTERVAL - int(self.time_survived / 5))
            
            # --- Collision Check ---
            self.check_collisions()

            # --- Time/Score Update ---
            self.time_survived += 1 / FPS

    def draw_ui(self):
        """Renders the fuel, score, and instructions."""
        
        # 1. Score
        score_text = self.font.render(f"SCORE: {int(self.player.score + self.time_survived * 5)}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 2. Velocity Indicator
        vel_mag = self.player.vel.length()
        vel_text = self.font.render(f"SPEED: {vel_mag:.1f}", True, BLUE)
        self.screen.blit(vel_text, (10, 40))

        # 3. Fuel Bar
        fuel_label = self.font.render("FUEL:", True, WHITE)
        self.screen.blit(fuel_label, (SCREEN_WIDTH - 150, 10))
        
        fuel_bar_width = 100
        fuel_bar_height = 15
        fuel_bar_x = SCREEN_WIDTH - fuel_bar_width - 10
        fuel_bar_y = 10
        
        fill = (self.player.fuel / 100) * fuel_bar_width
        
        # Draw background and fill
        pygame.draw.rect(self.screen, RED, (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 2)
        pygame.draw.rect(self.screen, GREEN, (fuel_bar_x, fuel_bar_y, fill, fuel_bar_height))
        
        if not self.game_active:
            self.draw_game_over()
        elif self.time_survived < 5:
            self.draw_intro_instructions()

    def draw_intro_instructions(self):
        """Draws initial instructions."""
        inst_text = self.font.render("W/UP: THRUST | A/LEFT: ROTATE LEFT | D/RIGHT: ROTATE RIGHT", True, YELLOW)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(inst_text, inst_rect)
        
    def draw_game_over(self):
        """Draws the game over message."""
        
        final_score = int(self.player.score + self.time_survived * 5)
        
        if self.player.fuel <= 0:
            message = "OUT OF FUEL - GAME OVER"
        else:
            message = "ASTEROID IMPACT - GAME OVER"

        over_text = self.big_font.render(message, True, RED)
        score_text = self.font.render(f"FINAL SCORE: {final_score}", True, WHITE)
        restart_text = self.font.render("Press 'R' to Restart", True, YELLOW)
        
        self.screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

    def reset_game(self):
        """Resets all game components for a new run."""
        self.player = Player()
        self.asteroids.empty()
        self.game_active = True
        self.asteroid_spawn_timer = ASTEROID_SPAWN_INTERVAL
        self.time_survived = 0.0

    def run(self):
        """The main game loop."""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            
            self.handle_input()
            self.update()

            # --- Drawing ---
            self.screen.fill(BLACK)
            
            # FIX: Asteroids now use Group.draw() because they have .image and .rect
            self.asteroids.draw(self.screen)
            
            # Player is drawn manually because it has a complex, non-rectangular shape
            self.player.draw(self.screen)
            
            # Draw the UI on top
            self.draw_ui()

            # Update the full screen
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = AetherDrift()
    game.run()
