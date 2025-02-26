import pygame
import sys
import numpy as np

# --- Configuration ---
CELL_SIZE = 10
GRID_WIDTH = 80
GRID_HEIGHT = 60
SCOREBOARD_HEIGHT = 40  # Extra space at the top for the scoreboard
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + SCOREBOARD_HEIGHT
FPS = 10

# Colors (R, G, B)
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GRAY    = (50, 50, 50)
GREEN   = (0, 255, 0)
RED     = (200, 0, 0)

# --- Helper Functions ---
def random_grid():
    """Initialize a grid with a random state (0 or 1) for each cell."""
    return np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])

def update_grid(grid):
    """Compute the next generation for Conway's Game of Life."""
    new_grid = grid.copy()
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            # Count the number of alive neighbors with wrap-around (toroidal grid)
            total = (
                grid[(i-1) % GRID_HEIGHT, (j-1) % GRID_WIDTH] +
                grid[(i-1) % GRID_HEIGHT, j] +
                grid[(i-1) % GRID_HEIGHT, (j+1) % GRID_WIDTH] +
                grid[i, (j-1) % GRID_WIDTH] +
                grid[i, (j+1) % GRID_WIDTH] +
                grid[(i+1) % GRID_HEIGHT, (j-1) % GRID_WIDTH] +
                grid[(i+1) % GRID_HEIGHT, j] +
                grid[(i+1) % GRID_HEIGHT, (j+1) % GRID_WIDTH]
            )
            # Apply Conway's rules
            if grid[i, j] == 1:
                if total < 2 or total > 3:
                    new_grid[i, j] = 0  # Cell dies
            else:
                if total == 3:
                    new_grid[i, j] = 1  # Cell becomes alive
    return new_grid

def reset_game():
    """Reinitialize game state."""
    grid = random_grid()
    generation = 0
    return grid, generation

# --- Main Game Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # Create restart button properties
    button_width, button_height = 150, 40
    button_rect = pygame.Rect(
        (WINDOW_WIDTH - button_width) // 2,
        (WINDOW_HEIGHT - button_height) // 2,
        button_width,
        button_height
    )

    # Initialize game state
    grid, generation = reset_game()
    paused = False  # Use pause to allow restarting or examine a state

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Toggle pause with space bar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

            # Check for mouse click on Restart button when paused
            if paused and event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    grid, generation = reset_game()
                    paused = False

        # Only update the grid if not paused
        if not paused:
            grid = update_grid(grid)
            generation += 1

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw scoreboard background
        scoreboard_rect = pygame.Rect(0, 0, WINDOW_WIDTH, SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, GRAY, scoreboard_rect)

        # Render generation counter on scoreboard
        gen_text = font.render(f"Generation: {generation}", True, WHITE)
        screen.blit(gen_text, (10, 10))

        # Draw playing area (grid area)
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                cell_value = grid[i, j]
                color = GREEN if cell_value == 1 else BLACK
                cell_rect = pygame.Rect(
                    j * CELL_SIZE,
                    i * CELL_SIZE + SCOREBOARD_HEIGHT,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(screen, color, cell_rect)

        # Optionally draw grid lines for clarity
        for i in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE + SCOREBOARD_HEIGHT), (WINDOW_WIDTH, i * CELL_SIZE + SCOREBOARD_HEIGHT))
        for j in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, GRAY, (j * CELL_SIZE, SCOREBOARD_HEIGHT), (j * CELL_SIZE, WINDOW_HEIGHT))

        # If paused, display a Restart button overlay
        if paused:
            # Dim the screen slightly
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            pause_text = font.render("Paused", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(pause_text, pause_rect)

            pygame.draw.rect(screen, RED, button_rect)
            restart_text = font.render("Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=button_rect.center)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
