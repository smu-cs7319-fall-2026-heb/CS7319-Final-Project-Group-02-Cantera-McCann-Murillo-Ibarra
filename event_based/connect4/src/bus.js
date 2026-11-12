import { io } from 'socket.io-client';

// The app's connection to the Centralized Event Router (the server).
// Every component, visual or logic, only publishes and subscribes here.
// A published event travels to the server, which sends it back to every
// subscriber in this window, so components never call each other.
const socket = io('http://localhost:4000');

export const bus = {
  publish(event, payload = {}) {
    socket.emit(event, payload);
  },

  // Returns an unsubscribe function, so it can be returned from useEffect.
  subscribe(event, handler) {
    socket.on(event, handler);
    return () => socket.off(event, handler);
  },
};
