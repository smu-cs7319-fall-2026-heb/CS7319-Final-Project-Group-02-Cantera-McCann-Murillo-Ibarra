import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import {
  createBoard,
  getDropRow,
  placePiece,
  findWinningLine,
  isBoardFull,
} from './utils/gameLogic';

test('renders the game with Red to move first', () => {
  render(<App />);
  expect(screen.getByText(/connect four/i)).toBeInTheDocument();
  expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent("Red's turn");
});

test('clicking a column drops a piece and switches turns', () => {
  render(<App />);
  fireEvent.click(screen.getAllByLabelText('Drop in column 1')[0]);
  expect(screen.getAllByLabelText('red piece')).toHaveLength(1);
  expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent("Yellow's turn");
});

test('pieces drop to the lowest empty row', () => {
  let board = createBoard();
  expect(getDropRow(board, 3)).toBe(5);
  board = placePiece(board, 5, 3, 'red');
  expect(getDropRow(board, 3)).toBe(4);
});

test('detects horizontal, vertical and diagonal wins', () => {
  let board = createBoard();
  [0, 1, 2, 3].forEach((c) => (board = placePiece(board, 5, c, 'red')));
  expect(findWinningLine(board, 5, 3)).toHaveLength(4);

  board = createBoard();
  [5, 4, 3, 2].forEach((r) => (board = placePiece(board, r, 0, 'yellow')));
  expect(findWinningLine(board, 2, 0)).toHaveLength(4);

  board = createBoard();
  [[5, 0], [4, 1], [3, 2], [2, 3]].forEach(([r, c]) => (board = placePiece(board, r, c, 'red')));
  expect(findWinningLine(board, 3, 2)).toHaveLength(4);

  board = createBoard();
  [0, 1, 2].forEach((c) => (board = placePiece(board, 5, c, 'red')));
  expect(findWinningLine(board, 5, 2)).toBeNull();
});

test('detects a full board', () => {
  const full = createBoard().map((row) => row.map(() => 'red'));
  expect(isBoardFull(full)).toBe(true);
  expect(isBoardFull(createBoard())).toBe(false);
});
