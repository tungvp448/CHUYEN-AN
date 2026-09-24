// ==================== KHỞI TẠO BIẾN TOÀN CỤC ====================
let playerHandle = "Anonymous_Detective";
let cases = [];
let currentCaseIndex = 0;
let casesProgress = {}; // case_id -> {solved, attempts, time, clues_used, score}

// Trạng thái bàn chơi vụ án hiện tại
const MAX_ATTEMPTS = 6;
let currentWordLength = 5; // Độ dài từ tự động thay đổi theo từng vụ án
let currentAttempt = 0;
let currentCol = 0;
let currentGuess = [];
let isSubmitting = false;
let caseIsFinished = false;

// Đồng hồ Contest
let contestTimerInterval = null;
let totalContestSeconds = 0;
let caseStartSeconds = 0;

// Hệ thống âm thanh
let isMusicOn = true;
let isSoundOn = true;
const audioElements = {
  bgm: document.getElementById("audio-bgm"),
  type: document.getElementById("audio-type"),
  submit: document.getElementById("audio-submit"),
  clue: document.getElementById("audio-clue"),
  win: document.getElementById("audio-win"),
  lose: document.getElementById("audio-lose"),
  error: document.getElementById("audio-error")
};

// ==================== AUDIO CONTROLLER ====================
function playSfx(name) {
  if (!isSoundOn) return;
  const audio = audioElements[name];
  if (audio) {
    audio.currentTime = 0;
    audio.play().catch(() => {});
  }
}

function stopSfx(name) {
  const audio = audioElements[name];
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
  }
}

function startBgm() {
  if (!isMusicOn) return;
  if (audioElements.bgm) {
    audioElements.bgm.volume = 0.35;
    audioElements.bgm.play().catch(() => {});
  }
}

function stopBgm() {
  if (audioElements.bgm) {
    audioElements.bgm.pause();
  }
}

// ==================== KHỞI CHẠY KHI TẢI TRANG ====================
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  buildVirtualKeyboard();
});

function setupEventListeners() {
  // Bắt đầu thi đấu
  document.getElementById("btn-start-contest").addEventListener("click", onStartContest);
  document.getElementById("player-name").addEventListener("keypress", (e) => {
    if (e.key === "Enter") onStartContest();
  });

  // Mở & Đóng Bảng Xếp Hạng
  document.getElementById("btn-open-leaderboard").addEventListener("click", () => showLeaderboard(false));
  document.getElementById("btn-view-standings").addEventListener("click", () => showLeaderboard(false));
  document.getElementById("btn-finish-leaderboard").addEventListener("click", () => showLeaderboard(false));
  document.getElementById("btn-close-modal").addEventListener("click", closeLeaderboard);

  // Nút âm thanh
  document.getElementById("btn-toggle-music").addEventListener("click", toggleMusic);
  document.getElementById("btn-toggle-sound").addEventListener("click", toggleSound);

  // Nút xem manh mối & Vụ án tiếp
  document.getElementById("btn-get-clue").addEventListener("click", onGetClue);
  document.getElementById("btn-next-case").addEventListener("click", onNextCase);
  document.getElementById("btn-play-again").addEventListener("click", resetContestToLobby);

  // Bắt phím vật lý trên máy tính
  document.addEventListener("keydown", handlePhysicalKey);
}

function toggleMusic() {
  isMusicOn = !isMusicOn;
  const btn = document.getElementById("btn-toggle-music");
  if (isMusicOn) {
    btn.textContent = "🎵";
    startBgm();
  } else {
    btn.textContent = "🔇";
    stopBgm();
  }
}

function toggleSound() {
  isSoundOn = !isSoundOn;
  const btn = document.getElementById("btn-toggle-sound");
  btn.textContent = isSoundOn ? "🔊" : "🔕";
}

