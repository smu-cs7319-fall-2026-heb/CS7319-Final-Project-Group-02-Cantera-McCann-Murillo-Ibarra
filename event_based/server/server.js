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

// ---- Bridge: browser → bus ----
const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: 'http://localhost:3000' }, // your React dev server
});

const TIMER_EVENTS = ['timer:started', 'timer:paused', 'timer:resumed', 'timer:expired'];

io.on('connection', (socket) => {
  console.log('browser connected:', socket.id);

  // Pass each allowed browser event onto the bus
  for (const event of TIMER_EVENTS) {
    socket.on(event, (payload) => bus.emit(event, payload));
  }

  socket.on('disconnect', () => console.log('browser disconnected:', socket.id));
});

httpServer.listen(4000, () => console.log('Bus server on http://localhost:4000'));