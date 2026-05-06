import pygame 
import sys
import time

def visualize_maze_gui(maze, path=None):
    """
    Opens a Pygame window to draw the maze and animate the agent's path.
    """
    pygame.init()
    
    rows = len(maze)
    cols = len(maze[0])
    
    # Calculate cell sizes based on a fixed window resolution
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    cell_w = WINDOW_WIDTH // cols
    cell_h = WINDOW_HEIGHT // rows
    
    # Colors (RGB)
    COLOR_BG = (240, 240, 240)      # Light gray for open paths
    COLOR_WALL = (40, 40, 40)       # Dark gray for walls
    COLOR_PATH = (46, 204, 113)     # Emerald green for the AI path
    COLOR_START = (52, 152, 219)    # Blue for Start
    COLOR_GOAL = (231, 76, 60)      # Red for Goal
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hybrid Search Algorithm Simulation")
    
    # Draw the static maze
    screen.fill(COLOR_BG)
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 1:
                pygame.draw.rect(screen, COLOR_WALL, (c * cell_w, r * cell_h, cell_w, cell_h))
                
    # Draw Start and Goal distinctively
    pygame.draw.rect(screen, COLOR_START, (0, 0, cell_w, cell_h))
    pygame.draw.rect(screen, COLOR_GOAL, ((cols-1) * cell_w, (rows-1) * cell_h, cell_w, cell_h))
    
    # Draw a grid to make it look like a map
    for r in range(rows):
        pygame.draw.line(screen, (200, 200, 200), (0, r * cell_h), (WINDOW_WIDTH, r * cell_h))
    for c in range(cols):
        pygame.draw.line(screen, (200, 200, 200), (c * cell_w, 0), (c * cell_w, WINDOW_HEIGHT))

    pygame.display.flip()
    
    # Animate the path if one was found
    if path:
        for node in path:
            # Allow the user to close the window during animation without crashing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            r, c = node
            # Don't overwrite the Start and Goal colors
            if node != (0, 0) and node != (rows-1, cols-1):
                # Draw the path block slightly smaller than the cell for a cool trail effect
                pygame.draw.rect(screen, COLOR_PATH, (c * cell_w + 2, r * cell_h + 2, cell_w - 4, cell_h - 4))
                pygame.display.flip()
                time.sleep(0.03)  # Delay to create the animation effect
                
    # Keep the window open until the user clicks the X
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()