import os

from component import Component


def main():
    bottom_host = os.getenv("BOTTOM_MQTT_HOST", "connector-controller")
    bottom_port = int(os.getenv("BOTTOM_MQTT_PORT", "1883"))

    component = Component(bottom_host, bottom_port)

    component.run()


if __name__ == "__main__":
    main()
