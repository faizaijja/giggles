// static/js/timer.js
let sessionDuration = 10 * 60; // 7 minutes
let breakDuration = 2 * 60;   // 2 minutes
let isSession = true;
let timer;

function startTimer(duration) {
  let time = duration;
  clearInterval(timer);

  timer = setInterval(() => {
    const minutes = String(Math.floor(time / 60)).padStart(2, '0');
    const seconds = String(time % 60).padStart(2, '0');
    const label = isSession ? 'Session' : 'Break';

    const timerDisplay = document.getElementById('timerDisplay');
    if (timerDisplay) {
      timerDisplay.textContent = `${label}: ${minutes}:${seconds}`;
    }

    if (--time < 0) {
      isSession = !isSession;
      startTimer(isSession ? sessionDuration : breakDuration);
    }
  }, 1000);
}

window.addEventListener('load', () => {
  const timerDisplay = document.getElementById('timerDisplay');
  if (timerDisplay) {
    startTimer(sessionDuration);
  }
});