// ==================== LOBBY & CONTEST SETUP ====================
async function onStartContest() {
  const input = document.getElementById("player-name");
  playerHandle = input.value.trim() || "Thám_Tử_Ẩn_Danh";
  document.getElementById("display-handle").textContent = playerHandle;

  // Bắt đầu phát BGM ngay lập tức sau click của user
  startBgm();

  // Tải danh sách vụ án từ server
  try {
    const res = await fetch("/api/cases");
    cases = await res.json();
    if (!cases || cases.length === 0) {
      alert("Không có vụ án nào trên máy chủ!");
      return;
    }
  } catch (err) {
    console.error("Lỗi nạp cases:", err);
    alert("Không thể kết nối tới máy chủ Chuyên Án!");
    return;
  }

  // Khởi tạo tiến trình contest
  casesProgress = {};
  cases.forEach(c => {
    casesProgress[c.id] = {
      solved: false,
      attempted: false,
      attempts: 0,
      time: 0,
      clues_used: 0,
      score: 0,
      revealed_clues: []
    };
  });

  // Chuyển màn hình
  document.getElementById("screen-lobby").classList.remove("active");
  document.getElementById("screen-finished").classList.remove("active");
  document.getElementById("screen-game").classList.add("active");

  // Khởi động đồng hồ bấm giờ
  startTimer();

  // Xây dựng thanh chọn vụ án (Problem Nav)
  buildProblemNav();

  // Nạp vụ án đầu tiên
  loadCase(0);
}

function startTimer() {
  if (contestTimerInterval) clearInterval(contestTimerInterval);
  totalContestSeconds = 0;
  updateTimerDisplay();

  contestTimerInterval = setInterval(() => {
    totalContestSeconds++;
    updateTimerDisplay();
  }, 1000);
}

function updateTimerDisplay() {
  const m = String(Math.floor(totalContestSeconds / 60)).padStart(2, "0");
  const s = String(totalContestSeconds % 60).padStart(2, "0");
  document.getElementById("contest-timer").textContent = `${m}:${s}`;
}

// ==================== PROBLEM NAVIGATOR (CP STYLE) ====================
function buildProblemNav() {
  const nav = document.getElementById("problem-nav");
  nav.innerHTML = "";

  cases.forEach((c, idx) => {
    const pill = document.createElement("div");
    pill.className = `nav-pill ${idx === currentCaseIndex ? "active" : ""}`;
    pill.id = `pill-case-${c.id}`;
    pill.textContent = `Vụ #${c.id}`;
    pill.addEventListener("click", () => {
      loadCase(idx);
    });
    nav.appendChild(pill);
  });
}

function updateProblemPill(caseId) {
  const pill = document.getElementById(`pill-case-${caseId}`);
  if (!pill) return;

  const prog = casesProgress[caseId];
  if (prog.solved) {
    pill.className = "nav-pill ac";
    pill.textContent = `Vụ #${caseId} (+${prog.attempts})`;
  } else if (prog.attempts >= MAX_ATTEMPTS) {
    pill.className = "nav-pill failed";
    pill.textContent = `Vụ #${caseId} (-6)`;
  }
}

