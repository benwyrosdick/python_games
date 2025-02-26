import pygame
import sys
import random

# --- Configuration ---
CELL_SIZE = 20
GRID_WIDTH = 50
GRID_HEIGHT = 40
SCOREBOARD_HEIGHT = 40  # Extra space at the top for the scoreboard
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + SCOREBOARD_HEIGHT
FPS = 10

# Colors (R, G, B)
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (200, 0, 0)
GREEN   = (0, 200, 0)
BLUE    = (0, 0, 200)
YELLOW  = (200, 200, 0)
GRAY    = (50, 50, 50)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# --- Helper Functions ---
def get_random_position(exclude):
    """Return a random position on the grid not in the exclude set."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
            return pos

def add_tuples(a, b):
    return (a[0] + b[0], a[1] + b[1])

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# --- Snake Class ---
class Snake:
    def __init__(self, init_positions, color):
        self.positions = init_positions  # list of tuples, head is first element
        self.direction = random.choice(DIRECTIONS)
        self.color = color
        self.alive = True
        self.score = len(init_positions)  # starting score is initial length

    def get_head(self):
        return self.positions[0]

    def move(self, food, obstacles):
        if not self.alive:
            return

        best_direction = None
        best_distance = float('inf')

        # Try each direction and choose the one that minimizes distance to food
        random.shuffle(DIRECTIONS)  # randomize tie-breakers
        for d in DIRECTIONS:
            new_head = add_tuples(self.get_head(), d)
            # Check for wall collisions (board boundaries)
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
                continue
            # Check if new_head would hit obstacles (self or other snake segments)
            if new_head in obstacles:
                continue
            dist = manhattan_distance(new_head, food)
            if dist < best_distance:
                best_distance = dist
                best_direction = d

        # If no valid direction is found, try to continue in the current direction if possible
        if best_direction is None:
            new_head = add_tuples(self.get_head(), self.direction)
            if (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT and
                new_head not in obstacles):
                best_direction = self.direction
            else:
                # Snake is trapped
                self.alive = False
                return

        self.direction = best_direction
        new_head = add_tuples(self.get_head(), self.direction)
        self.positions.insert(0, new_head)

    def trim_tail(self):
        # Remove last segment (simulate movement)
        self.positions.pop()

    def check_self_collision(self):
        # Check if the head collides with its own body
        return self.get_head() in self.positions[1:]

# --- Main Game Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game with 2 Computer Controlled Snakes")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # Initialize snakes with different starting positions
    snake1 = Snake(init_positions=[(5, 5)], color=GREEN)
    snake2 = Snake(init_positions=[(GRID_WIDTH - 6, GRID_HEIGHT - 6)], color=BLUE)

    # Place initial food (avoid snake positions)
    occupied = set(snake1.positions + snake2.positions)
    food = get_random_position(occupied)

    running = True
    while running:
        clock.tick(FPS)

        # Process events (only allow quitting)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move snakes if they are alive
        for snake in (snake1, snake2):
            if snake.alive:
                # Build obstacles set from both snakes (all segments)
                obstacles = set(snake1.positions) | set(snake2.positions)
                # Exclude snake's current head from obstacles so it can move from there
                snake.move(food, obstacles - {snake.get_head()})

        # Check collisions for each snake
        for snake in (snake1, snake2):
            head = snake.get_head()
            # Wall collision
            if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
                snake.alive = False
            # Self collision
            if snake.check_self_collision():
                snake.alive = False

        # Check for snake collisions with the other snake
        if snake1.get_head() in snake2.positions:
            snake1.alive = False
        if snake2.get_head() in snake1.positions:
            snake2.alive = False

        # Check if any snake ate the food
        ate_food = False

        for snake in (snake1, snake2):
            if snake.alive and snake.get_head() == food:
                # Snake grows: do not trim tail this round and increase score
                snake.score += 1
                ate_food = snake
                # Place new food (avoid all snake segments)
                occupied = set(snake1.positions + snake2.positions)
                food = get_random_position(occupied)
                break  # Only one snake can eat the food per update

        # For snakes that did not eat, trim tail to simulate movement
        for snake in (snake1, snake2):
            if snake.alive and not (snake == ate_food):
                snake.trim_tail()

        # --- Drawing ---
        # Clear screen (fill with black)
        screen.fill(BLACK)

        # Draw scoreboard background
        scoreboard_rect = pygame.Rect(0, 0, WINDOW_WIDTH, SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, GRAY, scoreboard_rect)

        # Render scoreboard text
        score_text1 = font.render(f"Green Snake Score: {snake1.score}", True, WHITE)
        score_text2 = font.render(f"Blue Snake Score: {snake2.score}", True, WHITE)
        screen.blit(score_text1, (10, 5))
        screen.blit(score_text2, (WINDOW_WIDTH - score_text2.get_width() - 10, 5))

        # Draw playing area background (below scoreboard)
        play_area = pygame.Rect(0, SCOREBOARD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, BLACK, play_area)

        # Draw food (adjust y coordinate by SCOREBOARD_HEIGHT)
        food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE + SCOREBOARD_HEIGHT, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, YELLOW, food_rect)

        # Draw snakes (adjust y coordinate by SCOREBOARD_HEIGHT)
        for snake in (snake1, snake2):
            for pos in snake.positions:
                rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE + SCOREBOARD_HEIGHT, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, snake.color, rect)
            # Optionally, mark the head with a white border if alive
            if snake.alive:
                head_rect = pygame.Rect(snake.get_head()[0] * CELL_SIZE,
                                        snake.get_head()[1] * CELL_SIZE + SCOREBOARD_HEIGHT,
                                        CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, head_rect, 2)

        # If both snakes are dead, display Game Over message centered in the play area
        if not snake1.alive and not snake2.alive:
            game_over_text = font.render("Game Over!", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, (WINDOW_HEIGHT + SCOREBOARD_HEIGHT)//2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
