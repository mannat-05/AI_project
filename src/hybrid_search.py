# src/hybrid_search.py

import heapq
from src.elastic_hash import ElasticHashSet

def manhattan_distance(a, b):
    """Heuristic function for grid-based search."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def hybrid_a_star_search(maze, start, goal):
    """
    A* Search that uses the ElasticHashSet for optimal state-tracking.
    Returns the optimal path and the number of nodes expanded.
    """
    rows, cols = len(maze), len(maze[0])
    frontier = []
    
    # heapq format: (f_score, tie_breaker, current_node, path)
    heapq.heappush(frontier, (0, 0, start, [start]))
    
    # Using our custom faster hash table to track visited nodes
    explored = ElasticHashSet(capacity=rows * cols)
    nodes_expanded = 0
    tie_breaker = 0 # To handle priority queue tie-breaks safely
    
    while frontier:
        f, _, current, path = heapq.heappop(frontier)
        
        if explored.contains(current):
            continue
            
        explored.add(current)
        nodes_expanded += 1
        
        if current == goal:
            return path, nodes_expanded
            
        # Explore neighbors (Up, Down, Left, Right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current[0] + dx, current[1] + dy
            
            # Check boundaries and obstacles (0 = free, 1 = wall)
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                neighbor = (nx, ny)
                if not explored.contains(neighbor):
                    g_cost = len(path) # Cost so far
                    h_cost = manhattan_distance(neighbor, goal) # Heuristic
                    f_cost = g_cost + h_cost
                    tie_breaker += 1
                    
                    heapq.heappush(frontier, (f_cost, tie_breaker, neighbor, path + [neighbor]))
                    
    return None, nodes_expanded # No path found