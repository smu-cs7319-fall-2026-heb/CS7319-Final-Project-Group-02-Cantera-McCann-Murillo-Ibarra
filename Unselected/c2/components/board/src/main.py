import os

from component import Component


def main():
    host = os.getenv("MQTT_HOST", "connector-model")
    port = int(os.getenv("MQTT_PORT", "1883"))

    component = Component(host, port)

    component.run()


if __name__ == "__main__":
    main()
