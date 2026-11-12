import { bus } from '../bus';
import { startLogic } from '.';
import {
  createBoard,
  getDropRow,
  placePiece,
  findWinningLine,
  isBoardFull,
} from './gameLogic';

// The logic components run against the in-memory bus (src/__mocks__/bus.js),
// which sends every event straight back like the real server does.
jest.mock('../bus');

let stopClock;

const publish = (event, payload = {}) => bus.publish(event, payload);
const last = (name) => bus.published.filter((e) => e.event === name).at(-1)?.payload;
const names = () => bus.published.map((e) => e.event);
const click = (...cols) => cols.forEach((col) => publish('player:column-clicked', { col }));
const clearLog = () => (bus.published = []);

beforeEach(() => {
  jest.useFakeTimers();
  bus.reset();
  stopClock = startLogic(bus);
  publish('window:opened');
});

afterEach(() => {
  stopClock();
  jest.useRealTimers();
});

describe('game rules', () => {
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
});

describe('logic components talking over the bus', () => {
  test('opening a window gets a snapshot from every component', () => {
    for (const name of [
      'board:updated',
      'status:report',
      'game:phase',
      'clock:configured',
      'clock:tick',
      'metrics:updated',
    ]) {
      expect(names()).toContain(name);
    }
    expect(last('status:report').currentPlayer).toBe('red');
  });

  test('a click becomes a move, a dropped piece, and a turn change', () => {
    click(0);
    expect(last('turn:move')).toEqual({ col: 0, player: 'red' });
    expect(last('board:piece-dropped')).toEqual({ row: 5, col: 0, player: 'red', result: null });
    expect(last('board:updated').board[5][0]).toBe('red');
    expect(last('turn:changed').player).toBe('yellow');
    expect(last('status:report').currentPlayer).toBe('yellow');
    expect(last('metrics:updated').moves).toBe(1);
  });

  test('four in a row wins, ends the game, and scores it', () => {
    click(0, 1, 0, 1, 0, 1, 0); // red stacks column 1
    expect(last('board:win').player).toBe('red');
    expect(last('board:updated').winningCells).toHaveLength(4);
    expect(last('game:phase').phase).toBe('over');
    expect(last('status:report')).toMatchObject({ winner: 'red', scores: { red: 1 } });
    expect(last('metrics:updated').gamesPlayed).toBe(1);

    clearLog();
    click(2);
    expect(names()).not.toContain('turn:move');
  });

  test('a full column produces a notice and keeps the turn', () => {
    click(0, 0, 0, 0, 0, 0); // fills column 1 without four in a row
    clearLog();
    click(0);
    expect(names()).toContain('board:column-full');
    expect(last('status:report').notice).toBe('That column is full, pick another one.');
    expect(names()).not.toContain('turn:changed');
  });

  test('pausing blocks moves and stops the clock until resumed', () => {
    publish('window:pause');
    expect(last('game:phase').phase).toBe('paused');
    expect(last('clock:tick').running).toBe(false);

    clearLog();
    click(3);
    jest.advanceTimersByTime(5000);
    expect(names()).not.toContain('turn:move');
    expect(names()).not.toContain('clock:tick');

    publish('window:resume');
    click(3);
    expect(last('board:piece-dropped').player).toBe('red');
  });

  test('running out of time skips the turn', () => {
    jest.advanceTimersByTime(20000);
    expect(names()).toContain('clock:expired');
    expect(last('turn:changed')).toEqual({ player: 'yellow', reason: 'timeout', skipped: 'red' });
    expect(last('status:report').notice).toBe('Red ran out of time! Turn skipped.');
    expect(last('clock:tick').timeLeft).toBe(20);
  });

  test('changing the turn length restarts the clock with the new length', () => {
    jest.advanceTimersByTime(3000);
    publish('window:duration-changed', { seconds: 10 });
    expect(last('clock:configured').duration).toBe(10);
    expect(last('clock:tick').timeLeft).toBe(10);

    publish('window:duration-changed', { seconds: 999 });
    expect(last('clock:configured').duration).toBe(10);
  });

  test('a new game clears the board but keeps scores until they are reset', () => {
    click(0, 1, 0, 1, 0, 1, 0);
    publish('window:new-game');
    expect(last('board:updated').board.flat().every((cell) => !cell)).toBe(true);
    expect(last('game:phase').phase).toBe('playing');
    expect(last('status:report')).toMatchObject({
      winner: null,
      currentPlayer: 'red',
      scores: { red: 1 },
    });

    publish('window:reset-scores');
    expect(last('status:report').scores).toEqual({ red: 0, yellow: 0, draws: 0 });
  });

  test('bad column numbers are ignored', () => {
    clearLog();
    click(-1, 7, 'x', 2.5);
    expect(names()).not.toContain('turn:move');
  });
});
