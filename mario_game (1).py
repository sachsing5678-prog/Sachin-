import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
TERMINAL_VELOCITY = 15

# Colors
SKY_BLUE = (92, 148, 252)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BRICK_COLOR = (180, 100, 50)
PIPE_GREEN = (0, 168, 0)
QUESTION_YELLOW = (255, 185, 0)
GROUND_BROWN = (139, 90, 43)
COIN_GOLD = (255, 215, 0)

class Camera:
    """Camera that follows the player"""
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target):
        # Follow player horizontally
        x = -target.rect.centerx + int(SCREEN_WIDTH / 3)
        y = 0  # Don't move vertically
        
        # Limit scrolling to level bounds
        x = min(0, x)  # Left edge
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right edge
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Mario(pygame.sprite.Sprite):
    """Mario player character with authentic physics"""
    def __init__(self, x, y):
        super().__init__()
        self.state = "small"  # small, super, fire
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.max_speed = 6
        self.acceleration = 0.5
        self.friction = 0.8
        self.jump_power = 14
        self.facing_right = True
        
        # Animation
        self.animation_frame = 0
        self.animation_counter = 0
        self.is_walking = False
        self.is_jumping = False
        
        # Invincibility after getting hit
        self.invincible = False
        self.invincible_timer = 0
        self.star_power = False
        self.star_timer = 0
        
        # Fire Mario
        self.can_shoot = False
        self.fireball_cooldown = 0
        
        self.draw_mario()
    
    def draw_mario(self):
        """Draw Mario sprite"""
        self.image.fill((0, 0, 0, 0))
        
        # Determine height based on state
        if self.state == "super" or self.state == "fire":
            self.height = 48
            hat_y = 2
            face_y = 12
        else:
            self.height = 32
            hat_y = 2
            face_y = 10
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect.height = self.height
        
        # Rainbow effect for star power
        if self.star_power:
            # Cycle through colors
            rainbow_offset = (pygame.time.get_ticks() // 100) % 6
        
        # Hat (red)
        hat_color = (220, 20, 20)
        if self.star_power:
            colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (138, 43, 226)]
            hat_color = colors[rainbow_offset]
        
        pygame.draw.ellipse(self.image, hat_color, (4, hat_y, 24, 12))
        pygame.draw.rect(self.image, hat_color, (6, hat_y + 6, 20, 8))
        
        # Hat logo (M)
        pygame.draw.circle(self.image, WHITE, (16, hat_y + 6), 4)
        
        # Face (peach)
        pygame.draw.ellipse(self.image, (255, 220, 177), (8, face_y, 16, 16))
        
        # Eyes
        if self.is_walking:
            offset = (self.animation_frame % 2)
            pygame.draw.circle(self.image, BLACK, (12, face_y + 6), 2)
            pygame.draw.circle(self.image, BLACK, (20, face_y + 6), 2)
        else:
            pygame.draw.circle(self.image, BLACK, (13, face_y + 6), 2)
            pygame.draw.circle(self.image, BLACK, (19, face_y + 6), 2)
        
        # Nose
        pygame.draw.circle(self.image, (255, 200, 160), (16, face_y + 10), 2)
        
        # Mustache
        pygame.draw.ellipse(self.image, (101, 67, 33), (10, face_y + 11, 12, 5))
        
        # Shirt color (red for normal, white for fire)
        shirt_color = WHITE if self.state == "fire" else (220, 20, 20)
        overalls_color = (30, 90, 200) if self.state != "fire" else (220, 20, 20)
        
        # Rainbow colors for star power
        if self.star_power:
            shirt_color = colors[(rainbow_offset + 2) % 6]
            overalls_color = colors[(rainbow_offset + 4) % 6]
        
        # Body
        body_y = face_y + 16
        pygame.draw.rect(self.image, shirt_color, (8, body_y, 16, 8))
        
        # Overalls
        pygame.draw.rect(self.image, overalls_color, (10, body_y + 4, 12, 12))
        
        # Buttons
        pygame.draw.circle(self.image, QUESTION_YELLOW, (13, body_y + 8), 2)
        pygame.draw.circle(self.image, QUESTION_YELLOW, (19, body_y + 8), 2)
        
        # Arms (animated based on walking)
        arm_offset = 0
        if self.is_walking:
            arm_offset = 2 if self.animation_frame % 2 == 0 else -2
        
        pygame.draw.rect(self.image, shirt_color, (4, body_y + 2 + arm_offset, 4, 10))
        pygame.draw.rect(self.image, shirt_color, (24, body_y + 2 - arm_offset, 4, 10))
        
        # Legs (animated)
        leg_y = body_y + 16
        if self.is_walking and self.on_ground:
            if self.animation_frame % 2 == 0:
                pygame.draw.rect(self.image, overalls_color, (10, leg_y, 5, 10))
                pygame.draw.rect(self.image, overalls_color, (17, leg_y - 2, 5, 12))
            else:
                pygame.draw.rect(self.image, overalls_color, (10, leg_y - 2, 5, 12))
                pygame.draw.rect(self.image, overalls_color, (17, leg_y, 5, 10))
        else:
            pygame.draw.rect(self.image, overalls_color, (10, leg_y, 5, 10))
            pygame.draw.rect(self.image, overalls_color, (17, leg_y, 5, 10))
        
        # Shoes
        shoe_y = leg_y + 10
        pygame.draw.ellipse(self.image, (101, 67, 33), (8, shoe_y, 8, 4))
        pygame.draw.ellipse(self.image, (101, 67, 33), (16, shoe_y, 8, 4))
        
        # Flip if facing left
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity_x -= self.acceleration
            self.facing_right = False
            self.is_walking = True
        elif keys[pygame.K_RIGHT]:
            self.velocity_x += self.acceleration
            self.facing_right = True
            self.is_walking = True
        else:
            self.is_walking = False
        
        # Apply friction
        self.velocity_x *= self.friction
        
        # Limit speed
        if abs(self.velocity_x) > self.max_speed:
            self.velocity_x = self.max_speed if self.velocity_x > 0 else -self.max_speed
        
        # Stop if moving very slowly
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0
    
    def jump(self):
        """Make Mario jump"""
        if self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False
            self.is_jumping = True
    
    def shoot_fireball(self):
        """Shoot a fireball (only if Fire Mario)"""
        if self.can_shoot and self.fireball_cooldown <= 0:
            self.fireball_cooldown = 20  # Cooldown between shots
            direction = 1 if self.facing_right else -1
            offset_x = 20 if self.facing_right else -20
            return Fireball(self.rect.centerx + offset_x, self.rect.centery, direction)
        return None
    
    def update(self, platforms, question_blocks, bricks, pipes):
        """Update Mario's position and state"""
        self.handle_input()
        
        # Apply gravity
        self.velocity_y += GRAVITY
        if self.velocity_y > TERMINAL_VELOCITY:
            self.velocity_y = TERMINAL_VELOCITY
        
        # Update animation
        if self.is_walking and self.on_ground:
            self.animation_counter += 1
            if self.animation_counter >= 8:
                self.animation_frame += 1
                self.animation_counter = 0
        
        # Invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Star power timer
        if self.star_power:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star_power = False
        
        # Fireball cooldown
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        
        # Horizontal movement and collision
        self.rect.x += self.velocity_x
        self.check_collision_x(platforms + question_blocks + bricks + pipes)
        
        # Vertical movement and collision
        self.rect.y += self.velocity_y
        self.on_ground = False
        self.check_collision_y(platforms + question_blocks + bricks + pipes)
        
        # Redraw Mario
        self.draw_mario()
        
        # Check if fell off the world
        if self.rect.top > SCREEN_HEIGHT:
            return "dead"
        
        return None
    
    def check_collision_x(self, platforms):
        """Check horizontal collisions"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                self.velocity_x = 0
    
    def check_collision_y(self, platforms):
        """Check vertical collisions"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.velocity_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                    
                    # Hit question block or brick from below
                    if hasattr(platform, 'hit'):
                        platform.hit()
    
    def power_up(self, power_type="super"):
        """Power up Mario"""
        if power_type == "super":
            if self.state == "small":
                self.state = "super"
                old_bottom = self.rect.bottom
                self.draw_mario()
                self.rect.bottom = old_bottom
        elif power_type == "fire":
            if self.state == "small":
                self.state = "super"
            self.state = "fire"
            self.can_shoot = True
            old_bottom = self.rect.bottom
            self.draw_mario()
            self.rect.bottom = old_bottom
        elif power_type == "star":
            self.star_power = True
            self.star_timer = 600  # 10 seconds at 60 FPS
    
    def take_damage(self):
        """Take damage"""
        if self.invincible or self.star_power:
            return False
        
        if self.state == "super" or self.state == "fire":
            self.state = "small"
            self.can_shoot = False
            self.invincible = True
            self.invincible_timer = 120  # 2 seconds at 60 FPS
            old_bottom = self.rect.bottom
            self.draw_mario()
            self.rect.bottom = old_bottom
            return False
        else:
            return True  # Mario dies

