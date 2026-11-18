import { io } from 'socket.io-client';

const socket = io('http://localhost:4000');

export const bus = {
  publish(event, payload = {}) {
    socket.emit(event, payload);
  },

  subscribe(event, handler) {
    socket.on(event, handler);
    return () => socket.off(event, handler);
  },

  subscribeAll(handler) {
    socket.onAny(handler);
    return () => socket.offAny(handler);
  },

  close() {
    socket.close();
  },
};
