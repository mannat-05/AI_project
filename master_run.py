import heapq
import random
import time
import pygame
import sys
from collections import deque

# ==========================================
# 1. ADVANCED HASHING (THE CORE INNOVATION)
# ==========================================
class ElasticHashSet:
    def __init__(self, capacity=10000):
        self.layer1 = [None] * capacity
        self.layer2 = [None] * (capacity // 2)
        self.layer3 = [None] * (capacity // 4)
        self.layers = [self.layer1, self.layer2, self.layer3]
        
    def _hash(self, item, layer_size, seed=0):
        return (hash(item) + seed) % layer_size

    def add(self, item):
        for i, layer in enumerate(self.layers):
            idx = self._hash(item, len(layer), seed=i)
            for probe in range(3): 
                probe_idx = (idx + probe) % len(layer)
                if layer[probe_idx] is None or layer[probe_idx] == item:
                    layer[probe_idx] = item
                    return
        self.layers[-1].append(item) 

    def contains(self, item):
        for i, layer in enumerate(self.layers):
            idx = self._hash(item, len(layer), seed=i)
            for probe in range(3):
                probe_idx = (idx + probe) % len(layer)
                if layer[probe_idx] == item:
                    return True
                if layer[probe_idx] is None:
                    break 
        return item in self.layers[-1]

# ==========================================
# 2. HYBRID ELASTIC-A* SEARCH ALGORITHM
# ==========================================
def octile_distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (1.414 - 1) * min(dx, dy)

def hybrid_elastic_search(maze, start, goal, turn_penalty=2.5):
    rows, cols = len(maze), len(maze[0])
    frontier = []
    
    start_state = (start, (0, 0)) 
    heapq.heappush(frontier, (0, 0, 0, start_state, [start]))
    
    explored = ElasticHashSet(capacity=rows * cols * 8) 
    nodes_expanded = 0
    tie_breaker = 0 
    
    movements = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),           # Orthogonal
        (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)  # Diagonal
    ]
    
    while frontier:
        f, _, current_g, current_state, path = heapq.heappop(frontier)
        current_pos, current_dir = current_state
        
        if explored.contains(current_state):
            continue
            
        explored.add(current_state)
        nodes_expanded += 1
        
        if current_pos == goal:
            return path, nodes_expanded
            
        for dx, dy, step_cost in movements:
            nx, ny = current_pos[0] + dx, current_pos[1] + dy
            new_dir = (dx, dy)
            
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                if step_cost > 1.0: 
                    if maze[current_pos[0]+dx][current_pos[1]] == 1 or maze[current_pos[0]][current_pos[1]+dy] == 1:
                        continue 
                
                new_state = ((nx, ny), new_dir)
                
                if not explored.contains(new_state):
                    turn_cost = turn_penalty if (current_dir != (0,0) and current_dir != new_dir) else 0
                        
                    new_g = current_g + step_cost + turn_cost
                    h_cost = octile_distance((nx, ny), goal) 
                    f_cost = new_g + h_cost
                    tie_breaker += 1
                    
                    heapq.heappush(frontier, (f_cost, tie_breaker, new_g, new_state, path + [(nx, ny)]))
                    
    return None, nodes_expanded 

