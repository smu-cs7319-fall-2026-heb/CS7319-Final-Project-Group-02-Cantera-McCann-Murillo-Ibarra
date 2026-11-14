import { render, screen, fireEvent, act } from '@testing-library/react';
import App from './App';
import { bus } from './bus';
import { emptyBoard } from './constants';

jest.mock('./bus');

const deliver = (event, payload) => act(() => bus.deliver(event, payload));
const published = (event) => bus.published.filter((e) => e.event === event);
const heading = () => screen.getByRole('heading', { level: 3 });

const report = (overrides) => ({
  currentPlayer: 'red',
  winner: null,
  isDraw: false,
  notice: '',
  scores: { red: 0, yellow: 0, draws: 0 },
  ...overrides,
});

beforeEach(() => bus.reset());

test('opening the window asks the logic components for their current state', () => {
  render(<App />);
  expect(published('window:opened')).toHaveLength(1);
  expect(screen.getByText(/connect four/i)).toBeInTheDocument();
  expect(heading()).toHaveTextContent("Red's turn");
});

test('clicking a column only publishes the click; the board waits for Board Logic', () => {
  render(<App />);
  fireEvent.click(screen.getByLabelText('Drop in column 1'));

  expect(published('player:column-clicked')).toEqual([
    { event: 'player:column-clicked', payload: { col: 0, clickedAt: expect.any(Number) } },
  ]);
  expect(screen.queryAllByLabelText('red piece')).toHaveLength(0);

  const board = emptyBoard();
  board[5][0] = 'red';
  deliver('board:updated', { board, winningCells: [] });
  deliver('status:report', report({ currentPlayer: 'yellow' }));

  expect(screen.getAllByLabelText('red piece')).toHaveLength(1);
  expect(heading()).toHaveTextContent("Yellow's turn");
});

test('StatusArtist draws the winner, notice and scores it is sent', () => {
  render(<App />);
  deliver('status:report', report({ winner: 'yellow', scores: { red: 2, yellow: 3, draws: 1 } }));
  expect(heading()).toHaveTextContent('Yellow wins!');
  expect(screen.getByText('Yellow: 3')).toBeInTheDocument();
  expect(screen.getByText('Draws: 1')).toBeInTheDocument();

  deliver('status:report', report({ notice: 'That column is full, pick another one.' }));
  expect(screen.getByText('That column is full, pick another one.')).toBeInTheDocument();
});

test('window controls publish requests and follow the game phase', () => {
  render(<App />);
  fireEvent.click(screen.getByText('Pause'));
  expect(published('window:pause')).toHaveLength(1);

  deliver('game:phase', { phase: 'paused' });
  fireEvent.click(screen.getByText('Resume'));
  expect(published('window:resume')).toHaveLength(1);

  fireEvent.click(screen.getByText('30s'));
  expect(published('window:duration-changed')[0].payload).toEqual({ seconds: 30 });

  fireEvent.click(screen.getByText('New Game'));
  fireEvent.click(screen.getByText('Reset Scores'));
  expect(published('window:new-game')).toHaveLength(1);
  expect(published('window:reset-scores')).toHaveLength(1);
});

test('the clock shows published ticks and hides when the game is over', () => {
  render(<App />);
  deliver('clock:tick', { timeLeft: 7, duration: 20, running: false });
  expect(screen.getByText('7s (paused)')).toBeInTheDocument();

  deliver('game:phase', { phase: 'over' });
  expect(screen.queryByText('Turn timer')).not.toBeInTheDocument();
});

test('hovering shows a preview piece in the lowest empty row', () => {
  const { container } = render(<App />);
  fireEvent.mouseEnter(screen.getByLabelText('Drop in column 4'));
  expect(published('player:column-hovered')[0].payload).toEqual({ col: 3 });

  deliver('player:column-hovered', { col: 3 });
  expect(container.querySelectorAll('.cell--preview-red')).toHaveLength(1);
});
