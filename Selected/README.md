# Connect 4 (Event Based)

The app has two parts: a bus server (`server/`) and the React client (`connect4/`). Run each one in its own terminal.

## 1. Start the server

```
cd event_based
cd server
npm i
node server
```

You should see `Bus server on http://localhost:4000`. Leave this terminal running.

## 2. Start the client

In a second terminal, starting from `event_based/server`:

```
cd ..
cd connect4
npm i
npm start
```

The game opens at [http://localhost:3000](http://localhost:3000).

## Architecture

- **Backend:** `server/server.js` is the Centralized Event Router. It has no game logic. It receives every event and sends it back out to the subscribers.
- **Frontend:** every other component lives in the React app. Each one publishes events to the router and subscribes to the events it cares about. Components never call each other directly.

| Component | File | Publishes |
| --- | --- | --- |
| Centralized Event Router | `server/server.js` | (routes everything) |
| Board Logic | `connect4/src/logic/boardLogic.js` | `board:*` |
| TurnLogic | `connect4/src/logic/turnLogic.js` | `turn:move`, `turn:changed` |
| Status | `connect4/src/logic/status.js` | `game:phase` |
| Status Logic | `connect4/src/logic/statusLogic.js` | `status:report` |
| Clock | `connect4/src/logic/clock.js` (display: `components/Clock.js`) | `clock:*` |
| Metrics | `connect4/src/logic/metrics.js` | `metrics:updated` |
| Player | `connect4/src/components/Player.js` | `player:*` |
| BoardArtist | `connect4/src/components/BoardArtist.js` | (draws only) |
| StatusArtist | `connect4/src/components/StatusArtist.js` | (draws only) |
| WindowingManager | `connect4/src/components/WindowingManager.js` | `window:*` |

Components in `src/logic/` have no UI. They are started once in `src/index.js`. Components in `src/components/` are what you see on screen.

## Metrics

The Metrics component (`connect4/src/logic/metrics.js`) measures every move, starting from the moment Player sends the click:

| Metric | Measured from | To |
| --- | --- | --- |
| Piece placed | `player:column-clicked` | `board:updated` with the new piece |
| Turn passed | `player:column-clicked` | `status:report` after `turn:changed` |
| Win detected | `player:column-clicked` (winning move) | `board:win` |
| Messages per move | every bus event caused by the move, counting the click | |

`clock:tick`, `player:column-hovered` and `metrics:updated` are left out of the message count. The footer under the game shows the last move and the medians.

To collect numbers for a report, start the server (step 1 above), then in a second terminal:

```
cd connect4
npm run benchmark
```

This plays 15 scripted games (105 moves) after one warm-up game and prints the median and 95th percentile of each metric. For more games, use `GAMES=30 npm run benchmark` in Git Bash, or `$env:GAMES=30; npm run benchmark` in PowerShell.

## Tests

```
cd connect4
npm test
```
