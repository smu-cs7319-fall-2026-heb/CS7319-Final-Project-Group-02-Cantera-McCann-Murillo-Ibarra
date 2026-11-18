import { ROWS, COLS } from './logic/gameLogic';

export { ROWS, COLS };

export const PLAYERS = {
  red: { name: 'Red', color: 'danger' },
  yellow: { name: 'Yellow', color: 'warning' },
};

export const emptyBoard = () => Array.from({ length: ROWS }, () => Array(COLS).fill(null));
