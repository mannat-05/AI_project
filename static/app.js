const generateButton = document.getElementById("generateButton");
const mazeCanvas = document.getElementById("mazeCanvas");
const densityInput = document.getElementById("density");
const densityValue = document.getElementById("densityValue");
const resultsModal = document.getElementById("resultsModal");
const modalOverlay = document.getElementById("modalOverlay");

function updateDensityLabel() {
    densityValue.textContent = Number(densityInput.value).toFixed(2);
}

function openModal() {
    resultsModal.classList.add("active");
    modalOverlay.classList.add("active");
}

function closeModal() {
    resultsModal.classList.remove("active");
    modalOverlay.classList.remove("active");
}

function drawMaze(maze, path) {
    const rows = maze.length;
    const cols = maze[0].length;
    const ctx = mazeCanvas.getContext("2d");
    const padding = 10;
    const maxSize = Math.min(window.innerWidth - 80, 760);
    mazeCanvas.width = Math.min(maxSize, cols * 28) + padding * 2;
    mazeCanvas.height = Math.min(maxSize, rows * 28) + padding * 2;

    const cellWidth = (mazeCanvas.width - padding * 2) / cols;
    const cellHeight = (mazeCanvas.height - padding * 2) / rows;

    ctx.fillStyle = "#f8f6f3";
    ctx.fillRect(0, 0, mazeCanvas.width, mazeCanvas.height);

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (maze[r][c] === 1) {
                ctx.fillStyle = "#5a5a5a";
            } else {
                ctx.fillStyle = "#e8dcc8";
            }
            ctx.fillRect(padding + c * cellWidth, padding + r * cellHeight, cellWidth, cellHeight);
        }
    }

    ctx.fillStyle = "#a68a64";
    ctx.fillRect(padding, padding, cellWidth, cellHeight);
    ctx.fillStyle = "#7ba9a0";
    ctx.fillRect(padding + (cols - 1) * cellWidth, padding + (rows - 1) * cellHeight, cellWidth, cellHeight);

    if (path && path.length > 0) {
        ctx.fillStyle = "rgba(121, 169, 160, 0.6)";
        path.forEach(([r, c]) => {
            if ((r === 0 && c === 0) || (r === rows - 1 && c === cols - 1)) return;
            ctx.fillRect(padding + c * cellWidth + 2, padding + r * cellHeight + 2, cellWidth - 4, cellHeight - 4);
        });
    }

    ctx.strokeStyle = "rgba(166, 138, 100, 0.2)";
    for (let r = 0; r <= rows; r++) {
        ctx.beginPath();
        ctx.moveTo(padding, padding + r * cellHeight);
        ctx.lineTo(padding + cols * cellWidth, padding + r * cellHeight);
        ctx.stroke();
    }
    for (let c = 0; c <= cols; c++) {
        ctx.beginPath();
        ctx.moveTo(padding + c * cellWidth, padding);
        ctx.lineTo(padding + c * cellWidth, padding + rows * cellHeight);
        ctx.stroke();
    }
}

function renderMetricsModal(metrics) {
    const modalMetrics = document.getElementById("modalMetrics");
    
    if (metrics.status === "failed") {
        modalMetrics.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 32px;">
                <div style="font-size: 3rem; margin-bottom: 16px;">⚠️</div>
                <h3 style="color: #3a3a3a; margin: 0 0 8px 0;">No path found</h3>
                <p style="color: #6b6b6b;">The maze appears to be unsolvable. Try adjusting the obstacle density.</p>
            </div>
        `;
        return;
    }

    const scorePercent = Math.round((metrics.score / 1500) * 100);
    const scoreColor = scorePercent > 60 ? "#7ba9a0" : scorePercent > 40 ? "#c9ad8e" : "#a86b5b";
    const scoreRGB = scoreColor === "#7ba9a0" ? "123, 169, 160" : scoreColor === "#c9ad8e" ? "201, 173, 142" : "168, 107, 91";

    modalMetrics.innerHTML = `
        <div class="metric-card">
            <div class="metric-label">Status</div>
            <div class="metric-value">✓</div>
            <div class="metric-unit">Solved</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Distance</div>
            <div class="metric-value">${metrics.distance}</div>
            <div class="metric-unit">units</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Turns</div>
            <div class="metric-value">${metrics.turns}</div>
            <div class="metric-unit">actions</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Nodes Expanded</div>
            <div class="metric-value">${metrics.nodes_expanded}</div>
            <div class="metric-unit">states</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Execution Time</div>
            <div class="metric-value">${metrics.time_taken}</div>
            <div class="metric-unit">sec</div>
        </div>
        <div class="metric-card" style="background: linear-gradient(135deg, rgba(${scoreRGB}, 0.15), rgba(${scoreRGB}, 0.05)); border: 2px solid ${scoreColor};">
            <div class="metric-label">Elastic Score</div>
            <div class="metric-value" style="color: ${scoreColor};">${metrics.score.toFixed(0)}</div>
            <div class="metric-unit">/ 1500 (${scorePercent}%)</div>
        </div>
    `;
}

async function solveMaze() {
    const mode = document.getElementById("mazeMode").value;
    const rows = document.getElementById("rows").value;
    const cols = document.getElementById("cols").value;
    const density = document.getElementById("density").value;

    generateButton.disabled = true;
    generateButton.textContent = "Solving...";

    const params = new URLSearchParams({ mode, rows, cols, density });
    try {
        const response = await fetch(`/api/solve?${params.toString()}`);
        const data = await response.json();

        if (!response.ok) {
            alert(`Error: ${data.error || 'Unable to solve maze.'}`);
            return;
        }

        drawMaze(data.maze, data.path);
        renderMetricsModal(data.metrics);
        openModal();
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to solve maze. Please try again.");
    } finally {
        generateButton.disabled = false;
        generateButton.textContent = "Generate & Solve";
    }
}

function downloadResults() {
    const modalMetrics = document.getElementById("modalMetrics");
    const text = modalMetrics.innerText;
    const element = document.createElement("a");
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
    element.setAttribute("download", "maze-results.txt");
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

generateButton.addEventListener("click", solveMaze);
densityInput.addEventListener("input", updateDensityLabel);
window.addEventListener("load", updateDensityLabel);
window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
});
