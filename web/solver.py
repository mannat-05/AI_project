import heapq
import random
from collections import deque
from src.elastic_hash import ElasticHashSet


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
        (-1, 0, 1.0),
        (1, 0, 1.0),
        (0, -1, 1.0),
        (0, 1, 1.0),
        (-1, -1, 1.414),
        (-1, 1, 1.414),
        (1, -1, 1.414),
        (1, 1, 1.414),
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
                    if maze[current_pos[0] + dx][current_pos[1]] == 1 or maze[current_pos[0]][current_pos[1] + dy] == 1:
                        continue

                new_state = ((nx, ny), new_dir)
                if not explored.contains(new_state):
                    turn_cost = turn_penalty if (current_dir != (0, 0) and current_dir != new_dir) else 0
                    new_g = current_g + step_cost + turn_cost
                    h_cost = octile_distance((nx, ny), goal)
                    f_cost = new_g + h_cost
                    tie_breaker += 1
                    heapq.heappush(frontier, (f_cost, tie_breaker, new_g, new_state, path + [(nx, ny)]))

    return None, nodes_expanded


class MazeFactory:
    @staticmethod
    def _is_solvable_8way(maze, start, goal):
        rows, cols = len(maze), len(maze[0])
        queue = deque([start])
        visited = set([start])
        movements = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                return True
            for dx, dy in movements:
                nr, nc = r + dx, c + dy
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                    if abs(dx) == 1 and abs(dy) == 1:
                        if maze[r + dx][c] == 1 or maze[r][c + dy] == 1:
                            continue
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    @staticmethod
    def create_scattered(rows, cols, start, goal, density=0.3):
        while True:
            maze = [[0 for _ in range(cols)] for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    if random.random() < density:
                        maze[r][c] = 1
            maze[start[0]][start[1]] = 0
            maze[goal[0]][goal[1]] = 0
            if MazeFactory._is_solvable_8way(maze, start, goal):
                return maze

    @staticmethod
    def create_structured(rows, cols):
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1
        maze = [[1 for _ in range(cols)] for _ in range(rows)]

        def carve_passages_from(r, c):
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1:
                    maze[r + dr // 2][c + dc // 2] = 0
                    maze[nr][nc] = 0
                    carve_passages_from(nr, nc)

        maze[0][0] = 0
        carve_passages_from(0, 0)
        num_loops = (rows * cols) // 15
        for _ in range(num_loops):
            r = random.randint(1, rows - 2)
            c = random.randint(1, cols - 2)
            maze[r][c] = 0
        maze[rows - 1][cols - 1] = 0
        return maze, rows, cols
