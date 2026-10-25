export const ROWS = 6;
export const COLS = 7;

export const PLAYERS = {
  red: { name: 'Red', color: 'danger' },
  yellow: { name: 'Yellow', color: 'warning' },
};

const DIRECTIONS = [
  [0, 1], // horizontal
  [1, 0], // vertical
  [1, 1], // diagonal down-right
  [1, -1], // diagonal down-left
];

export const createBoard = () =>
  Array.from({ length: ROWS }, () => Array(COLS).fill(null));

export const nextPlayer = (player) => (player === 'red' ? 'yellow' : 'red');

// Returns the lowest empty row in a column, or -1 if the column is full.
export function getDropRow(board, col) {
  for (let row = ROWS - 1; row >= 0; row--) {
    if (!board[row][col]) return row;
  }
  return -1;
}

// Returns a new board with the piece placed (does not mutate the original).
export function placePiece(board, row, col, player) {
  return board.map((cells, r) =>
    r === row ? cells.map((cell, c) => (c === col ? player : cell)) : cells
  );
}

// Checks every line through the last move. Returns the winning cells as
// [row, col] pairs, or null if the move did not win.
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
