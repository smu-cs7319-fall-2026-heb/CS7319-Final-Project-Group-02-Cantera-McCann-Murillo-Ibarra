import { registerBoardLogic } from './boardLogic';
import { registerTurnLogic } from './turnLogic';
import { registerStatus } from './status';
import { registerStatusLogic } from './statusLogic';
import { registerClock } from './clock';
import { registerMetrics } from './metrics';

// Plugs every logic component into the bus. These have no UI; they only
// listen for events and publish new ones. Returns a function that stops the
// clock (used by tests).
export function startLogic(bus) {
  registerMetrics(bus);
  registerStatus(bus);
  registerTurnLogic(bus);
  registerBoardLogic(bus);
  registerStatusLogic(bus);
  const clock = registerClock(bus);
  return clock.stop;
}