// ==================== CASE LOGIC & BOARD ====================
function loadCase(index) {
  // Dừng ngay lập tức âm thanh thắng/thua của vụ án trước đó
  stopSfx("win");
  stopSfx("lose");

  currentCaseIndex = index;
  const c = cases[index];
  currentWordLength = c.word_length || 5; // Cập nhật độ dài từ khóa của vụ án này
  caseStartSeconds = totalContestSeconds;
  caseIsFinished = casesProgress[c.id].solved || casesProgress[c.id].attempts >= MAX_ATTEMPTS;

  // Cập nhật Navigator highlight
  document.querySelectorAll(".nav-pill").forEach((p, idx) => {
    p.classList.toggle("active", idx === index);
  });

  // Tiêu đề & Thông tin vụ án
  document.getElementById("case-title").textContent = `🕵️ Vụ #${c.id}: ${c.case_name}`;
  
  // Khôi phục manh mối
  const prog = casesProgress[c.id];
  updateClueUI(c, prog);

  // Tải ảnh vật chứng hoặc ảnh mở khóa (nếu đã phá xong vụ này)
  const imgEl = document.getElementById("evidence-img");
  const placeholderEl = document.getElementById("evidence-placeholder");
  document.getElementById("placeholder-case-name").textContent = c.case_name;

  const revealPath = prog.reveal_image || c.reveal_image;
  const currentDisplayImg = (prog.solved && revealPath) ? revealPath : c.image;

  if (currentDisplayImg) {
    const fullSrc = currentDisplayImg.startsWith("/") ? currentDisplayImg : `/${currentDisplayImg}`;
    imgEl.onload = () => {
      imgEl.style.display = "block";
      placeholderEl.style.display = "none";
    };
    imgEl.onerror = () => {
      imgEl.style.display = "none";
      placeholderEl.style.display = "block";
    };
    imgEl.src = fullSrc;
    if (imgEl.complete && imgEl.naturalWidth > 0) {
      imgEl.style.display = "block";
      placeholderEl.style.display = "none";
    }
  } else {
    imgEl.style.display = "none";
    placeholderEl.style.display = "block";
  }

  // Tạo lại bảng Wordle Grid
  buildWordleGrid();

  // Đặt lại phím ảo
  resetKeyboardColors();

  // Cập nhật trạng thái
  currentAttempt = 0;
  currentCol = 0;
  currentGuess = [];
  document.getElementById("status-bar").textContent = caseIsFinished 
    ? (prog.solved ? "🎉 Vụ án này đã được phá thành công!" : "💀 Vụ án này đã thất bại!")
    : `Nhập ${currentWordLength} chữ cái để giải mã hung khí / tang vật`;
  document.getElementById("status-bar").style.color = "#e4e4e7";

  document.getElementById("btn-next-case").style.display = caseIsFinished ? "block" : "none";
}

function updateClueUI(c, prog) {
  const clueDisplay = document.getElementById("clue-display");
  const btnClue = document.getElementById("btn-get-clue");

  if (prog.revealed_clues.length > 0) {
    const lastClue = prog.revealed_clues[prog.revealed_clues.length - 1];
    clueDisplay.textContent = `🔍 Manh mối ${prog.revealed_clues.length}/${c.clues_count}: ${lastClue}`;
    clueDisplay.style.color = "#38bdf8";
  } else {
    clueDisplay.textContent = "💡 Bấm 'Xem Manh Mối' để mở gợi ý giải mã vụ án";
    clueDisplay.style.color = "#a1a1aa";
  }

  btnClue.textContent = `🔍 XEM MANH MỐI (${prog.revealed_clues.length}/${c.clues_count})`;
  btnClue.disabled = (prog.revealed_clues.length >= c.clues_count) || caseIsFinished;
}

async function onGetClue() {
  const c = cases[currentCaseIndex];
  const prog = casesProgress[c.id];
  if (prog.revealed_clues.length >= c.clues_count || caseIsFinished) return;

  const nextIdx = prog.revealed_clues.length;
  try {
    const res = await fetch(`/api/clue/${c.id}/${nextIdx}`);
    const data = await res.json();
    if (data.success) {
      playSfx("clue");
      prog.revealed_clues.push(data.clue);
      prog.clues_used++;
      updateClueUI(c, prog);
    }
  } catch (err) {
    console.error("Lỗi lấy manh mối:", err);
  }
}

// ==================== BẢNG WORDLE GRID ====================
function buildWordleGrid() {
  const grid = document.getElementById("wordle-grid");
  grid.innerHTML = "";

  for (let r = 0; r < MAX_ATTEMPTS; r++) {
    const row = document.createElement("div");
    row.className = "grid-row";
    row.id = `grid-row-${r}`;

    for (let col = 0; col < currentWordLength; col++) {
      const cell = document.createElement("div");
      cell.className = "grid-cell";
      cell.id = `cell-${r}-${col}`;
      row.appendChild(cell);
    }
    grid.appendChild(row);
  }
}

// ==================== BÀN PHÍM ẢO & XỬ LÝ NHẬP LIỆU ====================
const KB_LAYOUT = [
  ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
  ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
  ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"]
];

function buildVirtualKeyboard() {
  const kb = document.getElementById("virtual-keyboard");
  kb.innerHTML = "";

  KB_LAYOUT.forEach(rowKeys => {
    const row = document.createElement("div");
    row.className = "kb-row";

    rowKeys.forEach(k => {
      const btn = document.createElement("button");
      btn.className = `kb-key ${k === "ENTER" || k === "⌫" ? "wide" : ""}`;
      btn.id = `key-${k === "⌫" ? "BACKSPACE" : k}`;
      btn.textContent = k;
      btn.addEventListener("click", () => handleInput(k === "⌫" ? "BACKSPACE" : k));
      row.appendChild(btn);
    });
    kb.appendChild(row);
  });
}

