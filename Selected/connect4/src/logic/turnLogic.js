import { COLS, nextPlayer } from './gameLogic';

export function registerTurnLogic(bus) {
  let currentPlayer = 'red';
  let phase = 'playing';

  const changeTurn = (player, reason, extra = {}) => {
    currentPlayer = player;
    bus.publish('turn:changed', { player, reason, ...extra });
  };

  bus.subscribe('game:phase', ({ phase: next }) => {
    phase = next;
  });

  bus.subscribe('player:column-clicked', ({ col }) => {
    if (phase !== 'playing') return;
    if (!Number.isInteger(col) || col < 0 || col >= COLS) return;
    bus.publish('turn:move', { col, player: currentPlayer });
  });

  bus.subscribe('board:piece-dropped', ({ player, result }) => {
    if (result) return;
    changeTurn(nextPlayer(player), 'move');
  });

  bus.subscribe('clock:expired', () => {
    if (phase !== 'playing') return;
    changeTurn(nextPlayer(currentPlayer), 'timeout', { skipped: currentPlayer });
  });

  bus.subscribe('window:new-game', () => changeTurn('red', 'new-game'));
}
