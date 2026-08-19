// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const BOX_SIZE = 3;
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let currentDifficulty = 'medium';
let isPuzzleSolved = false;
let hasSubmittedLeaderboardScore = false;
const LEADERBOARD_KEY = 'sudoku-top-scores';
const MAX_LEADERBOARD_SCORES = 10;
const THEME_KEY = 'sudoku-theme';

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  const toggle = document.getElementById('theme-toggle');
  const isDark = selectedTheme === 'dark';

  document.body.dataset.theme = selectedTheme;
  if (toggle) {
    toggle.setAttribute('aria-pressed', String(isDark));
    toggle.textContent = isDark ? 'Switch to light mode' : 'Switch to dark mode';
  }
}

function initializeTheme() {
  let savedTheme = 'light';
  try {
    savedTheme = window.localStorage.getItem(THEME_KEY) || 'light';
  } catch (error) {
    savedTheme = 'light';
  }

  applyTheme(savedTheme);
}

function toggleTheme() {
  const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    window.localStorage.setItem(THEME_KEY, nextTheme);
  } catch (error) {
    // The theme still applies when storage is unavailable.
  }
}

// Timer functions
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

// Hint counter functions
function updateHintDisplay() {
  document.getElementById('hints-used').innerText = `Hints Used: ${hintsUsed}`;
}

function resetHints() {
  hintsUsed = 0;
  updateHintDisplay();
}

function getSelectedDifficulty() {
  const selected = document.querySelector('input[name="difficulty"]:checked');
  return selected ? selected.value : 'medium';
}

function readLeaderboardScores() {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return [];
    }

    const rawScores = window.localStorage.getItem(LEADERBOARD_KEY);
    if (!rawScores) {
      return [];
    }

    const parsed = JSON.parse(rawScores);
    if (!Array.isArray(parsed)) {
      return [];
    }

    const normalized = parsed.reduce((scores, item) => {
      if (!item || typeof item !== 'object') {
        return scores;
      }

      const playerName = typeof item.playerName === 'string' ? item.playerName.trim() : '';
      const completionSeconds = Number(item.completionSeconds);
      const hints = Number(item.hintsUsed);
      const difficulty = typeof item.difficulty === 'string' ? item.difficulty.toLowerCase() : 'medium';

      if (!playerName || Number.isNaN(completionSeconds) || completionSeconds < 0) {
        return scores;
      }

      scores.push({
        playerName: playerName.slice(0, 30),
        completionSeconds: Math.max(0, Math.floor(completionSeconds)),
        completionTime: typeof item.completionTime === 'string' ? item.completionTime : formatTime(Math.max(0, Math.floor(completionSeconds))),
        hintsUsed: Number.isFinite(hints) ? Math.max(0, Math.floor(hints)) : 0,
        difficulty
      });
      return scores;
    }, []);

    return normalized.sort((a, b) => a.completionSeconds - b.completionSeconds || a.hintsUsed - b.hintsUsed);
  } catch (error) {
    console.warn('Leaderboard data was invalid or corrupted and was ignored.', error);
    return [];
  }
}

function saveLeaderboardScores(scores) {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    window.localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores.slice(0, MAX_LEADERBOARD_SCORES)));
  } catch (error) {
    console.warn('Unable to save leaderboard scores.', error);
  }
}