function resetKeyboardColors() {
  document.querySelectorAll(".kb-key").forEach(k => {
    k.classList.remove("correct", "present", "absent");
  });
}

function handlePhysicalKey(e) {
  if (document.getElementById("screen-game").classList.contains("active") && !caseIsFinished) {
    if (e.key === "Enter") {
      handleInput("ENTER");
    } else if (e.key === "Backspace") {
      handleInput("BACKSPACE");
    } else if (/^[a-zA-Z]$/.test(e.key)) {
      handleInput(e.key.toUpperCase());
    }
  }
}

function handleInput(key) {
  if (caseIsFinished || isSubmitting) return;

  if (key === "ENTER") {
    submitGuess();
  } else if (key === "BACKSPACE") {
    if (currentCol > 0) {
      currentCol--;
      currentGuess.pop();
      const cell = document.getElementById(`cell-${currentAttempt}-${currentCol}`);
      cell.textContent = "";
      cell.classList.remove("active");
      playSfx("type");
    }
  } else if (/^[A-Z]$/.test(key)) {
    if (currentCol < currentWordLength) {
      currentGuess.push(key);
      const cell = document.getElementById(`cell-${currentAttempt}-${currentCol}`);
      cell.textContent = key;
      cell.classList.add("active");
      currentCol++;
      playSfx("type");
    }
  }
}

// ==================== NỘP TỪ ĐOÁN (SUBMIT GUESS) ====================
async function submitGuess() {
  if (currentCol < currentWordLength) {
    playSfx("error");
    const rowEl = document.getElementById(`grid-row-${currentAttempt}`);
    rowEl.classList.add("shake");
    setTimeout(() => rowEl.classList.remove("shake"), 400);
    showStatus(`⚠️ Phải đủ ${currentWordLength} chữ cái!`, "#facc15");
    return;
  }

  isSubmitting = true;
  const c = cases[currentCaseIndex];
  const guessWord = currentGuess.join("");

  try {
    const res = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: c.id,
        guess: guessWord,
        attempt: currentAttempt + 1
      })
    });

    const data = await res.json();
    if (!data.success) {
      playSfx("error");
      showStatus(`⚠️ ${data.error}`, "#facc15");
      isSubmitting = false;
      return;
    }

    // Hiệu ứng lật ô Wordle (Flip animation)
    playSfx("submit");
    const statuses = data.result_status;

    statuses.forEach((status, i) => {
      const cell = document.getElementById(`cell-${currentAttempt}-${i}`);
      setTimeout(() => {
        cell.classList.add("flip", status);
        updateVirtualKeyColor(guessWord[i], status);
      }, i * 150);
    });

    // Chờ animation hoàn thành để đánh giá kết quả
    setTimeout(() => {
      evaluateRoundResult(data, c);
      isSubmitting = false;
    }, currentWordLength * 150 + 200);

  } catch (err) {
    console.error("Lỗi submit:", err);
    isSubmitting = false;
  }
}

function updateVirtualKeyColor(char, status) {
  const btn = document.getElementById(`key-${char}`);
  if (!btn) return;

  if (status === "correct") {
    btn.className = "kb-key correct";
  } else if (status === "present" && !btn.classList.contains("correct")) {
    btn.className = "kb-key present";
  } else if (status === "absent" && !btn.classList.contains("correct") && !btn.classList.contains("present")) {
    btn.className = "kb-key absent";
  }
}

