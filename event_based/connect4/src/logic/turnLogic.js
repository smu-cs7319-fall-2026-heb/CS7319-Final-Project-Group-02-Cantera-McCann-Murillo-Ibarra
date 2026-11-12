import { COLS, nextPlayer } from './gameLogic';

// ---- TurnLogic ----
// Knows whose turn it is. Turns a player's click into a move for Board Logic
// (only while the game is being played) and passes the turn along after a
// move or when the clock runs out.
//
// Listens: player:column-clicked, board:piece-dropped, clock:expired,
//          game:phase, window:new-game
// Publishes: turn:move, turn:changed
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
    // A winning or drawing move ends the game, so the turn does not pass.
    if (result) return;
    changeTurn(nextPlayer(player), 'move');
  });

  bus.subscribe('clock:expired', () => {
    if (phase !== 'playing') return;
    changeTurn(nextPlayer(currentPlayer), 'timeout', { skipped: currentPlayer });
  });

  bus.subscribe('window:new-game', () => changeTurn('red', 'new-game'));
}