function renderLeaderboard() {
  const tbody = document.getElementById('leaderboard-body');
  const emptyState = document.getElementById('leaderboard-empty');

  if (!tbody) {
    return;
  }

  const scores = readLeaderboardScores();

  tbody.innerHTML = '';

  if (scores.length === 0) {
    if (emptyState) {
      emptyState.hidden = false;
    }
    return;
  }

  if (emptyState) {
    emptyState.hidden = true;
  }

  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.playerName}</td>
      <td>${score.completionTime || formatTime(score.completionSeconds)}</td>
      <td>${score.hintsUsed}</td>
      <td>${score.difficulty}</td>
    `;
    tbody.appendChild(row);
  });
}

function addScoreToLeaderboard(playerName, completionSeconds, hintsUsedValue, difficultyValue) {
  const cleanName = playerName.trim() || 'Player';
  const timeValue = Math.max(0, Math.floor(completionSeconds));
  const hintsValue = Number.isFinite(hintsUsedValue) ? Math.max(0, Math.floor(hintsUsedValue)) : 0;
  const score = {
    playerName: cleanName.slice(0, 30),
    completionSeconds: timeValue,
    completionTime: formatTime(timeValue),
    hintsUsed: hintsValue,
    difficulty: difficultyValue || 'medium'
  };

  const scores = readLeaderboardScores();
  scores.push(score);
  scores.sort((a, b) => a.completionSeconds - b.completionSeconds || a.hintsUsed - b.hintsUsed);
  saveLeaderboardScores(scores);
  renderLeaderboard();
}

function updateControlState() {
  const hintButton = document.getElementById('hint');
  const checkButton = document.getElementById('check-solution');

  if (hintButton) {
    hintButton.disabled = isPuzzleSolved;
  }

  if (checkButton) {
    checkButton.disabled = isPuzzleSolved;
  }
}

function openCompletionModal() {
  const modal = document.getElementById('completion-modal');
  const summary = document.getElementById('completion-summary');
  const input = document.getElementById('player-name');

  if (!modal || !summary || !input) {
    return;
  }

  summary.textContent = `Congratulations! You solved the puzzle in ${formatTime(elapsedSeconds)} with ${hintsUsed} hint(s) on ${currentDifficulty} difficulty.`;
  modal.hidden = false;
  input.value = '';
  input.focus();
}

function closeCompletionModal() {
  const modal = document.getElementById('completion-modal');
  const form = document.getElementById('completion-form');

  if (modal) {
    modal.hidden = true;
  }

  if (form) {
    form.reset();
  }
}

function resetCompletionState() {
  isPuzzleSolved = false;
  hasSubmittedLeaderboardScore = false;
  updateControlState();
}

function recordCompletedGame() {
  if (isPuzzleSolved) {
    return;
  }

  isPuzzleSolved = true;
  hasSubmittedLeaderboardScore = false;
  stopTimer();
  updateControlState();
  openCompletionModal();
}

async function checkForSolvedBoard() {
  if (isPuzzleSolved) {
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) {
    return;
  }

  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board })
    });

    if (!res.ok) {
      return;
    }

    const data = await res.json();
    if (!data || data.error) {
      return;
    }

    const incorrect = new Set((data.incorrect || []).map((cell) => cell[0] * SIZE + cell[1]));
    if (incorrect.size === 0) {
      const msg = document.getElementById('message');
      if (msg) {
        msg.classList.remove('message-error');
        msg.classList.add('message-success');
        msg.innerText = `Congratulations! You solved the puzzle in ${formatTime(elapsedSeconds)} with ${hintsUsed} hint(s).`;
      }
      recordCompletedGame();
    }
  } catch (error) {
    console.warn('Unable to validate board completion state.', error);
  }
}

async function useHint() {
  if (isPuzzleSolved) {
    return;
  }
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const msg = document.getElementById('message');
  
  // Check if puzzle is already solved
  let emptyCellCount = 0;
  for (let i = 0; i < inputs.length; i++) {
    if (!inputs[i].disabled && inputs[i].value === '') {
      emptyCellCount++;
    }
  }
  
  if (emptyCellCount === 0) {
    msg.classList.remove('message-success');
    msg.classList.add('message-error');
    msg.innerText = 'Puzzle is already complete! No hints needed.';
    return;
  }
  
  // Request a hint from the backend
  const res = await fetch('/hint');
  
  if (!res.ok) {
    msg.classList.remove('message-success');
    msg.classList.add('message-error');
    msg.innerText = 'No more empty cells to hint!';
    return;
  }
  
  const data = await res.json();
  
  if (data.error) {
    msg.classList.remove('message-success');
    msg.classList.add('message-error');
    msg.innerText = data.error;
    return;
  }
  
  // Fill the hinted cell
  const hintedRow = data.row;
  const hintedCol = data.col;
  const hintedValue = data.value;
  
  const idx = hintedRow * SIZE + hintedCol;
  const hintedCell = inputs[idx];
  
  hintedCell.value = hintedValue;
  hintedCell.disabled = true;
  hintedCell.className = 'sudoku-cell hinted';
  
  // Increment hints counter
  hintsUsed++;
  updateHintDisplay();
  
  msg.style.color = '#388e3c';
  msg.innerText = `Hint provided! (Hints used: ${hintsUsed})`;
}

// Sudoku validation functions
function getRowValues(row) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const values = new Set();
  for (let j = 0; j < SIZE; j++) {
    const idx = row * SIZE + j;
    const val = inputs[idx].value;
    if (val) values.add(parseInt(val, 10));
  }
  return values;
}

function getColumnValues(col) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const values = new Set();
  for (let i = 0; i < SIZE; i++) {
    const idx = i * SIZE + col;
    const val = inputs[idx].value;
    if (val) values.add(parseInt(val, 10));
  }
  return values;
}

function getBoxValues(row, col) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const values = new Set();
  const startRow = Math.floor(row / BOX_SIZE) * BOX_SIZE;
  const startCol = Math.floor(col / BOX_SIZE) * BOX_SIZE;
  
  for (let i = startRow; i < startRow + BOX_SIZE; i++) {
    for (let j = startCol; j < startCol + BOX_SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      if (val) values.add(parseInt(val, 10));
    }
  }
  return values;
}

function hasConflict(value, row, col) {
  const numValue = parseInt(value, 10);
  
  // Check row
  if (getRowValues(row).has(numValue)) return true;
  
  // Check column
  if (getColumnValues(col).has(numValue)) return true;
  
  // Check 3x3 box
  if (getBoxValues(row, col).has(numValue)) return true;
  
  return false;
}

function clearCellErrors(input) {
  input.classList.remove('invalid', 'conflict', 'incorrect');
}

function validateCell(input) {
  clearCellErrors(input);
  
  const value = input.value.trim();
  
  // Empty cells are valid
  if (!value) {
    return true;
  }
  
  // Check if it's a single digit
  if (value.length !== 1) {
    input.classList.add('invalid');
    return false;
  }
  
  // Check if it's 1-9
  const numValue = parseInt(value, 10);
  if (isNaN(numValue) || numValue < 1 || numValue > 9) {
    input.classList.add('invalid');
    return false;
  }
  
  // Get row and column
  const row = parseInt(input.dataset.row, 10);
  const col = parseInt(input.dataset.col, 10);
  
  // Check for conflicts with other cells
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  // Temporarily remove this cell's value to check conflicts
  const tempValue = input.value;
  input.value = '';
  
  if (hasConflict(tempValue, row, col)) {
    input.value = tempValue;
    input.classList.add('conflict');
    return false;
  }
  
  // Restore value
  input.value = tempValue;
  return true;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
}

async function newGame() {
  currentDifficulty = getSelectedDifficulty();
  resetCompletionState();
  closeCompletionModal();
  const url = `/new?difficulty=${encodeURIComponent(currentDifficulty)}`;
  const res = await fetch(url);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  
  // Reset hints counter for new game
  resetHints();
  startTimer();
}

async function checkSolution() {
  if (isPuzzleSolved) {
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  
  // Build the board from user input
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  
  // Send to backend for verification
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  
  const data = await res.json();
  const msg = document.getElementById('message');
  
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  
  // Highlight incorrect cells
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue; // Don't modify prefilled cells
    
    // Clear any previous validation states
    inp.classList.remove('invalid', 'conflict', 'incorrect');
    
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  
  // Show result message
  if (incorrect.size === 0) {
    msg.classList.remove('message-error');
    msg.classList.add('message-success');
    msg.innerText = `Congratulations! You solved the puzzle in ${formatTime(elapsedSeconds)} with ${hintsUsed} hint(s).`;
    recordCompletedGame();
  } else {
    msg.classList.remove('message-success');
    msg.classList.add('message-error');
    msg.innerText = `${incorrect.size} cell(s) are incorrect. Keep trying!`;
  }
}

// Event delegation for board input
document.addEventListener('DOMContentLoaded', () => {
  const boardDiv = document.getElementById('sudoku-board');
  const themeToggle = document.getElementById('theme-toggle');
  const completionForm = document.getElementById('completion-form');
  const closeButton = document.getElementById('close-completion-modal');
  const cancelButton = document.getElementById('cancel-completion');
  renderLeaderboard();
  initializeTheme();
  updateControlState();

  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  // Single event listener for all cells using event delegation
  boardDiv.addEventListener('input', (e) => {
    const input = e.target;
    
    // Only handle input elements (cells)
    if (!input.classList.contains('sudoku-cell') || input.disabled || isPuzzleSolved) {
      return;
    }
    
    // Only allow digits 1-9
    const val = input.value.replace(/[^1-9]/g, '');
    input.value = val;
    
    // Validate the cell
    validateCell(input);
    checkForSolvedBoard();
  });

  if (completionForm) {
    completionForm.addEventListener('submit', (event) => {
      event.preventDefault();

      const submitButton = completionForm.querySelector('button[type="submit"]');
      if (!isPuzzleSolved || hasSubmittedLeaderboardScore) {
        if (submitButton) {
          submitButton.disabled = true;
        }
        return;
      }

      const nameInput = document.getElementById('player-name');
      const playerName = nameInput ? nameInput.value.trim() : '';

      if (!playerName) {
        if (nameInput) {
          nameInput.focus();
        }
        return;
      }

      hasSubmittedLeaderboardScore = true;
      if (submitButton) {
        submitButton.disabled = true;
      }
      addScoreToLeaderboard(playerName, elapsedSeconds, hintsUsed, currentDifficulty);
      closeCompletionModal();
    });
  }

  if (closeButton) {
    closeButton.addEventListener('click', () => {
      const submitButton = completionForm ? completionForm.querySelector('button[type="submit"]') : null;
      if (submitButton) {
        submitButton.disabled = false;
      }
      closeCompletionModal();
    });
  }

  if (cancelButton) {
    cancelButton.addEventListener('click', () => {
      const submitButton = completionForm ? completionForm.querySelector('button[type="submit"]') : null;
      if (submitButton) {
        submitButton.disabled = false;
      }
      closeCompletionModal();
    });
  }

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeCompletionModal();
    }
  });
});

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', useHint);
  newGame();
});

// Clean up timer on page unload
window.addEventListener('beforeunload', () => {
  stopTimer();
});