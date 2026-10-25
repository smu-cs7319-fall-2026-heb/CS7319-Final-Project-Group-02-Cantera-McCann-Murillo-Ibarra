import { io } from 'socket.io-client';

// One connection for the whole app. Every component imports this
// instead of opening its own connection.
export const socket = io('http://localhost:4000');