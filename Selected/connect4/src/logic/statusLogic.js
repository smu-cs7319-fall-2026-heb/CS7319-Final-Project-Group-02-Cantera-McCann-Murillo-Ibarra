import { PLAYER_NAMES } from './gameLogic';

const emptyScores = () => ({ red: 0, yellow: 0, draws: 0 });

export function registerStatusLogic(bus) {
  const state = {
    currentPlayer: 'red',
    winner: null,
    isDraw: false,
    notice: '',
    scores: emptyScores(),
  };

  const report = () => bus.publish('status:report', { ...state, scores: { ...state.scores } });

  bus.subscribe('turn:changed', ({ player, reason, skipped }) => {
    state.currentPlayer = player;
    state.notice =
      reason === 'timeout' ? `${PLAYER_NAMES[skipped]} ran out of time! Turn skipped.` : '';
    report();
  });

  bus.subscribe('board:column-full', () => {
    state.notice = 'That column is full, pick another one.';
    report();
  });

  bus.subscribe('board:win', ({ player }) => {
    state.winner = player;
    state.notice = '';
    state.scores[player] += 1;
    report();
  });

  bus.subscribe('board:full', () => {
    state.isDraw = true;
    state.notice = '';
    state.scores.draws += 1;
    report();
  });

  bus.subscribe('window:new-game', () => {
    state.winner = null;
    state.isDraw = false;
    state.notice = '';
    report();
  });

  bus.subscribe('window:reset-scores', () => {
    state.scores = emptyScores();
    report();
  });

  bus.subscribe('window:opened', report);
}
