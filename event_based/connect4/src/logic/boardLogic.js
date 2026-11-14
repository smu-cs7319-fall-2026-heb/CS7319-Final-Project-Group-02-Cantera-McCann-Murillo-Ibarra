import {
  createBoard,
  getDropRow,
  placePiece,
  findWinningLine,
  isBoardFull,
} from './gameLogic';

export function registerBoardLogic(bus) {
  let board = createBoard();
  let winningCells = [];

  const publishBoard = () => bus.publish('board:updated', { board, winningCells });

  bus.subscribe('turn:move', ({ col, player }) => {
    const row = getDropRow(board, col);
    if (row === -1) {
      bus.publish('board:column-full', { col, player });
      return;
    }

    board = placePiece(board, row, col, player);
    const line = findWinningLine(board, row, col);
    const full = !line && isBoardFull(board);
    const result = line ? 'win' : full ? 'draw' : null;

    bus.publish('board:piece-dropped', { row, col, player, result });
    if (line) {
      winningCells = line;
      bus.publish('board:win', { player, cells: line });
    } else if (full) {
      bus.publish('board:full', {});
    }
    publishBoard();
  });

  bus.subscribe('window:new-game', () => {
    board = createBoard();
    winningCells = [];
    bus.publish('board:reset', {});
    publishBoard();
  });

  bus.subscribe('window:opened', publishBoard);
}
