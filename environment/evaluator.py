# environment/evaluator.py

class AgentEvaluator:
    """
    Evaluates the algorithm's performance similar to UC Berkeley's CS188 Pacman.
    Score = Base Points - (Path Cost * Penalty) - (Nodes Expanded * Penalty)
    """
    @staticmethod
    def evaluate(path, nodes_expanded, time_taken):
        print("\n" + "="*40)
        print("🤖 PERFORMANCE EVALUATION")
        print("="*40)
        
        if path is None:
            print("Status: FAILED (No path found)")
            print("Score: 0")
            return
            
        path_cost = len(path) - 1 # Start node doesn't cost a step
        
        # Scoring logic: High base score, penalized for inefficient paths and too much memory/expansion
        base_score = 1000
        cost_penalty = path_cost * 2
        expansion_penalty = nodes_expanded * 0.5
        final_score = base_score - cost_penalty - expansion_penalty
        
        print(f"Path Length (Cost): {path_cost}")
        print(f"Nodes Expanded (Memory/Time usage): {nodes_expanded}")
        print(f"Execution Time: {time_taken:.5f} seconds")
        print("-" * 40)
        print(f"FINAL SCORE: {max(0, final_score):.1f} / 1000")
        print("="*40 + "\n")