# ==========================================
# 3. ADAPTABLE MAZE FACTORY
# ==========================================
class MazeFactory:
    """
    Generates different topologies to test the generalizability of the AI.
    """
    @staticmethod
    def _is_solvable_8way(maze, start, goal):
        rows, cols = len(maze), len(maze[0])
        queue = deque([start])
        visited = set([start])
        movements = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        
        while queue:
            r, c = queue.popleft()
            if (r, c) == goal: return True
            for dx, dy in movements:
                nr, nc = r + dx, c + dy
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                    if abs(dx) == 1 and abs(dy) == 1: 
                        if maze[r+dx][c] == 1 or maze[r][c+dy] == 1: continue 
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    @staticmethod
    def create_scattered(rows, cols, start, goal, density=0.3):
        """Creates an open environment with random obstacles (e.g., Drone in a forest)."""
        while True:
            maze = [[0 for _ in range(cols)] for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    if random.random() < density: maze[r][c] = 1
            maze[start[0]][start[1]] = 0
            maze[goal[0]][goal[1]] = 0
            if MazeFactory._is_solvable_8way(maze, start, goal):
                return maze

    @staticmethod
    def create_structured(rows, cols):
        """Creates structured corridors (e.g., Micromouse competition)."""
        if rows % 2 == 0: rows += 1
        if cols % 2 == 0: cols += 1
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        
        def carve_passages_from(r, c):
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1:
                    maze[r + dr//2][c + dc//2] = 0 
                    maze[nr][nc] = 0               
                    carve_passages_from(nr, nc)
                    
        maze[0][0] = 0
        carve_passages_from(0, 0)
        
        num_loops = (rows * cols) // 15
        for _ in range(num_loops):
            r, c = random.randint(1, rows-2), random.randint(1, cols-2)
            maze[r][c] = 0
            
        maze[rows-1][cols-1] = 0
        return maze, rows, cols

    @staticmethod
    def create_from_array(array_2d):
        """Allows loading a specific, hardcoded real-world floor plan."""
        return array_2d

def print_maze(maze, path=[]):
    for r in range(len(maze)):
        row_str = ""
        for c in range(len(maze[0])):
            if (r, c) in path:
                row_str += "\033[92m*\033[0m " 
            elif maze[r][c] == 1:
                row_str += "█ " 
            else:
                row_str += ". " 
        print(row_str)

# ==========================================
# 4. REAL-WORLD ALGORITHM EVALUATOR
# ==========================================
class AgentEvaluator:
    @staticmethod
    def count_turns(path):
        if len(path) < 3: return 0
        turns = 0
        for i in range(1, len(path) - 1):
            prev, curr, nxt = path[i-1], path[i], path[i+1]
            dir1 = (curr[0] - prev[0], curr[1] - prev[1])
            dir2 = (nxt[0] - curr[0], nxt[1] - curr[1])
            if dir1 != dir2: turns += 1
        return turns

    @staticmethod
    def calculate_distance(path):
        dist = 0
        for i in range(1, len(path)):
            prev, curr = path[i-1], path[i]
            dx, dy = abs(curr[0] - prev[0]), abs(curr[1] - prev[1])
            dist += 1.414 if (dx == 1 and dy == 1) else 1.0
        return dist

    @staticmethod
    def evaluate(path, nodes_expanded, time_taken):
        print("\n" + "="*50)
        print("🚀 ALGORITHM PERFORMANCE & REAL-WORLD METRICS")
        print("="*50)
        
        if path is None:
            print("Status: FAILED")
            return
            
        physical_distance = AgentEvaluator.calculate_distance(path)
        turn_count = AgentEvaluator.count_turns(path)
        
        base_score = 1500
        distance_penalty = physical_distance * 10
        turn_penalty = turn_count * 15         
        memory_penalty = nodes_expanded * 0.1  
        
        final_score = base_score - distance_penalty - turn_penalty - memory_penalty
        
        print(f"Total Physical Distance: {physical_distance:.2f} units")
        print(f"Mechanical Turns Made:   {turn_count} turns")
        print(f"States/Nodes Expanded:   {nodes_expanded} (Memory footprint)")
        print(f"Algorithm CPU Time:      {time_taken:.5f} sec")
        print("-" * 50)
        print(f"ELASTIC SEARCH SCORE:    {max(0, final_score):.1f} / 1500")
        print("="*50 + "\n")

# ==========================================
# 5. PYGAME VISUALIZER
# ==========================================
def visualize_maze_gui(maze, path=None):
    pygame.init()
    rows, cols = len(maze), len(maze[0])
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
    cell_w, cell_h = WINDOW_WIDTH // cols, WINDOW_HEIGHT // rows
    
    COLOR_BG, COLOR_WALL = (240, 240, 240), (40, 40, 40)
    COLOR_PATH, COLOR_START, COLOR_GOAL = (46, 204, 113), (52, 152, 219), (231, 76, 60)
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Elastic-A* Universal Maze Solver")
    
    screen.fill(COLOR_BG)
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 1:
                pygame.draw.rect(screen, COLOR_WALL, (c * cell_w, r * cell_h, cell_w, cell_h))
                
    pygame.draw.rect(screen, COLOR_START, (0, 0, cell_w, cell_h))
    pygame.draw.rect(screen, COLOR_GOAL, ((cols-1) * cell_w, (rows-1) * cell_h, cell_w, cell_h))
    
    for r in range(rows): pygame.draw.line(screen, (200, 200, 200), (0, r * cell_h), (WINDOW_WIDTH, r * cell_h))
    for c in range(cols): pygame.draw.line(screen, (200, 200, 200), (c * cell_w, 0), (c * cell_w, WINDOW_HEIGHT))
    pygame.display.flip()
    
    if path:
        for node in path:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            r, c = node
            if node != (0, 0) and node != (rows-1, cols-1):
                pygame.draw.circle(screen, COLOR_PATH, (c * cell_w + cell_w//2, r * cell_h + cell_h//2), min(cell_w, cell_h)//3)
                pygame.display.flip()
                time.sleep(0.04)  
                
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

# ==========================================
# 6. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    BASE_ROWS, BASE_COLS = 21, 41 
    START = (0, 0)
    
    # Interactive Menu
    print("\n" + "="*40)
    print("🤖 UNIVERSAL MAZE GENERATOR")
    print("="*40)
    print("1. Structured Corridors (Micromouse)")
    print("2. Scattered Obstacles (Open Environment)")
    print("3. Custom Array (Hardcoded Trap)")
    
    # Get user input with a simple validation loop
    while True:
        try:
            MAZE_TYPE_SELECTION = int(input("\nEnter the number of your choice (1-3): "))
            if MAZE_TYPE_SELECTION in [1, 2, 3]:
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Generate based on selection
    if MAZE_TYPE_SELECTION == 1:
        print("\nGenerating Structured Maze...")
        maze, ROWS, COLS = MazeFactory.create_structured(BASE_ROWS, BASE_COLS)
        GOAL = (ROWS - 1, COLS - 1)
        
    elif MAZE_TYPE_SELECTION == 2:
        print("\nGenerating Scattered Environment...")
        ROWS, COLS = BASE_ROWS, BASE_COLS
        GOAL = (ROWS - 1, COLS - 1)
        maze = MazeFactory.create_scattered(ROWS, COLS, START, GOAL, density=0.35)
        
    elif MAZE_TYPE_SELECTION == 3:
        print("\nLoading Custom U-Shaped Trap...")
        ROWS, COLS = 10, 10
        GOAL = (9, 9)
        custom_grid = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        ]
        maze = MazeFactory.create_from_array(custom_grid)

    print("\nRunning Elastic Hybrid Search...")
    start_time = time.time()
    
    path, nodes_expanded = hybrid_elastic_search(maze, START, GOAL, turn_penalty=3.0)
    
    end_time = time.time()
    
    if path: 
        print("\nOptimal Path Found.")
    else: 
        print("\nNo valid path exists.")
        
    AgentEvaluator.evaluate(path, nodes_expanded, end_time - start_time)
    
    print("Launching Pygame Simulation Window...")
    visualize_maze_gui(maze, path)