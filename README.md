[devcontainer]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
[vs code]: https://code.visualstudio.com/
[board_domain_example.yaml]: c2/context/board_domain_example.yaml

# c2

## how to run 
1. Install Docker (choose wsl when asked) 
2. build and start containers. from the project root run:   
```sh
    docker compose -f c2/compose.yaml up --build
```

Note: use `--attach subscribe_all` to listen to connector messages only, and mute all other compose container output:
```sh
    docker compose -f c2/compose.yaml up --build --attach subscribe_all
```
 

## auto play
run:
```sh
GAMES=20 docker compose -f c2/compose.yaml run --rm --build auto_play
```

Note: `auto_play` resets Status when it starts, so wins and games played start again from 0.

## how to stop containers   
```sh
docker compose -f c2/compose.yaml down  
```

## Development

### devcontainer 
1. install [vs code]
2. Install the [devcontainer] extension for vs code.
3. open the command pallet (ctrl-shift-p) 
4. pick **Dev Container: Open folder in Container...** 
5. then pick final_project/c2 (bc it has the .devcontainer/ directory)
6. wait for vs code to build and open the devcontainer 

### listen to all messages on the connector-model connector (mqtt broker)  
```sh
mosquitto_sub --host connector-model --topic '#' --verbose
```

### Compile clock component
```sh
mkdir -p /tmp/build
cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/
cmake --build /tmp/build/
# one-liner for easy copying 
mkdir -p /tmp/build && cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/ && cmake --build /tmp/build/
```

### test  
1. install the python requirements on host machine  
```sh
python -m pip install -r c2/requirements.txt  
```
2. start containers  
```sh
docker compose -f c2/compose.yaml up      
```
3. run pytest against them 
```sh
python -m pytest c2/test -v   
```

Note: to shorten test runs add `TURN_SECONDS=5`
```sh
TURN_SECONDS=5 docker compose -f c2/compose.yaml up
TURN_SECONDS=5 python -m pytest c2/test -v
```

# Changes
- removed the top domain connection from TurnLogic after implementing it  
    because it's purpose is small and makes no requests or listens to any 
    notifications to/from clock, status or board.   
- renamed connector-state to connector-presenter to connector-controller. 
    The first name was because of the way the book talked about those top layers 
    in the c2 example, then the change to connector-presenter was becaus of preference 
    in MVP (Model View Presenter) over MPC (Model View Controller) but finally 
    the rename to conector-controller bc of the realization that since the GUI 
    can send requests up to the top State components it is actually MVC since
    the View can access the Model.   



# Event Based

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

# Comparison

Implementation Differences Between the Two Architecture Styles
We built Connect 4 twice, once in each candidate style. Both versions have the same component boxes: Board, Status, Clock, Board Logic, Turn Logic, Status Logic, Board Artist, Status Artist, a Layout/Windowing Manager, and a Player/GUI input. The difference is in how these components are packaged, how they talk to each other, and which parts can be reused.

## 1. Overall Structure

### C2 (layered, MQTT)

In the C2 version, each component runs as a separate program in its own Docker container. Docker Compose spins up 16 services: 10 components, 5 MQTT brokers that serve as the connectors, and a logging service that listens in on all of the brokers. There’s also an optional Auto Play component if you want to run a scripted game.

The system is split into layers. At the bottom is the model layer (Board, Status, and Clock). Above that is the logic layer (Board Logic, Turn Logic, and Status Logic), then the view layer (Board Artist and Status Artist), and then the Layout Manager. At the very top, the GUI is a Next.js app called Graphics Binding that connects to the top broker through a WebSocket on port 9001. Each layer can only talk to the broker directly above or below it.

Requests move up the layers and notifications move down. Components don’t know each other by name. They only know which topics to use for the layer above and the layer below.

### Event-Based (central bus)

The event-based version is much simpler on the deployment side. It’s just two programs: a Node.js server that acts as the event bus, and a React app that holds everything else.

The bus server is only 28 lines long. It has no game logic and doesn’t even know what the events are called. Its only job is to take in every event and pass it along to anyone who’s subscribed.

All of the components live in the React app. The ones that handle logic without a UI, like Board Logic, Turn Logic, Status, and Clock, are in src/logic/ and get started once when the app loads. The ones that draw something on screen, like the Player, Board Artist, and Windowing Manager, are in src/components/.

There aren’t any layers here. Any component can send or listen for any event, and none of them call each other directly. The only thing tying them together is the event names they share.

# 2. Languages and Source Code

| | C2 | Event-Based |
| --- | --- | --- |
| Languages | Python (8 components), C++ (Clock), TypeScript/Next.js (GUI) | JavaScript only (Node server and React) |
| Messaging library | paho-mqtt (Python), Boost.Asio with an MQTT client (C++), mqtt.js (GUI) | socket.io (server), socket.io-client (React) |
| Connector software | Eclipse Mosquitto brokers, set up with config files | One small socket.io server we wrote |
| Size of component source | About 3,660 lines of Python and C++, plus the GUI | About 750 lines, not counting tests |
| How to run | `docker compose up --build` (16 containers) | `node server`, then `npm start` |


In the C2 version, every Python component is built the same way. main.py grabs the broker’s host and port from environment variables and starts things up. event_client.py handles the MQTT connection, including connecting, subscribing, publishing, and re-subscribing if the connection drops. domain.py sets up the component’s top and bottom domains and builds the full topic names from them, like c2/connector-model/board/bottom_domain/requests/request_result. component.py connects each topic to the function that handles it and sends out requests and notifications. Finally, there’s a logic file, like board.py or board_logic.py, that holds the actual game rules and doesn’t touch any messaging code.

