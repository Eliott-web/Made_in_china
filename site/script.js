const PICO_IP = "192.168.4.1";
const POLL_INTERVAL = 500;

const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const gameState = document.getElementById("game-state");
const scoreDisplay = document.getElementById("score-display");
const btnStart = document.getElementById("btn-start");
const btnReset = document.getElementById("btn-reset");

let pollTimer = null;
let score = 0;

function setStatus(state) {
    statusDot.className = "";
    if (state === "connected") {
        statusDot.classList.add("connected");
        statusText.textContent = "Connected";
    } else if (state === "error") {
        statusDot.classList.add("error");
        statusText.textContent = "Disconnected";
    } else {
        statusText.textContent = "Waiting";
    }
}

async function fetchData() {
    try {
        const res = await fetch(`http://${PICO_IP}/data`, { signal: AbortSignal.timeout(400) });
        const json = await res.json();
        setStatus("connected");
        updateCards(json);
    } catch {
        setStatus("error");
    }
}

function updateCards(json) {
    document.querySelectorAll(".data-card").forEach(card => {
        const key = card.dataset.key;
        if (key && json[key] !== undefined) {
            card.querySelector(".data-value").textContent = json[key];
        }
    });
}

function startGame() {
    score = 0;
    scoreDisplay.textContent = "0";
    gameState.textContent = "Running";
    btnStart.disabled = true;
    pollTimer = setInterval(fetchData, POLL_INTERVAL);
}

function resetGame() {
    clearInterval(pollTimer);
    score = 0;
    scoreDisplay.textContent = "—";
    gameState.textContent = "Waiting";
    btnStart.disabled = false;
    setStatus("idle");
    document.querySelectorAll(".data-value").forEach(el => el.textContent = "—");
}

btnStart.addEventListener("click", startGame);
btnReset.addEventListener("click", resetGame);
