import { createServer } from 'node:http';
import { Server } from 'socket.io';

// ---- Centralized Event Router ----
// The only backend piece. Components in the React app publish events here,
// and the router sends each one back out to the subscribers in that window.
// It has no game logic and does not know who sent or who receives an event.

// Events that fire too often to be worth logging.
const QUIET_EVENTS = new Set([
  'clock:tick',
  'player:column-hovered',
  'board:updated',
  'status:report',
  'metrics:updated',
]);

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: 'http://localhost:3000' }, // your React dev server
});

io.on('connection', (socket) => {
  console.log('window connected:', socket.id);

  socket.onAny((event, payload = {}) => {
    if (!QUIET_EVENTS.has(event)) console.log(`[bus] ${event}`, JSON.stringify(payload));
    // Each window is its own game, so events go back to that window only.
    // (Broadcasting with io.emit would make every open tab's Board Logic
    // answer every click.)
    socket.emit(event, payload);
  });

  socket.on('disconnect', () => console.log('window disconnected:', socket.id));
});

httpServer.listen(4000, () => console.log('Bus server on http://localhost:4000'));
