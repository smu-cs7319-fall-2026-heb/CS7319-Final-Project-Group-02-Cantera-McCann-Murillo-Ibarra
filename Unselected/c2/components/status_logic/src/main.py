import os

from component import Component


def main():
    top_host = os.getenv("TOP_MQTT_HOST", "connector-controller")
    top_port = int(os.getenv("TOP_MQTT_PORT", "1883"))
    turn_seconds = int(os.getenv("TURN_SECONDS", "30"))

    component = Component(top_host, top_port, turn_seconds)

    component.run()


if __name__ == "__main__":
    main()
