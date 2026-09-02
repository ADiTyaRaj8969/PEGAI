(function () {
  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d");
  const scoreEl = document.getElementById("score");
  const bestEl = document.getElementById("best");
  const overlay = document.getElementById("overlay");
  const overlayTitle = document.getElementById("overlay-title");
  const overlayMsg = document.getElementById("overlay-msg");
  const startBtn = document.getElementById("start-btn");
  const speedSelect = document.getElementById("speed");

  const GRID_SIZE = 20;
  const TILE = canvas.width / GRID_SIZE;

  let snake, direction, nextDirection, food, score, best, tickMs, timer;
  let running = false;
  let paused = false;

  best = Number(localStorage.getItem("snake-best") || 0);
  bestEl.textContent = best;

  function resetState() {
    snake = [
      { x: 9, y: 10 },
      { x: 8, y: 10 },
      { x: 7, y: 10 },
    ];
    direction = { x: 1, y: 0 };
    nextDirection = { x: 1, y: 0 };
    score = 0;
    scoreEl.textContent = score;
    tickMs = Number(speedSelect.value);
    placeFood();
  }

  function placeFood() {
    let candidate;
    do {
      candidate = {
        x: Math.floor(Math.random() * GRID_SIZE),
        y: Math.floor(Math.random() * GRID_SIZE),
      };
    } while (snake.some((s) => s.x === candidate.x && s.y === candidate.y));
    food = candidate;
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // food
    ctx.fillStyle = "#ff6b6b";
    ctx.beginPath();
    const fx = food.x * TILE + TILE / 2;
    const fy = food.y * TILE + TILE / 2;
    ctx.arc(fx, fy, TILE / 2.4, 0, Math.PI * 2);
    ctx.fill();

    // snake
    snake.forEach((seg, i) => {
      const isHead = i === 0;
      ctx.fillStyle = isHead ? "#9dffb8" : "#7CFC9A";
      const pad = 1.5;
      ctx.fillRect(
        seg.x * TILE + pad,
        seg.y * TILE + pad,
        TILE - pad * 2,
        TILE - pad * 2
      );
    });
  }

  function step() {
    direction = nextDirection;
    const head = {
      x: snake[0].x + direction.x,
      y: snake[0].y + direction.y,
    };

    // wall collision
    if (
      head.x < 0 ||
      head.x >= GRID_SIZE ||
      head.y < 0 ||
      head.y >= GRID_SIZE
    ) {
      return gameOver();
    }

    // self collision
    if (snake.some((s) => s.x === head.x && s.y === head.y)) {
      return gameOver();
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
      score += 10;
      scoreEl.textContent = score;
      placeFood();
    } else {
      snake.pop();
    }

    draw();
  }

  function loop() {
    timer = setInterval(step, tickMs);
  }

  function stopLoop() {
    clearInterval(timer);
  }

  function gameOver() {
    stopLoop();
    running = false;
    if (score > best) {
      best = score;
      localStorage.setItem("snake-best", String(best));
      bestEl.textContent = best;
    }
    overlayTitle.textContent = "Game Over";
    overlayMsg.textContent = `Score: ${score} — Press Space or Start to try again`;
    startBtn.textContent = "Play Again";
    overlay.classList.remove("hidden");
  }

  function startGame() {
    resetState();
    draw();
    overlay.classList.add("hidden");
    running = true;
    paused = false;
    stopLoop();
    loop();
  }

  function togglePause() {
    if (!running) return;
    paused = !paused;
    if (paused) {
      stopLoop();
      overlayTitle.textContent = "Paused";
      overlayMsg.textContent = "Press Space to resume";
      startBtn.textContent = "Resume";
      overlay.classList.remove("hidden");
    } else {
      overlay.classList.add("hidden");
      loop();
    }
  }

  function setDirection(dx, dy) {
    // prevent reversing directly into itself
    if (snake.length > 1 && dx === -direction.x && dy === -direction.y) return;
    nextDirection = { x: dx, y: dy };
  }

  const KEY_MAP = {
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
    w: [0, -1],
    s: [0, 1],
    a: [-1, 0],
    d: [1, 0],
    W: [0, -1],
    S: [0, 1],
    A: [-1, 0],
    D: [1, 0],
  };

  window.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      e.preventDefault();
      if (!running && overlay.classList.contains("hidden") === false) {
        startGame();
      } else {
        togglePause();
      }
      return;
    }

    const mapped = KEY_MAP[e.key];
    if (mapped) {
      e.preventDefault();
      if (!running || paused) return;
      setDirection(mapped[0], mapped[1]);
    }
  });

  document.querySelectorAll(".mobile-controls button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!running || paused) return;
      const dir = btn.dataset.dir;
      if (dir === "up") setDirection(0, -1);
      if (dir === "down") setDirection(0, 1);
      if (dir === "left") setDirection(-1, 0);
      if (dir === "right") setDirection(1, 0);
    });
  });

  startBtn.addEventListener("click", startGame);

  speedSelect.addEventListener("change", () => {
    tickMs = Number(speedSelect.value);
    if (running && !paused) {
      stopLoop();
      loop();
    }
  });

  // initial paint
  resetState();
  draw();
})();