class Ground(pygame.sprite.Sprite):
    """Ground/Floor platform"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw()
    
    def draw(self):
        # Ground texture
        self.image.fill(GROUND_BROWN)
        
        # Add brick pattern
        for y in range(0, self.rect.height, 16):
            for x in range(0, self.rect.width, 16):
                pygame.draw.rect(self.image, (120, 80, 40), (x, y, 16, 16), 1)
        
        # Top grass layer
        for x in range(0, self.rect.width, 4):
            pygame.draw.line(self.image, (34, 139, 34), (x, 0), (x + 2, 0), 2)

class QuestionBlock(pygame.sprite.Sprite):
    """Question mark block"""
    def __init__(self, x, y, item_type="coin"):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.item_type = item_type  # "coin", "mushroom", "fire_flower", "star", "1up"
        self.is_active = True
        self.bounce_offset = 0
        self.bouncing = False
        self.bounce_speed = 0
        self.draw()
    
    def draw(self):
        if self.is_active:
            # Yellow block with question mark
            self.image.fill(QUESTION_YELLOW)
            
            # Border
            pygame.draw.rect(self.image, (255, 215, 100), (0, 0, 32, 32), 3)
            pygame.draw.rect(self.image, (200, 140, 0), (3, 3, 26, 26), 2)
            
            # Question mark
            font = pygame.font.Font(None, 28)
            text = font.render("?", True, WHITE)
            text_rect = text.get_rect(center=(16, 16))
            self.image.blit(text, text_rect)
            
            # Corner decorations
            for x, y in [(6, 6), (26, 6), (6, 26), (26, 26)]:
                pygame.draw.circle(self.image, WHITE, (x, y), 2)
        else:
            # Used block (brown)
            self.image.fill(BRICK_COLOR)
            pygame.draw.rect(self.image, (150, 80, 40), (0, 0, 32, 32), 2)
    
    def hit(self):
        """Called when Mario hits the block from below"""
        if self.is_active:
            self.is_active = False
            self.bouncing = True
            self.bounce_speed = -8
            self.draw()
            return self.item_type
        return None
    
    def update(self):
        if self.bouncing:
            self.bounce_offset += self.bounce_speed
            self.rect.y += self.bounce_speed
            self.bounce_speed += 1
            
            if self.bounce_offset >= 0:
                self.rect.y -= self.bounce_offset
                self.bounce_offset = 0
                self.bouncing = False
                self.bounce_speed = 0

class Brick(pygame.sprite.Sprite):
    """Breakable brick block"""
    def __init__(self, x, y, breakable=True):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.breakable = breakable
        self.broken = False
        self.draw()
    
    def draw(self):
        # Orange brick
        self.image.fill(BRICK_COLOR)
        
        # Brick pattern
        for row in range(2):
            for col in range(2):
                offset = row * 8
                pygame.draw.rect(self.image, (160, 90, 45), 
                               (col * 16 + offset, row * 16, 16, 16), 2)
    
    def hit(self):
        """Called when hit from below"""
        if self.breakable:
            self.broken = True
            return "break"
        return None

class Pipe(pygame.sprite.Sprite):
    """Warp pipe"""
    def __init__(self, x, y, height):
        super().__init__()
        self.width = 64
        self.height = height
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw()
    
    def draw(self):
        # Pipe body
        pygame.draw.rect(self.image, PIPE_GREEN, (8, 16, 48, self.height - 16))
        
        # Pipe rim (top)
        pygame.draw.rect(self.image, (0, 200, 0), (0, 0, 64, 20))
        pygame.draw.rect(self.image, (0, 140, 0), (4, 4, 56, 12))
        
        # Shading
        pygame.draw.rect(self.image, (0, 140, 0), (8, 16, 24, self.height - 16))
        
        # Highlight
        pygame.draw.rect(self.image, (50, 220, 50), (36, 20, 4, self.height - 20))

class Goomba(pygame.sprite.Sprite):
    """Goomba enemy"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -1.5
        self.velocity_y = 0
        self.is_alive = True
        self.squashed = False
        self.animation_frame = 0
        self.animation_counter = 0
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.squashed:
            # Flat squashed goomba
            pygame.draw.ellipse(self.image, (139, 90, 43), (4, 20, 24, 8))
            return
        
        # Body
        pygame.draw.ellipse(self.image, (139, 90, 43), (4, 8, 24, 22))
        
        # Feet (animated)
        foot_offset = 2 if self.animation_frame % 2 == 0 else -2
        pygame.draw.ellipse(self.image, (101, 67, 33), (2, 26, 12, 6))
        pygame.draw.ellipse(self.image, (101, 67, 33), (18, 26, 12, 6))
        
        # Angry eyebrows
        pygame.draw.line(self.image, BLACK, (8, 12), (11, 14), 3)
        pygame.draw.line(self.image, BLACK, (24, 12), (21, 14), 3)
        
        # Eyes
        pygame.draw.circle(self.image, WHITE, (10, 16), 4)
        pygame.draw.circle(self.image, WHITE, (22, 16), 4)
        pygame.draw.circle(self.image, BLACK, (10, 17), 2)
        pygame.draw.circle(self.image, BLACK, (22, 17), 2)
        
        # Fangs
        points1 = [(14, 22), (16, 25), (18, 22)]
        pygame.draw.polygon(self.image, WHITE, points1)
    
    def update(self, platforms):
        if not self.is_alive:
            return
        
        # Animation
        self.animation_counter += 1
        if self.animation_counter >= 15:
            self.animation_frame += 1
            self.animation_counter = 0
            if not self.squashed:
                self.draw()
        
        if self.squashed:
            return
        
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check platform collisions
        on_platform = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    on_platform = True
                elif self.velocity_x != 0:
                    # Hit wall, turn around
                    self.velocity_x *= -1
        
        # Turn around at edges
        if not on_platform and self.velocity_y == 0:
            self.velocity_x *= -1
    
    def stomp(self):
        """Called when Mario stomps on the goomba"""
        self.squashed = True
        self.is_alive = False
        self.draw()

