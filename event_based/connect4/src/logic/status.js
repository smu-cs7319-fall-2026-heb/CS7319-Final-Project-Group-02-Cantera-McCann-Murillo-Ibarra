export function registerStatus(bus) {
  let phase = 'playing';

  const setPhase = (next) => {
    phase = next;
    bus.publish('game:phase', { phase });
  };

  bus.subscribe('window:pause', () => {
    if (phase === 'playing') setPhase('paused');
  });

  bus.subscribe('window:resume', () => {
    if (phase === 'paused') setPhase('playing');
  });

  bus.subscribe('window:new-game', () => setPhase('playing'));
  bus.subscribe('board:win', () => setPhase('over'));
  bus.subscribe('board:full', () => setPhase('over'));

  bus.subscribe('window:opened', () => bus.publish('game:phase', { phase }));
}
