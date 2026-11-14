import { createServer } from 'node:http';
import { Server } from 'socket.io';

const QUIET_EVENTS = new Set([
  'clock:tick',
  'player:column-hovered',
  'board:updated',
  'status:report',
  'metrics:updated',
]);

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: 'http://localhost:3000' }, 
});

io.on('connection', (socket) => {
  console.log('window connected:', socket.id);

  socket.onAny((event, payload = {}) => {
    if (!QUIET_EVENTS.has(event)) console.log(`[bus] ${event}`, JSON.stringify(payload));
    socket.emit(event, payload);
  });

  socket.on('disconnect', () => console.log('window disconnected:', socket.id));
});

httpServer.listen(4000, () => console.log('Bus server on http://localhost:4000'));
