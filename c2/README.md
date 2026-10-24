[devcontainer]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
[vs code]: https://code.visualstudio.com/
[board_domain_example.yaml]: c2/context/board_domain_example.yaml

# c2

## how to run 
1. Install Docker (choose wsl when asked) 
2. Run `docker compose up --build` From `final_project/c2` (the directory containing `compose.yaml`)  

Note: no GUI available yet  

 

## Development

### devcontainer 
1. install [vs code]
2. Install the [devcontainer] extension for vs code.
3. open the command pallet (ctrl-shift-p) 
4. pick **Dev Container: Open folder in Container...** 
5. then pick final_project/c2 (bc it has the .devcontainer/ directory)
6. wait for vs code to build and open the devcontainer 

### listen to all messages on the connector-state connector (mqtt broker)  

```sh
mosquitto_sub --host connector-state --topic '#' --verbose
```
### Compile clock component

```sh
mkdir -p /tmp/build
cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/
cmake --build /tmp/build/
# one-liner for easy copying 
mkdir -p /tmp/build && cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/ && cmake --build /tmp/build/
```



## TODO
- [ ] Set up each broker in Docker Compose using the config files in `c2/connectors/`.
- [ ] Use a shared domain file for components. See [board_domain_example.yaml] in `c2/context/`.