class Mushroom(pygame.sprite.Sprite):
    """Super Mushroom power-up"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 32  # Spawn above block
        self.velocity_x = 2
        self.velocity_y = -4  # Pop up
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Stem
        pygame.draw.rect(self.image, (250, 240, 230), (12, 18, 8, 12))
        
        # Cap
        pygame.draw.ellipse(self.image, (220, 20, 60), (4, 6, 24, 18))
        
        # White spots
        pygame.draw.circle(self.image, WHITE, (10, 12), 4)
        pygame.draw.circle(self.image, WHITE, (22, 12), 4)
        pygame.draw.circle(self.image, WHITE, (16, 18), 3)
        
        # Eyes
        pygame.draw.circle(self.image, BLACK, (13, 22), 2)
        pygame.draw.circle(self.image, BLACK, (19, 22), 2)
    
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Platform collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                if self.rect.right > platform.rect.left and self.velocity_x > 0:
                    self.velocity_x *= -1
                if self.rect.left < platform.rect.right and self.velocity_x < 0:
                    self.velocity_x *= -1

class FireFlower(pygame.sprite.Sprite):
    """Fire Flower power-up"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 32  # Spawn above block
        self.velocity_y = -4  # Pop up
        self.animation_frame = 0
        self.animation_counter = 0
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Stem (green)
        pygame.draw.rect(self.image, (0, 168, 0), (12, 20, 8, 10))
        
        # Flower petals (alternating red/orange/yellow)
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 100, 0)]
        angle_offset = (self.animation_frame * 10) % 360
        
        # Center
        pygame.draw.circle(self.image, (255, 255, 0), (16, 14), 6)
        
        # Petals
        petal_positions = [
            (16, 6),   # Top
            (24, 14),  # Right
            (16, 22),  # Bottom
            (8, 14),   # Left
        ]
        
        for i, (px, py) in enumerate(petal_positions):
            color = colors[i % len(colors)]
            pygame.draw.circle(self.image, color, (px, py), 5)
        
        # Eyes on center
        pygame.draw.circle(self.image, BLACK, (14, 13), 1)
        pygame.draw.circle(self.image, BLACK, (18, 13), 1)
    
    def update(self, platforms):
        # Animation
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_frame += 1
            self.animation_counter = 0
            self.draw()
        
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move
        self.rect.y += self.velocity_y
        
        # Platform collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0

