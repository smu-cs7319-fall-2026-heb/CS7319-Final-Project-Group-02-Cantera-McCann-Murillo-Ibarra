const UNCOUNTED_EVENTS = new Set(['clock:tick', 'player:column-hovered', 'metrics:updated']);

const QUIET_MS = 250;

export function summarize(values) {
  if (values.length === 0) return { count: 0, last: null, median: null, p95: null };
  const sorted = [...values].sort((a, b) => a - b);
  const rank = (q) => sorted[Math.max(0, Math.ceil(q * sorted.length) - 1)];
  return { count: values.length, last: values.at(-1), median: rank(0.5), p95: rank(0.95) };
}

export function registerMetrics(bus, { now = () => performance.now() } = {}) {
  const totals = { gamesPlayed: 0, moves: 0, timeouts: 0 };
  const samples = [];
  let pending = null; 
  let quietTimer = null;

  const elapsed = () => Math.round((now() - pending.clickedAt) * 100) / 100;

  const publishMetrics = () => {
    const column = (key) => samples.map((s) => s[key]).filter((v) => v !== null);
    bus.publish('metrics:updated', {
      ...totals,
      samples: [...samples],
      summary: {
        placedMs: summarize(column('placedMs')),
        turnMs: summarize(column('turnMs')),
        winMs: summarize(column('winMs')),
        messages: summarize(column('messages')),
      },
    });
  };

  const finishMove = () => {
    clearTimeout(quietTimer);
    quietTimer = null;
    const move = pending;
    pending = null;
    if (!move || move.placedMs === null) return;
    const { placedMs, turnMs, winMs, messages } = move;
    samples.push({ placedMs, turnMs, winMs, messages });
    publishMetrics();
  };

  const restartQuietTimer = () => {
    clearTimeout(quietTimer);
    quietTimer = setTimeout(finishMove, QUIET_MS);
  };

  bus.subscribeAll((event) => {
    if (!pending || UNCOUNTED_EVENTS.has(event)) return;
    pending.messages += 1;
    restartQuietTimer();
  });

  bus.subscribe('player:column-clicked', ({ clickedAt }) => {
    if (typeof clickedAt !== 'number') return;
    if (pending) finishMove();
    pending = {
      clickedAt,
      messages: 1, 
      dropped: false,
      turnPassed: false,
      placedMs: null,
      turnMs: null,
      winMs: null,
    };
    restartQuietTimer();
  });

  bus.subscribe('board:piece-dropped', () => {
    totals.moves += 1;
    if (pending) pending.dropped = true;
  });

  bus.subscribe('board:updated', () => {
    if (pending?.dropped && pending.placedMs === null) pending.placedMs = elapsed();
  });

  bus.subscribe('turn:changed', ({ reason }) => {
    if (pending && reason === 'move') pending.turnPassed = true;
  });

  bus.subscribe('status:report', () => {
    if (pending?.turnPassed && pending.turnMs === null) pending.turnMs = elapsed();
  });

  bus.subscribe('board:win', () => {
    totals.gamesPlayed += 1;
    if (pending) pending.winMs = elapsed();
  });

  bus.subscribe('board:full', () => {
    totals.gamesPlayed += 1;
  });

  bus.subscribe('clock:expired', () => {
    totals.timeouts += 1;
    publishMetrics();
  });

  bus.subscribe('window:opened', publishMetrics);
}
