import paho.mqtt.client as mqtt

class EventClient:
    def __init__(self, host, port, on_connect=None):
        self._host = host
        self._port = port
        self._on_connected = on_connect
        self._subscriptions = set()

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.on_connect = self._on_connect

    def subscribe(self, topic, handler):
        self._client.message_callback_add(topic, handler)
        self._subscriptions.add(topic)

        if self._client.is_connected():
            self._client.subscribe(topic)

    def run(self):
        try:
            self._client.connect(self._host, self._port)
            self._client.loop_forever()
        finally:
            self.disconnect()

    def disconnect(self):
        self._client.disconnect()

    def _on_connect(
        self, client, userdata, flags, reason_code, properties
    ):
        if reason_code.is_failure:
            return

        for topic in self._subscriptions:
            client.subscribe(topic)

        if self._on_connected is not None:
            self._on_connected()

    def publish(self, topic, payload):
        return self._client.publish(topic, payload)
