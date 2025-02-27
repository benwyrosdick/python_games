import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (34, 139, 34)
CANNON_COLOR_1 = (105, 105, 105)   # Left cannon color
CANNON_COLOR_2 = (70, 130, 180)    # Right cannon color
PROJECTILE_COLOR = (255, 69, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Player Cannon Artillery")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

# Physics
gravity = 0.5

# Terrain generation parameters
TERRAIN_STEP = 1  # pixel step for terrain array
MIN_HEIGHT = HEIGHT - 200
MAX_HEIGHT = HEIGHT - 50

def generate_terrain():
    terrain = []
    # Start with a base height in the middle of our allowed range.
    height = (MIN_HEIGHT + MAX_HEIGHT) // 2
    for x in range(WIDTH):
        # Vary the height with a small random step
        height += random.randint(-1, 1)
        # Clamp the height
        height = max(MIN_HEIGHT, min(MAX_HEIGHT, height))
        terrain.append(height)
    return terrain

terrain = generate_terrain()

def draw_terrain(terrain):
    # Create a polygon for the terrain
    points = [(0, HEIGHT)]
    for x in range(WIDTH):
        points.append((x, terrain[x]))
    points.append((WIDTH - 1, HEIGHT))
    pygame.draw.polygon(screen, GROUND_COLOR, points)

class Cannon:
    def __init__(self, x, color):
        self.x = x
        self.y = terrain[int(x)]
        self.color = color
        self.angle = 45 if x < WIDTH // 2 else 135  # left cannon fires right, right cannon fires left
        self.power = 50
        self.length = 40
        self.radius = 15  # for drawing and collision
    
    def update_position(self):
        # Cannon sits on the terrain
        self.y = terrain[int(self.x)]
    
    def draw(self):
        self.update_position()
        # Calculate barrel end point
        rad_angle = math.radians(self.angle)
        end_x = self.x + self.length * math.cos(rad_angle)
        end_y = self.y - self.length * math.sin(rad_angle)
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 8)
        # Draw the base of the cannon
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def fire(self):
        # Start the projectile at the tip of the barrel
        rad_angle = math.radians(self.angle)
        start_x = self.x + self.length * math.cos(rad_angle)
        start_y = self.y - self.length * math.sin(rad_angle)
        # Velocity components (adjust factor to moderate speed)
        vel_x = self.power * math.cos(rad_angle) / 2.0
        vel_y = -self.power * math.sin(rad_angle) / 2.0
        return [start_x, start_y], [vel_x, vel_y]

# Create two cannons
cannon_left = Cannon(50, CANNON_COLOR_1)
cannon_right = Cannon(WIDTH - 50, CANNON_COLOR_2)
cannons = [cannon_left, cannon_right]

# Game state variables
current_player = 0  # 0 for left cannon, 1 for right cannon
projectile_active = False
projectile_pos = [0, 0]
projectile_vel = [0, 0]
game_over = False
winner = None

def update_projectile(pos, vel):
    # Update projectile position and velocity
    pos[0] += vel[0]
    pos[1] += vel[1]
    vel[1] += gravity  # gravity effect
    return pos, vel

def check_collision_with_terrain(pos):
    x = int(pos[0])
    if 0 <= x < WIDTH:
        if pos[1] >= terrain[x]:
            return True
    return False

def check_collision_with_cannon(pos, cannon):
    # Simple collision: if projectile is within cannon's radius
    dx = pos[0] - cannon.x
    dy = pos[1] - cannon.y
    distance = math.hypot(dx, dy)
    return distance <= cannon.radius

def draw_turn_info():
    info = f"Player {current_player + 1}'s turn"
    text = font.render(info, True, BLACK)
    screen.blit(text, (10, 10))
    # Also display current cannon's angle and power
    cannon = cannons[current_player]
    params = f"Angle: {cannon.angle}°  Power: {cannon.power}"
    text2 = font.render(params, True, BLACK)
    screen.blit(text2, (10, 30))

def show_winner(winner):
    text = big_font.render(f"Player {winner + 1} Wins!", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

while True:
    screen.fill(WHITE)
    draw_terrain(terrain)
    
    # Draw both cannons
    for cannon in cannons:
        cannon.draw()
    
    # Draw turn info (if game is not over)
    if not game_over:
        draw_turn_info()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if not game_over and event.type == pygame.KEYDOWN:
            cannon = cannons[current_player]
            # Adjust cannon parameters (controls vary by current player's side)
            if event.key == pygame.K_UP:
                # Increase angle (cap angle based on side)
                if current_player == 0:
                    cannon.angle = min(cannon.angle + 2, 90)
                else:
                    cannon.angle = min(cannon.angle + 2, 180)
            elif event.key == pygame.K_DOWN:
                if current_player == 0:
                    cannon.angle = max(cannon.angle - 2, 0)
                else:
                    cannon.angle = max(cannon.angle - 2, 90)
            elif event.key == pygame.K_RIGHT:
                cannon.power = min(cannon.power + 2, 100)
            elif event.key == pygame.K_LEFT:
                cannon.power = max(cannon.power - 2, 10)
            elif event.key == pygame.K_SPACE and not projectile_active:
                # Fire projectile from current player's cannon
                projectile_pos, projectile_vel = cannon.fire()
                projectile_active = True

    # Update and draw projectile if one is active
    if projectile_active:
        projectile_pos, projectile_vel = update_projectile(projectile_pos, projectile_vel)
        pygame.draw.circle(screen, PROJECTILE_COLOR, (int(projectile_pos[0]), int(projectile_pos[1])), 5)
        
        # Check for collision with terrain
        if check_collision_with_terrain(projectile_pos):
            projectile_active = False
            # Switch turn if no hit
            current_player = 1 - current_player
        
        # Check for collision with the opponent cannon
        opponent = cannons[1 - current_player]
        if check_collision_with_cannon(projectile_pos, opponent):
            projectile_active = False
            game_over = True
            winner = current_player

        # If projectile goes off screen, end turn
        if projectile_pos[0] < 0 or projectile_pos[0] > WIDTH or projectile_pos[1] > HEIGHT:
            projectile_active = False
            current_player = 1 - current_player

    pygame.display.flip()
    clock.tick(60)
    
    # If game over, show winner and then exit
    if game_over:
        show_winner(winner)
        pygame.quit()
        sys.exit()
