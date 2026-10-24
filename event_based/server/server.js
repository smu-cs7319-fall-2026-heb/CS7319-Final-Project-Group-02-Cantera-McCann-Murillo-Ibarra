import { createServer } from 'node:http';
import { EventEmitter } from 'node:events';
import { Server } from 'socket.io';

// ---- The bus ----
const bus = new EventEmitter();

// ---- Consumers (subscribers) ----
// Each one only listens to the bus. None of them knows who emitted the event.
bus.on('timer:started', ({ duration }) => {
  console.log(`[timer] turn started (${duration}s)`);
});

bus.on('timer:paused', ({ timeLeft }) => {
  console.log(`[timer] paused with ${timeLeft}s left`);
});

bus.on('timer:resumed', ({ timeLeft }) => {
  console.log(`[timer] resumed with ${timeLeft}s left`);
});

bus.on('timer:expired', ({ duration }) => {
  console.log(`[timer] time's up after ${duration}s`);
  // Later: the game engine subscribes here and skips the turn.
});

bus.on('board:column-clicked', ({ col, player }) => {
  console.log(`[board] ${player} clicked column ${col + 1}`);
  // Later: the game engine subscribes here and validates the move.
});

bus.on('board:column-full', ({ col, player }) => {
  console.log(`[board] ${player} tried full column ${col + 1}`);
});

bus.on('board:piece-dropped', ({ row, col, player }) => {
  console.log(`[board] ${player} piece landed at row ${row + 1}, column ${col + 1}`);
});

bus.on('board:win', ({ player, cells }) => {
  console.log(`[board] ${player} wins with ${cells.length} in a row`);
});

bus.on('board:full', () => {
  console.log('[board] board is full, draw');
});

bus.on('board:reset', () => {
  console.log('[board] board cleared for a new game');
});

bus.on('cell:filled', ({ row, col, player }) => {
  console.log(`[cell] (${row + 1}, ${col + 1}) filled by ${player}`);
});

bus.on('cell:cleared', ({ row, col }) => {
  console.log(`[cell] (${row + 1}, ${col + 1}) cleared`);
});

bus.on('cell:highlighted', ({ row, col, player }) => {
  console.log(`[cell] (${row + 1}, ${col + 1}) is part of ${player}'s winning line`);
});

bus.on('controls:new-game', () => {
  console.log('[controls] new game requested');
  // Later: the game engine subscribes here and resets the board.
});

bus.on('controls:pause', () => {
  console.log('[controls] pause pressed');
});

bus.on('controls:resume', () => {
  console.log('[controls] resume pressed');
});

bus.on('controls:reset-scores', () => {
  console.log('[controls] scores reset');
});

bus.on('controls:duration-changed', ({ from, to }) => {
  console.log(`[controls] turn length changed from ${from}s to ${to}s`);
});

bus.on('status:turn-changed', ({ player }) => {
  console.log(`[status] it's now ${player}'s turn`);
});

bus.on('status:winner', ({ player }) => {
  console.log(`[status] showing ${player} as the winner`);
});

bus.on('status:draw', () => {
  console.log('[status] showing a draw');
});

bus.on('status:notice', ({ message }) => {
  console.log(`[status] notice: ${message}`);
});

bus.on('status:scores-updated', ({ scores }) => {
  console.log(`[status] scores: red ${scores.red}, yellow ${scores.yellow}, draws ${scores.draws}`);
});

// ---- Bridge: browser → bus ----
const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: 'http://localhost:3000' }, // your React dev server
});

const TIMER_EVENTS = ['timer:started', 'timer:paused', 'timer:resumed', 'timer:expired'];
const BOARD_EVENTS = [
  'board:column-clicked',
  'board:column-full',
  'board:piece-dropped',
  'board:win',
  'board:full',
  'board:reset',
];
const CELL_EVENTS = ['cell:filled', 'cell:cleared', 'cell:highlighted'];
const CONTROLS_EVENTS = [
  'controls:new-game',
  'controls:pause',
  'controls:resume',
  'controls:reset-scores',
  'controls:duration-changed',
];
const STATUS_EVENTS = [
  'status:turn-changed',
  'status:winner',
  'status:draw',
  'status:notice',
  'status:scores-updated',
];
const ALLOWED_EVENTS = [
  ...TIMER_EVENTS,
  ...BOARD_EVENTS,
  ...CELL_EVENTS,
  ...CONTROLS_EVENTS,
  ...STATUS_EVENTS,
];

io.on('connection', (socket) => {
  console.log('browser connected:', socket.id);

  // Pass each allowed browser event onto the bus
  for (const event of ALLOWED_EVENTS) {
    socket.on(event, (payload) => bus.emit(event, payload));
  }

  socket.on('disconnect', () => console.log('browser disconnected:', socket.id));
});

httpServer.listen(4000, () => console.log('Bus server on http://localhost:4000'));