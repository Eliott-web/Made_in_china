const PICO_IP       = "192.168.4.1";
const POLL_INTERVAL = 500;

const statusDot        = document.getElementById("status-dot");
const statusText       = document.getElementById("status-text");
const gameState        = document.getElementById("game-state");
const scoreDisplay     = document.getElementById("score-display");
const btnStart         = document.getElementById("btn-start");
const btnStop          = document.getElementById("btn-stop");
const btnReset         = document.getElementById("btn-reset");
const selectJ1         = document.getElementById("select-j1");
const selectJ2         = document.getElementById("select-j2");
const inputRounds      = document.getElementById("input-rounds");
const inputProfileName = document.getElementById("input-profile-name");
const btnCreateProfile = document.getElementById("btn-create-profile");
const profileList      = document.getElementById("profile-list");
const highscoresBody   = document.getElementById("highscores-body");

let pollTimer    = null;
let activeJ1     = null;
let activeJ2     = null;
let activeRounds = 0;


// ─── API ─────────────────────────────────────────────────────────────────────

async function apiGet(path) {
    const res = await fetch(`http://${PICO_IP}${path}`, { signal: AbortSignal.timeout(2000) });
    return res.json();
}

async function apiPost(path, body = {}) {
    const res = await fetch(`http://${PICO_IP}${path}`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(body),
        signal:  AbortSignal.timeout(2000),
    });
    return res.json();
}


// ─── DATABASE (Pico) ─────────────────────────────────────────────────────────

async function dbGetAllProfiles() {
    const res = await apiGet("/db");
    return Object.values(res.profiles);
}

async function dbCreateProfile(name) {
    const res = await apiPost("/profile/create", { name });
    return res.ok;
}

async function dbDeleteProfile(name) {
    await apiPost("/profile/delete", { name });
}

async function dbUpdateStats(name, games_won, rounds_won, rounds_played) {
    await apiPost("/stats/update", { name, games_won, rounds_won, rounds_played });
}


// ─── NAVIGATION ──────────────────────────────────────────────────────────────

function showView(viewId) {
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(viewId).classList.add("active");
    document.querySelector(`.nav-btn[data-view="${viewId}"]`).classList.add("active");
    if (viewId === "view-profiles")   renderProfileList();
    if (viewId === "view-highscores") renderHighscores();
    if (viewId === "view-game")       renderProfileSelects();
}


// ─── STATUS ──────────────────────────────────────────────────────────────────

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


// ─── GAME ────────────────────────────────────────────────────────────────────

async function startGame() {
    const rounds = parseInt(inputRounds.value, 10);
    activeJ1     = selectJ1.value;
    activeJ2     = selectJ2.value;
    activeRounds = rounds;

    if (!activeJ1 || !activeJ2 || activeJ1 === activeJ2) return;

    try { await apiPost("/start", { rounds }); } catch {}

    gameState.textContent    = "Running";
    scoreDisplay.textContent = "0 — 0";
    btnStart.disabled = true;
    btnStop.disabled  = false;
    pollTimer = setInterval(fetchData, POLL_INTERVAL);
}

async function stopGame() {
    clearInterval(pollTimer);
    pollTimer = null;
    btnStart.disabled = false;
    btnStop.disabled  = true;
    gameState.textContent = "Stopped";
    try { await apiPost("/stop"); } catch {}
}

async function resetGame() {
    clearInterval(pollTimer);
    pollTimer = null;
    scoreDisplay.textContent = "—";
    gameState.textContent    = "Waiting";
    btnStart.disabled = false;
    btnStop.disabled  = true;
    setStatus("idle");
    document.querySelectorAll(".data-value").forEach(el => el.textContent = "—");
    try { await apiPost("/reset"); } catch {}
}

async function onGameOver(j1Score, j2Score) {
    clearInterval(pollTimer);
    pollTimer = null;
    btnStart.disabled = false;
    btnStop.disabled  = true;

    try {
        await dbUpdateStats(activeJ1, j1Score > j2Score ? 1 : 0, j1Score, activeRounds);
        await dbUpdateStats(activeJ2, j2Score > j1Score ? 1 : 0, j2Score, activeRounds);
    } catch {}

    scoreDisplay.textContent = `${j1Score} — ${j2Score}`;
    if (j1Score > j2Score)      gameState.textContent = `${activeJ1} wins !`;
    else if (j2Score > j1Score) gameState.textContent = `${activeJ2} wins !`;
    else                        gameState.textContent = "Draw !";
}


// ─── POLLING ─────────────────────────────────────────────────────────────────

let errorCount = 0;

async function fetchData() {
    try {
        const json = await apiGet("/data");
        setStatus("connected");
        errorCount = 0;
        updateCards(json);
        if (json.game_over) onGameOver(json.j1_score, json.j2_score);
    } catch {
        errorCount++;
        setStatus("error");
        if (errorCount >= 5) {
            clearInterval(pollTimer);
            pollTimer = null;
            btnStart.disabled = false;
            btnStop.disabled  = true;
            gameState.textContent = "Connection lost";
        }
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


// ─── PROFILES ────────────────────────────────────────────────────────────────

async function createProfile() {
    const name = inputProfileName.value.trim();
    if (!name) return;
    const ok = await dbCreateProfile(name);
    if (ok) {
        inputProfileName.value = "";
        renderProfileList();
        renderProfileSelects();
    }
}

async function deleteProfile(name) {
    await dbDeleteProfile(name);
    renderProfileList();
    renderProfileSelects();
}

async function renderProfileSelects() {
    let profiles = [];
    try { profiles = await dbGetAllProfiles(); } catch {}
    [selectJ1, selectJ2].forEach(sel => {
        const current = sel.value;
        sel.innerHTML = profiles.map(p => `<option value="${p.name}">${p.name}</option>`).join("");
        if (profiles.find(p => p.name === current)) sel.value = current;
    });
}

async function renderProfileList() {
    let profiles = [];
    try { profiles = await dbGetAllProfiles(); } catch {}
    profileList.innerHTML = profiles.map(p =>
        `<div class="profile-row">
            <span class="profile-name">${p.name}</span>
            <span class="profile-stats">${p.games_played} games &mdash; ${p.rounds_won} rounds won</span>
            <button class="btn-delete" data-name="${p.name}">Delete</button>
        </div>`
    ).join("");
    profileList.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => deleteProfile(btn.dataset.name));
    });
}


// ─── HIGHSCORES ──────────────────────────────────────────────────────────────

async function renderHighscores() {
    let profiles = [];
    try { profiles = await dbGetAllProfiles(); } catch {}
    profiles.sort((a, b) => b.games_won - a.games_won);
    highscoresBody.innerHTML = profiles.map(p => {
        const rate = p.rounds_played > 0
            ? Math.round((p.rounds_won / p.rounds_played) * 100) + "%"
            : "—";
        return `<tr>
            <td>${p.name}</td>
            <td>${p.games_played}</td>
            <td>${p.games_won}</td>
            <td>${p.rounds_played}</td>
            <td>${p.rounds_won}</td>
            <td>${rate}</td>
        </tr>`;
    }).join("");
}


// ─── EVENTS ──────────────────────────────────────────────────────────────────

btnStart.addEventListener("click", startGame);
btnStop.addEventListener("click",  stopGame);
btnReset.addEventListener("click", resetGame);
btnCreateProfile.addEventListener("click", createProfile);
inputProfileName.addEventListener("keydown", e => { if (e.key === "Enter") createProfile(); });
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => showView(btn.dataset.view));
});


// ─── INIT ────────────────────────────────────────────────────────────────────

btnStop.disabled = true;
renderProfileSelects();
