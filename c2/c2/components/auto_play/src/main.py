import os

from component import Component


def main():
    top_host = os.getenv("TOP_MQTT_HOST", "connector-view")
    top_port = int(os.getenv("TOP_MQTT_PORT", "1883"))
    games = int(os.getenv("GAMES", "10"))

    component = Component(top_host, top_port, games)

    component.run()


if __name__ == "__main__":
    main()
