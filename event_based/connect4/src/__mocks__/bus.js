// In-memory stand-in for the server, used by tests via jest.mock('./bus').
// Like the real server, every published event is sent straight back to the
// subscribers. Tests read `bus.published` to see what was sent, and call
// `bus.deliver(event, payload)` to inject an event themselves.
let handlers = {};

export const bus = {
  published: [],

  publish(event, payload = {}) {
    bus.published.push({ event, payload });
    bus.deliver(event, payload);
  },

  subscribe(event, handler) {
    (handlers[event] ??= new Set()).add(handler);
    return () => handlers[event].delete(handler);
  },

  deliver(event, payload) {
    handlers[event]?.forEach((handler) => handler(payload));
  },

  reset() {
    handlers = {};
    bus.published = [];
  },
};
