// ---- Metrics ----
// Keeps running totals of games, moves and timeouts.
//
// Listens: board:piece-dropped, board:win, board:full, clock:expired, window:opened
// Publishes: metrics:updated
export function registerMetrics(bus) {
  const totals = { gamesPlayed: 0, moves: 0, timeouts: 0 };

  const publishTotals = () => bus.publish('metrics:updated', { ...totals });
  const count = (key) => () => {
    totals[key] += 1;
    publishTotals();
  };

  bus.subscribe('board:piece-dropped', count('moves'));
  bus.subscribe('board:win', count('gamesPlayed'));
  bus.subscribe('board:full', count('gamesPlayed'));
  bus.subscribe('clock:expired', count('timeouts'));
  bus.subscribe('window:opened', publishTotals);
}
