import paho.mqtt.client as mqtt


class EventClient:
    def __init__(self, host: str, port: int) -> None:
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.connect(host, port)
        self._client.loop_start()

    def publish(self, topic: str, payload: str) -> None:
        self._client.publish(topic, payload).wait_for_publish()
