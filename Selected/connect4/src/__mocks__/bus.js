let handlers = {};
let allHandlers = new Set();

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

  subscribeAll(handler) {
    allHandlers.add(handler);
    return () => allHandlers.delete(handler);
  },

  close() {},

  deliver(event, payload) {
    allHandlers.forEach((handler) => handler(event, payload));
    handlers[event]?.forEach((handler) => handler(payload));
  },

  reset() {
    handlers = {};
    allHandlers = new Set();
    bus.published = [];
  },
};