function evaluateRoundResult(data, c) {
  const prog = casesProgress[c.id];
  prog.attempts = currentAttempt + 1;
  prog.attempted = true;

  if (data.is_correct) {
    // PHÁ ÁN THÀNH CÔNG! (ACCEPTED - AC)
    playSfx("win");
    caseIsFinished = true;
    prog.solved = true;
    prog.time = totalContestSeconds - caseStartSeconds;

    // Đổi sang ảnh mở khóa (reveal_image) ngay lập tức
    const revealImg = data.reveal_image || c.reveal_image;
    if (revealImg) {
      prog.reveal_image = revealImg;
      const imgEl = document.getElementById("evidence-img");
      const placeholderEl = document.getElementById("evidence-placeholder");
      const fullSrc = revealImg.startsWith("/") ? revealImg : `/${revealImg}`;
      
      imgEl.onload = () => {
        imgEl.style.display = "block";
        placeholderEl.style.display = "none";
      };
      imgEl.onerror = () => {
        console.error("Lỗi nạp ảnh mở khóa:", fullSrc);
      };
      imgEl.src = fullSrc;
      if (imgEl.complete && imgEl.naturalWidth > 0) {
        imgEl.style.display = "block";
        placeholderEl.style.display = "none";
      }
    }

    // Tính điểm CP
    prog.score = calculateCaseScore(prog.attempts, prog.clues_used, prog.time);
    showStatus("🎉 PHÁ ÁN THÀNH CÔNG! BẠN ĐÃ TÌM RA TỪ KHÓA!", "#4ade80");
    document.getElementById("btn-next-case").style.display = "block";

    updateProblemPill(c.id);
    updateTotalScore();
    checkIfContestFinished();

  } else if (currentAttempt + 1 >= MAX_ATTEMPTS) {
    // THẤT BẠI VỤ ÁN NÀY (FAILED)
    playSfx("lose");
    caseIsFinished = true;
    prog.solved = false;
    prog.time = totalContestSeconds - caseStartSeconds;
    prog.score = 0;

    const answer = data.target_word || "???";
    showStatus(`💀 CHUYÊN ÁN BẾ TẮC! TỪ KHÓA LÀ: ${answer}`, "#f87171");
    document.getElementById("btn-next-case").style.display = "block";

    updateProblemPill(c.id);
    checkIfContestFinished();

  } else {
    // TIẾP TỤC HÀNG TIẾP THEO
    currentAttempt++;
    currentCol = 0;
    currentGuess = [];
    showStatus("Tiếp tục giải mã...", "#e4e4e7");
  }
}

function calculateCaseScore(attempts, cluesUsed, timeSec) {
  // Điểm gốc 1000 - trừ theo lượt đoán - trừ theo clue - trừ theo thời gian
  let score = 1000 - ((attempts - 1) * 120) - (cluesUsed * 80) - Math.min(200, Math.floor(timeSec * 1.5));
  return Math.max(100, score);
}

function updateTotalScore() {
  let total = 0;
  Object.values(casesProgress).forEach(p => {
    total += p.score || 0;
  });
  document.getElementById("current-score").textContent = total;
}

function showStatus(msg, color) {
  const el = document.getElementById("status-bar");
  el.textContent = msg;
  el.style.color = color;
}

function onNextCase() {
  // Tìm vụ án tiếp theo chưa giải xong
  let nextIdx = (currentCaseIndex + 1) % cases.length;
  for (let i = 0; i < cases.length; i++) {
    const checkIdx = (currentCaseIndex + 1 + i) % cases.length;
    const p = casesProgress[cases[checkIdx].id];
    if (!p.solved && p.attempts < MAX_ATTEMPTS) {
      nextIdx = checkIdx;
      break;
    }
  }
  loadCase(nextIdx);
}