class Star(pygame.sprite.Sprite):
    """Invincibility Star power-up"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 32  # Spawn above block
        self.velocity_x = 3
        self.velocity_y = -8  # Pop up and bounce
        self.animation_frame = 0
        self.animation_counter = 0
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Rotating rainbow star
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), 
                  (0, 0, 255), (138, 43, 226)]
        color = colors[self.animation_frame % len(colors)]
        
        # Draw star
        center_x, center_y = 16, 16
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180
            if i % 2 == 0:
                radius = 12
            else:
                radius = 5
            x = center_x + radius * (angle and 1) * 10  # Simplified
            y = center_y + radius * (angle and 1) * 10
            points.append((x, y))
        
        # Simple star shape
        star_points = [
            (16, 4),   # Top
            (19, 12),  # Top right inner
            (28, 12),  # Right
            (21, 18),  # Bottom right inner
            (24, 28),  # Bottom right
            (16, 22),  # Bottom inner
            (8, 28),   # Bottom left
            (11, 18),  # Bottom left inner
            (4, 12),   # Left
            (13, 12),  # Top left inner
        ]
        
        pygame.draw.polygon(self.image, color, star_points)
        pygame.draw.polygon(self.image, WHITE, star_points, 2)
        
        # Sparkles
        pygame.draw.circle(self.image, WHITE, (16, 16), 3)
    
    def update(self, platforms):
        # Animation
        self.animation_counter += 1
        if self.animation_counter >= 5:
            self.animation_frame += 1
            self.animation_counter = 0
            self.draw()
        
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Platform collision - bounce
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = -8  # Bounce
                if self.rect.right > platform.rect.left and self.velocity_x > 0:
                    self.velocity_x *= -1
                if self.rect.left < platform.rect.right and self.velocity_x < 0:
                    self.velocity_x *= -1

class OneUpMushroom(pygame.sprite.Sprite):
    """1-Up Mushroom (extra life)"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 32  # Spawn above block
        self.velocity_x = 2
        self.velocity_y = -4  # Pop up
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Stem
        pygame.draw.rect(self.image, (250, 240, 230), (12, 18, 8, 12))
        
        # Cap (green instead of red)
        pygame.draw.ellipse(self.image, (0, 200, 0), (4, 6, 24, 18))
        
        # White spots
        pygame.draw.circle(self.image, WHITE, (10, 12), 4)
        pygame.draw.circle(self.image, WHITE, (22, 12), 4)
        pygame.draw.circle(self.image, WHITE, (16, 18), 3)
        
        # Eyes
        pygame.draw.circle(self.image, BLACK, (13, 22), 2)
        pygame.draw.circle(self.image, BLACK, (19, 22), 2)
    
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Platform collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                if self.rect.right > platform.rect.left and self.velocity_x > 0:
                    self.velocity_x *= -1
                if self.rect.left < platform.rect.right and self.velocity_x < 0:
                    self.velocity_x *= -1

