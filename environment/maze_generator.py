# environment/maze_generator.py

import random

def generate_random_maze(rows, cols, obstacle_density=0.25):
    """
    Generates a grid-based maze. 0 = Free, 1 = Wall.
    Ensures start (0,0) and goal (rows-1, cols-1) are free.
    """
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if random.random() < obstacle_density:
                maze[r][c] = 1
                
    # Guarantee start and end are clear of obstacles
    maze[0][0] = 0
    maze[rows-1][cols-1] = 0
    return maze

def print_maze(maze, path=[]):
    """
    Visualizes the maze and the path found by the algorithm in the terminal.
    """
    for r in range(len(maze)):
        row_str = ""
        for c in range(len(maze[0])):
            if (r, c) in path:
                row_str += "\033[92m*\033[0m " # Green asterisk for path
            elif maze[r][c] == 1:
                row_str += "█ " # Wall block
            else:
                row_str += ". " # Open space
        print(row_str)