Components that sit between two layers, like Board Logic, the Artists, and the Layout Manager, need two MQTT connections, one for the connector above and one for the connector below. Each connection runs on its own thread, so any shared data has to be protected with a lock (you can see this in board_logic/src/component.py).

The event-based components are a lot smaller, since the bus takes care of all the connection work. A logic component is just one register...(bus) function that listens for certain events and publishes new ones. For example, Board Logic listens for turn:move and sends out board:piece-dropped, board:win, board:full, and board:updated. An artist component is just a React function that takes the latest event data and draws it on the screen.

# 3. Connectors

## C2

The connectors in C2 are actual message brokers (Mosquitto), with one broker for each boundary between layers.

Some of the brokers are linked together with bridges that are set up in their config files. For example, connector-controller and connector-view are both bridged to connector-model. They pass bottom_domain/requests topics up to the model and send bottom_domain/notifications topics back down. All of the bridges use QoS 0, which means each message is delivered at most once.

Messages get routed based on the topic name. The topic tells you which broker it’s on, which component it’s for, whether it’s the top or bottom domain, and what type of message it is.

Since the brokers are ready-made software, we didn’t have to write any connector code. It’s all handled through configuration.

## Event-Based

The event-based version only has one connector, which is the socket.io bus server. Every component connects to it.

Instead of routing by layer, messages are routed by event name, like player:column-clicked or clock:tick.

The server only sends each event back to the browser window it came from, so every window runs its own separate game. We set it up this way because when we broadcast to all windows, the Board Logic in every open tab responded to the same click.

Components don’t use socket.io directly. Instead, they go through a small wrapper in src/bus.js that has publish, subscribe, subscribeAll, and close.

# 4. Reusable Components and Connectors

## Reusable in C2

Mosquitto brokers: All 5 connectors use the same broker image. The only thing that changes between them is the config file.

EventClient: All the Python components use the same event_client.py file, and the copies are identical. However, it’s reused by copying the file instead of sharing it as a package, so any fix has to be made in all of the different places.

Domain pattern: Every component sets up its topics the same way, with a top domain and a bottom domain that each have requests and notifications. domain.py takes that setup and turns it into the actual topic names.

Graphics Binding widgets: The GUI only draws basic widgets (badge, bar, button, caption, circle, heading, rectangle, and text) in the positions the Layout Manager tells it to. It doesn’t know anything about Connect 4, so it could be reused for a different board game.

Testability: Each component can take an optional publish function, so tests can swap out the real broker for a fake one.

Reusable in Event-Based

Bus server: The server never looks at event names or what’s inside them, so it could route events for any application without being changed.

bus.js wrapper: This is one shared module that every component uses. If we ever swapped out socket.io, this would be the only file we’d need to change.

useBusEvent hook (src/useBusEvent.js): This is a shared React hook that every artist uses. It subscribes to an event and gives back the most recent data. Because of this, a new display component only needs one line to get its data.

gameLogic.js: This file holds just the Connect 4 rules, like finding which row a piece drops into, placing a piece, checking for a winning line, and checking if the board is full. It doesn’t have any messaging code, so both Board Logic and the tests can use it directly.

Mock bus (src/__mocks__/bus.js): This is an in-memory version of the bus that lets us test all the logic components together without starting the server.

New components can be added without changing any of the existing ones. For example, we added the Metrics component later on. It subscribes to every event using subscribeAll so it can count messages and time each move, and we didn’t have to change any other component to make it work.

# 5. How One Move Travels Through Each System

## C2

The player clicks a column in the Graphics Binding GUI. It sends a click request to connector-layout.
Layout Manager passes the click up to Board Artist, which turns it into a move request.
The request goes up through connector-view and across the bridge to the logic layer.
Board Logic holds the move until the next Clock tick. The Clock publishes one tick per second. On the tick, Board Logic asks Board to place the piece.
Board places the piece and publishes the new state on connector-model. Board Logic checks for a win or draw, and Turn Logic and Status Logic update the turn and status.
The notifications come back down through the artists and Layout Manager to the GUI.
Because Board Logic waits for the tick, a move can wait anywhere from 0 to 1000 ms before it is processed.

## Event-Based

Player publishes player:column-clicked.
Turn Logic checks that the game is running and the column is valid, then publishes turn:move.
Board Logic places the piece, checks for a win or draw, and publishes board:piece-dropped (with the result) and board:updated.
Turn Logic passes the turn (turn:changed), and Status Logic publishes status:report.
Board Artist and Status Artist redraw as soon as their events arrive.
A normal move takes 6 bus messages, and a winning move takes 7. In our benchmark (15 games, 105 moves on localhost), placing a piece took a median of 4.8 ms (6.5 ms p95), and passing the turn took a median of 5.7 ms (7.6 ms p95).

# 6. Summary of the Main Differences

## Packaging
C2 has many separate programs in separate containers. Event-based has one server plus one front-end app.
## Connectors
C2 uses 5 brokers joined by bridges, routed by layered topic names. Event-based uses one bus routed by event names.
## Rules about who can talk to whom
C2 enforces layers (requests up, notifications down). Event-based lets any component publish or subscribe to anything.
## Timing
C2's Board Logic is driven by the Clock tick. Event-based components react the moment an event arrives.
# Reuse
C2 reuses off-the-shelf brokers and generic GUI widgets, but copies its client code into each component. Event-based reuses one bus wrapper, one hook and one rules module across all components, and its server is fully generic.
# Languages
C2 mixes Python, C++ and TypeScript, which shows the style's language independence. Event-based is JavaScript only, which is simpler to build and run.

