# c2

## Compile clock component

```sh
mkdir -p /tmp/build
cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/
cmake --build /tmp/build/
# one-liner for easy copying 
mkdir -p /tmp/build && cmake -S /workspaces/c2/c2/components/clock/ -B /tmp/build/ && cmake --build /tmp/build/
```

## Development

From the dev container, this will print every message published to the mqtt
broker running in the connector-state Docker Compose service:

```sh
mosquitto_sub --host connector-state --topic '#' --verbose
```

