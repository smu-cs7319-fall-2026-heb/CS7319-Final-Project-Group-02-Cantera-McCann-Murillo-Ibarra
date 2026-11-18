export const ROWS = 6;
export const COLS = 7;


export const PLAYER_NAMES = { red: 'Red', yellow: 'Yellow' };

const DIRECTIONS = [
  [0, 1], 
  [1, 0], 
  [1, 1], 
  [1, -1], 
];

export const createBoard = () =>
  Array.from({ length: ROWS }, () => Array(COLS).fill(null));

export const nextPlayer = (player) => (player === 'red' ? 'yellow' : 'red');

export function getDropRow(board, col) {
  for (let row = ROWS - 1; row >= 0; row--) {
    if (!board[row][col]) return row;
  }
  return -1;
}

export function placePiece(board, row, col, player) {
  return board.map((cells, r) =>
    r === row ? cells.map((cell, c) => (c === col ? player : cell)) : cells
  );
}

export function findWinningLine(board, row, col) {
  const player = board[row][col];
  if (!player) return null;

  for (const [dr, dc] of DIRECTIONS) {
    const line = [[row, col]];
    for (const sign of [1, -1]) {
      let r = row + dr * sign;
      let c = col + dc * sign;
      while (r >= 0 && r < ROWS && c >= 0 && c < COLS && board[r][c] === player) {
        line.push([r, c]);
        r += dr * sign;
        c += dc * sign;
      }
    }
    if (line.length >= 4) return line;
  }
  return null;
}

export const isBoardFull = (board) => board[0].every(Boolean);
