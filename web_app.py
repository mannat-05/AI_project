from flask import Flask, render_template, request, jsonify
import time
from web.solver import MazeFactory, hybrid_elastic_search

app = Flask(__name__, template_folder="templates", static_folder="static")


def compute_metrics(path, nodes_expanded, time_taken):
    if path is None:
        return {
            "status": "failed",
            "nodes_expanded": nodes_expanded,
            "time_taken": round(time_taken, 5),
            "distance": None,
            "turns": None,
            "score": 0,
        }

    distance = 0.0
    turns = 0

    for i in range(1, len(path)):
        prev, curr = path[i - 1], path[i]
        dx = abs(curr[0] - prev[0])
        dy = abs(curr[1] - prev[1])
        distance += 1.414 if dx == 1 and dy == 1 else 1.0

    for i in range(1, len(path) - 1):
        prev, curr, nxt = path[i - 1], path[i], path[i + 1]
        dir1 = (curr[0] - prev[0], curr[1] - prev[1])
        dir2 = (nxt[0] - curr[0], nxt[1] - curr[1])
        if dir1 != dir2:
            turns += 1

    base_score = 1500
    distance_penalty = distance * 10
    turn_penalty = turns * 15
    memory_penalty = nodes_expanded * 0.1
    score = max(0, base_score - distance_penalty - turn_penalty - memory_penalty)

    return {
        "status": "solved",
        "nodes_expanded": nodes_expanded,
        "time_taken": round(time_taken, 5),
        "distance": round(distance, 3),
        "turns": turns,
        "score": round(score, 1),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


@app.route("/api/solve", methods=["GET"])
def solve_maze():
    try:
        rows = int(request.args.get("rows", 20))
        cols = int(request.args.get("cols", 20))
        mode = request.args.get("mode", "random")
        density = float(request.args.get("density", 0.25))
    except ValueError:
        return jsonify({"error": "Invalid query parameters."}), 400

    if rows < 5 or cols < 5 or rows > 60 or cols > 60:
        return jsonify({"error": "Rows and cols must be between 5 and 60."}), 400

    if density < 0 or density > 0.75:
        return jsonify({"error": "Density must be between 0 and 0.75."}), 400

    if mode == "structured":
        maze, rows, cols = MazeFactory.create_structured(rows, cols)
    else:
        maze = MazeFactory.create_scattered(rows, cols, (0, 0), (rows - 1, cols - 1), density=density)

    start = (0, 0)
    goal = (rows - 1, cols - 1)

    start_time = time.time()
    path, nodes_expanded = hybrid_elastic_search(maze, start, goal)
    time_taken = time.time() - start_time

    metrics = compute_metrics(path, nodes_expanded, time_taken)

    return jsonify({
        "rows": rows,
        "cols": cols,
        "maze": maze,
        "path": path if path is not None else [],
        "metrics": metrics,
    })


if __name__ == "__main__":
    app.run(debug=True)
