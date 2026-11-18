import { bus } from '../bus';
import { startLogic } from '../logic';
import { summarize } from '../logic/metrics';

const GAMES = Number(process.env.GAMES) || 15;
const WARMUP_GAMES = 1;
const GAME_MOVES = [0, 1, 0, 1, 0, 1, 0];

let latestMetrics = null;
let stopClock = () => {};

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitFor(condition, what, timeoutMs = 5000) {
  const start = Date.now();
  while (!condition()) {
    if (Date.now() - start > timeoutMs) throw new Error(`Timed out waiting for ${what}`);
    await wait(5);
  }
}

afterAll(() => {
  stopClock();
  bus.close();
});

test(
  'move benchmark',
  async () => {
    bus.subscribe('metrics:updated', (metrics) => (latestMetrics = metrics));
    stopClock = startLogic(bus);
    bus.publish('window:opened');
    await waitFor(() => latestMetrics, 'the bus server (is `node server` running?)');

    for (let game = 0; game < WARMUP_GAMES + GAMES; game++) {
      bus.publish('window:new-game');
      await wait(100);
      for (const col of GAME_MOVES) {
        const before = latestMetrics.samples.length;
        bus.publish('player:column-clicked', { col, clickedAt: performance.now() });
        await waitFor(() => latestMetrics.samples.length > before, 'a move to be measured');
      }
    }

    const samples = latestMetrics.samples.slice(WARMUP_GAMES * GAME_MOVES.length);
    const column = (key) => samples.map((s) => s[key]).filter((v) => v !== null);
    const rows = [
      ['placed (click -> board:updated)', summarize(column('placedMs')), 'ms'],
      ['turn passed (click -> status:report)', summarize(column('turnMs')), 'ms'],
      ['win detected (click -> board:win)', summarize(column('winMs')), 'ms'],
      ['messages per move', summarize(column('messages')), ''],
    ];

    const lines = rows.map(
      ([label, s, unit]) =>
        `${label.padEnd(38)} n=${String(s.count).padEnd(4)} median=${s.median}${unit}  p95=${s.p95}${unit}`
    );
    console.log(`Event-based move benchmark (${GAMES} games, after ${WARMUP_GAMES} warm-up)\n${lines.join('\n')}`);
    expect(samples).toHaveLength(GAMES * GAME_MOVES.length);
  },
  10 * 60 * 1000
);
