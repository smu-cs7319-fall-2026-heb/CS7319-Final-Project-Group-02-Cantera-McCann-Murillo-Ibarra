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

Note: no GUI available yet  

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

## TODO
- [ ] Add integration testing.  
- [ ] Add unit testing.  
- [ ] Add component/connector (broker) configuration. 
      (not all brokers will use the default port number for example) 
- [ ] Figure out how to collect empirical data... 
- [ ] Set up each broker in Docker Compose using the config files in `c2/connectors/`.
- [ ] Use a shared domain file for components. See [board_domain_example.yaml] in `c2/context/`.
- [ ] Figure out a way that a double click within a second on the gui does not send two moves for the same player.