// ==================== KẾT THÚC THI ĐẤU (FINISH CONTEST) ====================
async function checkIfContestFinished() {
  const allDone = cases.every(c => {
    const p = casesProgress[c.id];
    return p.solved || p.attempts >= MAX_ATTEMPTS;
  });

  if (allDone) {
    clearInterval(contestTimerInterval);

    // Tính toán kết quả tổng kết
    let solvedCount = 0;
    let totalScore = 0;
    const casesDetail = {};

    cases.forEach(c => {
      const p = casesProgress[c.id];
      if (p.solved) solvedCount++;
      totalScore += p.score;
      casesDetail[c.id] = {
        solved: p.solved,
        attempts: p.attempts,
        time: p.time,
        clues: p.clues_used,
        score: p.score
      };
    });

    // Nộp kết quả lên server
    let rank = "?";
    try {
      const res = await fetch("/api/submit_contest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          handle: playerHandle,
          score: totalScore,
          solved: solvedCount,
          total_time: totalContestSeconds,
          cases_detail: casesDetail
        })
      });
      const submitData = await res.json();
      if (submitData.success) {
        rank = `#${submitData.rank}`;
      }
    } catch (e) {
      console.error("Lỗi submit contest:", e);
    }

    // Hiển thị màn hình Finished
    setTimeout(() => {
      document.getElementById("screen-game").classList.remove("active");
      document.getElementById("screen-finished").classList.add("active");

      document.getElementById("summary-solved").textContent = `${solvedCount}/${cases.length}`;
      document.getElementById("summary-score").textContent = totalScore;
      
      const m = String(Math.floor(totalContestSeconds / 60)).padStart(2, "0");
      const s = String(totalContestSeconds % 60).padStart(2, "0");
      document.getElementById("summary-time").textContent = `${m}:${s}`;
      document.getElementById("summary-rank").textContent = rank;
    }, 1200);
  }
}

function resetContestToLobby() {
  // Tắt ngay lập tức tất cả các âm thanh (nhạc win, nhạc lose, nhạc nền BGM)
  stopSfx("win");
  stopSfx("lose");
  stopSfx("submit");
  stopSfx("clue");
  stopSfx("type");
  stopBgm();

  document.getElementById("screen-finished").classList.remove("active");
  document.getElementById("screen-lobby").classList.add("active");
}

// ==================== BẢNG XẾP HẠNG (LEADERBOARD MODAL) ====================
async function showLeaderboard(fromFinish = false) {
  const modal = document.getElementById("modal-leaderboard");
  modal.classList.add("active");

  const tbody = document.getElementById("leaderboard-tbody");
  tbody.innerHTML = `<tr><td colspan="6" style="padding: 20px; color: #a1a1aa;">Đang tải bảng xếp hạng...</td></tr>`;

  try {
    const res = await fetch("/api/leaderboard");
    const standings = await res.json();

    if (!standings || standings.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="padding: 20px; color: #a1a1aa;">Chưa có thám tử nào nộp bài!</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    standings.forEach(row => {
      const tr = document.createElement("tr");

      // Cột Rank với màu huy chương
      let rankDisplay = `#${row.rank}`;
      let rankClass = "";
      if (row.rank === 1) { rankDisplay = "🥇 #1"; rankClass = "rank-gold"; }
      else if (row.rank === 2) { rankDisplay = "🥈 #2"; rankClass = "rank-silver"; }
      else if (row.rank === 3) { rankDisplay = "🥉 #3"; rankClass = "rank-bronze"; }

      const m = String(Math.floor(row.total_time / 60)).padStart(2, "0");
      const s = String(row.total_time % 60).padStart(2, "0");

      // Chi tiết từng vụ
      let detailsHtml = "";
      const details = row.cases_detail || {};
      for (let i = 1; i <= 4; i++) {
        const item = details[i];
        if (item) {
          if (item.solved) {
            detailsHtml += `<span class="badge-ac" title="Vụ #${i}: ${item.time}s">+${item.attempts}</span> `;
          } else {
            detailsHtml += `<span class="badge-fail" title="Vụ #${i}: Thất bại">-6</span> `;
          }
        } else {
          detailsHtml += `<span class="badge-none">.</span> `;
        }
      }

      tr.innerHTML = `
        <td class="${rankClass}">${rankDisplay}</td>
        <td style="font-weight: 700; text-align: left;">${escapeHtml(row.handle)}</td>
        <td style="color: #4ade80; font-weight: 700;">${row.solved}</td>
        <td style="color: #fbbf24; font-weight: 700;">${row.score}</td>
        <td>${m}:${s}</td>
        <td>${detailsHtml}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Lỗi leaderboard:", err);
    tbody.innerHTML = `<tr><td colspan="6" style="padding: 20px; color: #ef4444;">Không thể tải bảng xếp hạng!</td></tr>`;
  }
}

function closeLeaderboard() {
  document.getElementById("modal-leaderboard").classList.remove("active");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