class Fireball(pygame.sprite.Sprite):
    """Fireball that Mario shoots"""
    def __init__(self, x, y, direction):
        super().__init__()
        self.width = 16
        self.height = 16
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 8 * direction
        self.velocity_y = -3
        self.lifetime = 180  # 3 seconds
        self.animation_frame = 0
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Rotating fireball
        colors = [(255, 100, 0), (255, 200, 0), (255, 255, 100)]
        color = colors[self.animation_frame % 3]
        
        pygame.draw.circle(self.image, color, (8, 8), 7)
        pygame.draw.circle(self.image, (255, 255, 200), (8, 8), 4)
        pygame.draw.circle(self.image, WHITE, (6, 6), 2)
    
    def update(self, platforms):
        self.animation_frame += 1
        self.draw()
        
        # Apply gravity
        self.velocity_y += GRAVITY * 0.5
        
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Bounce off ground
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = -4  # Bounce
        
        # Lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Coin(pygame.sprite.Sprite):
    """Collectible coin"""
    def __init__(self, x, y, floating=True):
        super().__init__()
        self.width = 24
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.floating = floating
        self.float_offset = 0
        self.float_direction = 1
        self.animation_frame = 0
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Coin
        pygame.draw.ellipse(self.image, COIN_GOLD, (2, 8, 20, 20))
        pygame.draw.ellipse(self.image, (218, 165, 32), (5, 11, 14, 14))
        
        # Shine
        pygame.draw.circle(self.image, (255, 255, 200), (10, 14), 4)
    
    def update(self):
        if self.floating:
            self.animation_frame += 1
            if self.animation_frame % 3 == 0:
                self.rect.y += self.float_direction
                self.float_offset += self.float_direction
                if abs(self.float_offset) > 4:
                    self.float_direction *= -1

