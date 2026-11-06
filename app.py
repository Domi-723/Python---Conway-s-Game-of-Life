import streamlit as st

st.set_page_config(page_title="Conway's Game of Life", page_icon="🧬", layout="centered")

st.title("Conway's Game of Life (50x50)")
st.write("Interaktivní Hra života s podporou dotyku na mobilu i myši na PC.")

# HTML/JS komponenta pro plynulou 60fps simulaci v mřížce 50x50
game_code = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        #controls {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
            justify-content: center;
        }
        button, select {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
        }
        button:hover { background-color: #2563eb; }
        button#clear { background-color: #ef4444; }
        button#clear:hover { background-color: #dc2626; }
        select { background-color: #1e293b; border: 1px solid #475569; }

        .board-container {
            width: 100%;
            max-width: 450px;
            aspect-ratio: 1;
            background: #1e293b;
            border: 2px solid #334155;
            border-radius: 8px;
            overflow: hidden;
            touch-action: none;
        }
        canvas { width: 100%; height: 100%; display: block; }
        .stats { margin-top: 10px; font-size: 0.85rem; color: #94a3b8; }
    </style>
</head>
<body>
    <div id="controls">
        <button id="startBtn">Start</button>
        <button id="stepBtn">Krok</button>
        <button id="clear">Vymazat</button>
        <button id="randomBtn">Náhodně</button>
        <select id="presetSelect">
            <option value="">-- Vzory --</option>
            <option value="glider">Kluzák (Glider)</option>
            <option value="gosper">Gosperův pistolník</option>
        </select>
    </div>

    <div class="board-container">
        <canvas id="gameCanvas"></canvas>
    </div>

    <div class="stats">Živé buňky: <span id="aliveCount">0</span> | Generace: <span id="genCount">0</span></div>

    <script>
        const ROWS = 50;
        const COLS = 50;
        let grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
        let running = false;
        let generation = 0;
        let timer = null;

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
            draw();
        }
        window.addEventListener('resize', resizeCanvas);

        function countAlive() {
            return grid.flat().reduce((a, b) => a + b, 0);
        }

        function draw() {
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const cellW = canvas.width / COLS;
            const cellH = canvas.height / ROWS;

            ctx.fillStyle = '#38bdf8';
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    if (grid[r][c] === 1) {
                        ctx.fillRect(c * cellW + 0.5, r * cellH + 0.5, cellW - 1, cellH - 1);
                    }
                }
            }
            document.getElementById('aliveCount').innerText = countAlive();
            document.getElementById('genCount').innerText = generation;
        }

        function computeNextGen() {
            let next = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    let neighbors = 0;
                    for (let dr = -1; dr <= 1; dr++) {
                        for (let dc = -1; dc <= 1; dc++) {
                            if (dr === 0 && dc === 0) continue;
                            let nr = r + dr;
                            let nc = c + dc;
                            if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) {
                                neighbors += grid[nr][nc];
                            }
                        }
                    }
                    if (grid[r][c] === 1 && (neighbors === 2 || neighbors === 3)) {
                        next[r][c] = 1;
                    } else if (grid[r][c] === 0 && neighbors === 3) {
                        next[r][c] = 1;
                    }
                }
            }
            grid = next;
            generation++;
        }

        function update() {
            if (!running) return;
            computeNextGen();
            draw();
            timer = setTimeout(() => requestAnimationFrame(update), 100);
        }

        let isDrawing = false;
        function handleInteraction(e) {
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            
            const x = clientX - rect.left;
            const y = clientY - rect.top;

            const c = Math.floor((x / rect.width) * COLS);
            const r = Math.floor((y / rect.height) * ROWS);

            if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
                grid[r][c] = 1;
                draw();
            }
        }

        canvas.addEventListener('mousedown', (e) => { isDrawing = true; handleInteraction(e); });
        window.addEventListener('mouseup', () => isDrawing = false);
        canvas.addEventListener('mousemove', (e) => { if (isDrawing) handleInteraction(e); });

        canvas.addEventListener('touchstart', (e) => { isDrawing = true; handleInteraction(e); e.preventDefault(); });
        window.addEventListener('touchend', () => isDrawing = false);
        canvas.addEventListener('touchmove', (e) => { if (isDrawing) handleInteraction(e); e.preventDefault(); });

        const startBtn = document.getElementById('startBtn');
        startBtn.addEventListener('click', () => {
            running = !running;
            startBtn.innerText = running ? 'Pauza' : 'Start';
            startBtn.style.backgroundColor = running ? '#eab308' : '#3b82f6';
            if (running) update();
        });

        document.getElementById('stepBtn').addEventListener('click', () => {
            if (!running) {
                computeNextGen();
                draw();
            }
        });

        document.getElementById('clear').addEventListener('click', () => {
            running = false;
            startBtn.innerText = 'Start';
            startBtn.style.backgroundColor = '#3b82f6';
            grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
            generation = 0;
            draw();
        });

        document.getElementById('randomBtn').addEventListener('click', () => {
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    grid[r][c] = Math.random() > 0.8 ? 1 : 0;
                }
            }
            generation = 0;
            draw();
        });

        document.getElementById('presetSelect').addEventListener('change', (e) => {
            grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
            generation = 0;
            const val = e.target.value;
            if (val === 'glider') {
                grid[1][2] = 1; grid[2][3] = 1; grid[3][1] = 1; grid[3][2] = 1; grid[3][3] = 1;
            } else if (val === 'gosper') {
                const p = [[5,1],[5,2],[6,1],[6,2],[5,11],[6,11],[7,11],[4,12],[8,12],[3,13],[9,13],[3,14],[9,14],[6,15],[4,16],[8,16],[5,17],[6,17],[7,17],[6,18],[3,21],[4,21],[5,21],[3,22],[4,22],[5,22],[2,23],[6,23],[1,25],[2,25],[6,25],[7,25],[3,35],[4,35],[3,36],[4,36]];
                p.forEach(([r, c]) => { if(r+5 < ROWS && c+5 < COLS) grid[r+5][c+5] = 1; });
            }
            draw();
            e.target.value = "";
        });

        resizeCanvas();
    </script>
</body>
</html>
"""

st.components.v1.html(game_code, height=580)