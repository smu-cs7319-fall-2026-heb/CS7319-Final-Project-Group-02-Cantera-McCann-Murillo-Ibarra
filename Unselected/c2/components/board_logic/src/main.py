import os

from component import Component


def main():
    top_host = os.getenv("TOP_MQTT_HOST", "connector-model")
    top_port = int(os.getenv("TOP_MQTT_PORT", "1883"))
    bottom_host = os.getenv("BOTTOM_MQTT_HOST", "connector-controller")
    bottom_port = int(os.getenv("BOTTOM_MQTT_PORT", "1883"))

    component = Component(top_host, top_port, bottom_host, bottom_port)

    component.run()


if __name__ == "__main__":
    main()