class Flag(pygame.sprite.Sprite):
    """Level end flag"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 48
        self.height = 320
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw()
    
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        
        # Pole
        pygame.draw.rect(self.image, WHITE, (22, 0, 4, 320))
        
        # Flag
        flag_color = (0, 200, 0)
        points = [(26, 20), (46, 30), (26, 40)]
        pygame.draw.polygon(self.image, flag_color, points)
        pygame.draw.polygon(self.image, BLACK, points, 2)
        
        # Pole top
        pygame.draw.circle(self.image, WHITE, (24, 10), 6)

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time_left = 400
        self.level_width = 6400
        
        # Camera
        self.camera = Camera(self.level_width, SCREEN_HEIGHT)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = []
        self.question_blocks = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.mushrooms = pygame.sprite.Group()
        self.fire_flowers = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.oneup_mushrooms = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        
        # Create player
        self.mario = Mario(100, 400)
        self.all_sprites.add(self.mario)
        
        # Build level
        self.build_level()
        
        # Font
        self.font = pygame.font.Font(None, 32)
        
        # Timer
        self.timer_counter = 0
    
    def build_level(self):
        """Build the level"""
        # Ground
        ground = Ground(0, 550, self.level_width, 50)
        self.platforms.append(ground)
        self.all_sprites.add(ground)
        
        # Floating platforms
        platform_positions = [
            (300, 450, 128, 16),
            (500, 380, 96, 16),
            (700, 450, 128, 16),
            (1000, 400, 160, 16),
            (1300, 350, 96, 16),
            (1600, 400, 128, 16),
            (1900, 320, 160, 16),
            (2200, 400, 128, 16),
            (2600, 350, 160, 16),
            (3000, 400, 96, 16),
            (3300, 300, 128, 16),
            (3600, 380, 160, 16),
            (4000, 320, 128, 16),
            (4300, 400, 96, 16),
        ]
        
        for x, y, w, h in platform_positions:
            platform = Ground(x, y, w, h)
            self.platforms.append(platform)
            self.all_sprites.add(platform)
        
        # Question blocks
        qblock_positions = [
            (400, 350, "coin"),
            (432, 350, "mushroom"),
            (464, 350, "coin"),
            (800, 350, "fire_flower"),
            (1100, 300, "coin"),
            (1400, 250, "mushroom"),
            (1700, 300, "1up"),
            (2000, 220, "coin"),
            (2300, 300, "star"),
            (2700, 250, "coin"),
            (3100, 300, "fire_flower"),
            (3400, 200, "coin"),
            (3700, 280, "mushroom"),
            (4100, 220, "1up"),
        ]
        
        for x, y, item in qblock_positions:
            block = QuestionBlock(x, y, item)
            self.question_blocks.add(block)
            self.all_sprites.add(block)
        
        # Bricks
        brick_positions = [
            (368, 350), (496, 350), (528, 350),
            (768, 350), (832, 350), (864, 350),
            (1200, 300), (1232, 300),
            (2100, 220), (2132, 220),
            (2800, 250), (2832, 250),
            (3500, 200), (3532, 200),
        ]
        
        for x, y in brick_positions:
            brick = Brick(x, y)
            self.bricks.add(brick)
            self.all_sprites.add(brick)
        
        # Pipes
        pipe_positions = [
            (600, 486, 64),
            (1500, 454, 96),
            (2400, 454, 96),
            (3200, 486, 64),
            (4200, 422, 128),
        ]
        
        for x, y, h in pipe_positions:
            pipe = Pipe(x, y, h)
            self.pipes.add(pipe)
            self.all_sprites.add(pipe)
        
        # Coins
        coin_positions = [
            (450, 300), (850, 300), (1150, 250),
            (1750, 250), (2050, 170), (2350, 250),
            (2750, 200), (3150, 250), (3450, 150),
            (3750, 230), (4150, 170),
        ]
        
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.coin_sprites.add(coin)
            self.all_sprites.add(coin)
        
        # Goombas
        goomba_positions = [
            (700, 518), (950, 518), (1250, 518),
            (1800, 518), (2100, 518), (2500, 518),
            (2900, 518), (3400, 518), (3800, 518),
            (4300, 518),
        ]
        
        for x, y in goomba_positions:
            goomba = Goomba(x, y)
            self.enemies.add(goomba)
            self.all_sprites.add(goomba)
        
        # Flag at end
        self.flag = Flag(self.level_width - 200, 230)
        self.all_sprites.add(self.flag)
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.mario.jump()
                if event.key == pygame.K_x or event.key == pygame.K_LCTRL:
                    # Shoot fireball
                    fireball = self.mario.shoot_fireball()
                    if fireball:
                        self.fireballs.add(fireball)
                        self.all_sprites.add(fireball)
    
    def update(self):
        """Update game state"""
        # Update timer
        self.timer_counter += 1
        if self.timer_counter >= 60:
            self.time_left -= 1
            self.timer_counter = 0
            if self.time_left <= 0:
                self.lives -= 1
                self.reset_level()
        
        # Update Mario
        all_platforms = (self.platforms + 
                        list(self.question_blocks) + 
                        list(self.bricks) + 
                        list(self.pipes))
        
        result = self.mario.update(all_platforms, 
                                   list(self.question_blocks),
                                   list(self.bricks),
                                   list(self.pipes))
        
        if result == "dead":
            self.lives -= 1
            self.reset_level()
        
        # Update camera
        self.camera.update(self.mario)
        
        # Update question blocks and spawn power-ups
        for block in self.question_blocks:
            block.update()
            
        # Check which blocks were just hit
        for block in self.question_blocks:
            if hasattr(block, '_just_hit') and block._just_hit:
                item = block.item_type
                if item == "mushroom":
                    mushroom = Mushroom(block.rect.x, block.rect.y)
                    self.mushrooms.add(mushroom)
                    self.all_sprites.add(mushroom)
                elif item == "fire_flower":
                    flower = FireFlower(block.rect.x, block.rect.y)
                    self.fire_flowers.add(flower)
                    self.all_sprites.add(flower)
                elif item == "star":
                    star = Star(block.rect.x, block.rect.y)
                    self.stars.add(star)
                    self.all_sprites.add(star)
                elif item == "1up":
                    oneup = OneUpMushroom(block.rect.x, block.rect.y)
                    self.oneup_mushrooms.add(oneup)
                    self.all_sprites.add(oneup)
                elif item == "coin":
                    self.coins += 1
                    self.score += 100
                block._just_hit = False
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms + list(self.pipes))
        
        # Update mushrooms
        for mushroom in self.mushrooms:
            mushroom.update(self.platforms + list(self.pipes))
        
        # Update fire flowers
        for flower in self.fire_flowers:
            flower.update(self.platforms + list(self.pipes))
        
        # Update stars
        for star in self.stars:
            star.update(self.platforms + list(self.pipes))
        
        # Update 1-up mushrooms
        for oneup in self.oneup_mushrooms:
            oneup.update(self.platforms + list(self.pipes))
        
        # Update coins
        for coin in self.coin_sprites:
            coin.update()
        
        # Update fireballs
        for fireball in self.fireballs:
            fireball.update(self.platforms + list(self.pipes))
        
        # Check mushroom collection
        mushroom_hits = pygame.sprite.spritecollide(self.mario, self.mushrooms, True)
        if mushroom_hits:
            self.mario.power_up("super")
            self.score += 1000
        
        # Check fire flower collection
        flower_hits = pygame.sprite.spritecollide(self.mario, self.fire_flowers, True)
        if flower_hits:
            self.mario.power_up("fire")
            self.score += 1000
        
        # Check star collection
        star_hits = pygame.sprite.spritecollide(self.mario, self.stars, True)
        if star_hits:
            self.mario.power_up("star")
            self.score += 1000
        
        # Check 1-up collection
        oneup_hits = pygame.sprite.spritecollide(self.mario, self.oneup_mushrooms, True)
        if oneup_hits:
            self.lives += 1
            self.score += 1000
        
        # Check coin collection
        coin_hits = pygame.sprite.spritecollide(self.mario, self.coin_sprites, True)
        for coin in coin_hits:
            self.coins += 1
            self.score += 200
        
        # Check fireball hitting enemies
        for fireball in self.fireballs:
            enemy_hits = pygame.sprite.spritecollide(fireball, self.enemies, False)
            for enemy in enemy_hits:
                if enemy.is_alive:
                    enemy.stomp()
                    self.score += 100
                    fireball.kill()
        
        # Check enemy collision
        enemy_hits = pygame.sprite.spritecollide(self.mario, self.enemies, False)
        for enemy in enemy_hits:
            if enemy.is_alive and not enemy.squashed:
                # Check if stomping
                if self.mario.velocity_y > 0 and self.mario.rect.bottom < enemy.rect.centery:
                    enemy.stomp()
                    self.mario.velocity_y = -8  # Bounce
                    self.score += 100
                else:
                    # Hit by enemy - star power kills enemies
                    if self.mario.star_power:
                        enemy.stomp()
                        self.score += 100
                    elif self.mario.take_damage():
                        self.lives -= 1
                        self.reset_level()
        
        # Check flag
        if self.mario.rect.colliderect(self.flag.rect):
            self.level_complete()
        
        # Remove broken bricks
        for brick in list(self.bricks):
            if brick.broken:
                brick.kill()
                self.bricks.remove(brick)
                self.score += 50
        
        # Check lives
        if self.lives <= 0:
            self.game_over()
    
    def draw(self):
        """Draw everything"""
        # Sky
        self.screen.fill(SKY_BLUE)
        
        # Draw clouds
        for i in range(8):
            x = i * 400 - (self.camera.camera.x // 2) % 400
            y = 80 + (i % 3) * 40
            self.draw_cloud(x, y)
        
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # Draw HUD
        self.draw_hud()
        
        pygame.display.flip()
    
    def draw_cloud(self, x, y):
        """Draw a cloud"""
        pygame.draw.ellipse(self.screen, WHITE, (x, y, 60, 30))
        pygame.draw.ellipse(self.screen, WHITE, (x + 20, y - 10, 50, 35))
        pygame.draw.ellipse(self.screen, WHITE, (x + 45, y + 5, 40, 25))
    
    def draw_hud(self):
        """Draw the HUD"""
        # Score
        score_text = self.font.render(f"SCORE: {self.score:06d}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = self.font.render(f"COINS: {self.coins:02d}", True, WHITE)
        self.screen.blit(coin_text, (10, 40))
        
        # Lives with visual hearts/Mario icons
        lives_text = self.font.render(f"x {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (330, 10))
        
        # Draw Mario life icon
        life_icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        life_icon.fill((0, 0, 0, 0))
        # Mini Mario head
        pygame.draw.ellipse(life_icon, (220, 20, 20), (4, 2, 16, 10))  # Hat
        pygame.draw.ellipse(life_icon, (255, 220, 177), (6, 10, 12, 12))  # Face
        pygame.draw.circle(life_icon, BLACK, (10, 15), 1)  # Eye
        pygame.draw.circle(life_icon, BLACK, (14, 15), 1)  # Eye
        self.screen.blit(life_icon, (300, 8))
        
        # Time
        time_text = self.font.render(f"TIME: {self.time_left:03d}", True, WHITE)
        self.screen.blit(time_text, (600, 10))
        
        # World
        world_text = self.font.render("WORLD 1-1", True, WHITE)
        self.screen.blit(world_text, (300, 40))
        
        # Power-up indicators
        if self.mario.state == "fire":
            power_text = self.font.render("FIRE MARIO!", True, (255, 165, 0))
            self.screen.blit(power_text, (10, 70))
        elif self.mario.state == "super":
            power_text = self.font.render("SUPER MARIO!", True, (0, 255, 0))
            self.screen.blit(power_text, (10, 70))
        
        if self.mario.star_power:
            star_text = self.font.render("INVINCIBLE!", True, QUESTION_YELLOW)
            star_shadow = self.font.render("INVINCIBLE!", True, (255, 100, 0))
            self.screen.blit(star_shadow, (602, 42))
            self.screen.blit(star_text, (600, 40))
    
    def reset_level(self):
        """Reset level after death"""
        if self.lives > 0:
            self.mario.rect.x = 100
            self.mario.rect.y = 400
            self.mario.velocity_x = 0
            self.mario.velocity_y = 0
            self.mario.state = "small"
            self.mario.draw_mario()
            self.time_left = 400
    
    def level_complete(self):
        """Handle level completion"""
        self.screen.fill(BLACK)
        text = self.font.render("LEVEL COMPLETE!", True, WHITE)
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))
        
        pygame.display.flip()
        pygame.time.wait(3000)
        self.running = False
    
    def game_over(self):
        """Handle game over"""
        self.screen.fill(BLACK)
        text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"FINAL SCORE: {self.score}", True, WHITE)
        restart_text = self.font.render("Press R to Restart or Q to Quit", True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 60))
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart
                        waiting = False
                    if event.key == pygame.K_q:
                        self.running = False
                        waiting = False
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
