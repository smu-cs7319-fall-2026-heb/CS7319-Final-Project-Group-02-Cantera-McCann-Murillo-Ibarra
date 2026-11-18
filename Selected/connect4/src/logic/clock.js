export const ALLOWED_DURATIONS = [10, 20, 30];

export function registerClock(bus, { duration: initialDuration = 20 } = {}) {
  let duration = initialDuration;
  let timeLeft = duration;
  let phase = 'playing';
  let intervalId = null;

  const publishTick = () =>
    bus.publish('clock:tick', { timeLeft, duration, running: intervalId !== null });

  const stop = () => {
    if (intervalId === null) return;
    clearInterval(intervalId);
    intervalId = null;
  };

  const start = () => {
    if (intervalId !== null || phase !== 'playing') return;
    intervalId = setInterval(tick, 1000);
  };

  const restart = () => {
    stop();
    timeLeft = duration;
    start();
    publishTick();
  };

  function tick() {
    timeLeft = Math.max(timeLeft - 1, 0);
    if (timeLeft === 0) {
      stop();
      publishTick();
      bus.publish('clock:expired', { duration });
      return;
    }
    publishTick();
  }

  bus.subscribe('turn:changed', restart);

  bus.subscribe('game:phase', ({ phase: next }) => {
    phase = next;
    if (phase === 'playing') start();
    else stop();
    publishTick();
  });

  bus.subscribe('window:duration-changed', ({ seconds }) => {
    if (!ALLOWED_DURATIONS.includes(seconds)) return;
    duration = seconds;
    bus.publish('clock:configured', { duration });
    if (phase !== 'over') restart();
  });

  bus.subscribe('window:opened', () => {
    start();
    bus.publish('clock:configured', { duration });
    publishTick();
  });

  return { stop };
}
