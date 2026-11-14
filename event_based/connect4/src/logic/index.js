import { registerBoardLogic } from './boardLogic';
import { registerTurnLogic } from './turnLogic';
import { registerStatus } from './status';
import { registerStatusLogic } from './statusLogic';
import { registerClock } from './clock';
import { registerMetrics } from './metrics';

export function startLogic(bus) {
  registerMetrics(bus);
  registerStatus(bus);
  registerTurnLogic(bus);
  registerBoardLogic(bus);
  registerStatusLogic(bus);
  const clock = registerClock(bus);
  return clock.stop;
}
