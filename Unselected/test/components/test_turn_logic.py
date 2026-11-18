import json
import queue
import threading
import time
import unittest
import paho.mqtt.client as mqtt


class TestTurnLogic(unittest.TestCase):
    # class level variables
    _host = "localhost"
    # tests run on the host, so the port is the only way to 
    # differentiate between connectors running behind the docker compose network 
    _controller_port = 1884
    _connection_timeout = 5
    _controller_client = None



    # instance level variables
    _PREFIX = "c2/connector-controller/turn_logic/bottom_domain"
    _RED = 1
    _YELLOW = -1
    _received_timeout = 3
    _subscribed_timeout = 5
    _subscribed = None
    _messages = None

    @classmethod
    def setUpClass(cls):
        try:
            cls._controller_client = cls._connect(cls._controller_port)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls._controller_client is not None:
            cls._controller_client.disconnect()
            cls._controller_client.loop_stop()

    @classmethod
    def _connect(cls, port):
        connected = threading.Event()

        def on_connect(client, userdata, flags, reason_code, properties):
            if not reason_code.is_failure:
                connected.set()

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.connect(cls._host, port)
        client.loop_start()
        if not connected.wait(cls._connection_timeout):
            client.loop_stop()
            raise AssertionError(f"Connection to port {port} timed out")
        return client

    def setUp(self):
        self._subscribed = threading.Event()
        self._messages = queue.Queue()
        self._controller_client.on_subscribe = self._on_subscribe
        self._controller_client.on_message = self._on_message
        try:
            self._controller_client.subscribe([
                (f"{self._PREFIX}/notifications/notify_turn", 0),
                (f"{self._PREFIX}/notifications/notify_reset_turn", 0),
            ])
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        self._controller_client.unsubscribe([
            f"{self._PREFIX}/notifications/notify_turn",
            f"{self._PREFIX}/notifications/notify_reset_turn",
        ])
        self._controller_client.on_subscribe = None
        self._controller_client.on_message = None

    def _request_turn(self):
        self._controller_client.publish(f"{self._PREFIX}/requests/request_turn")

    def _request_reset_turn(self):
        self._controller_client.publish(f"{self._PREFIX}/requests/request_reset_turn")

    def _wait_for(self, topic, result=None):
        deadline = time.monotonic() + self._received_timeout
        while time.monotonic() < deadline:
            remaining = max(0, deadline - time.monotonic())
            try:
                message_topic, payload = self._messages.get(timeout=remaining)
            except queue.Empty:
                break

            # skip stale or unrelated messages until the one we want shows up
            if message_topic != topic:
                continue
            if result is None or payload == result:
                return payload

        self.fail(f"Timed out waiting on {topic} for result {result!r}")

    def _on_subscribe(
        self, client, userdata, mid, reason_code_list, properties
    ):
        if reason_code_list[0].is_failure:
            return

        self._subscribed.set()

    def _on_message(self, client, userdata, msg):
        self._messages.put((msg.topic, json.loads(msg.payload)))

    # each turn request gets a player and switches to the other player
    def test_notify_turn_on_request(self):
        self._request_turn()
        first_player = self._wait_for(f"{self._PREFIX}/notifications/notify_turn")
        self.assertIn(first_player, (self._RED, self._YELLOW))

        self._request_turn()
        second_player = self._wait_for(f"{self._PREFIX}/notifications/notify_turn")
        self.assertIn(second_player, (self._RED, self._YELLOW))
        self.assertNotEqual(first_player, second_player)

    def test_request_reset_turn(self):
        self._request_turn()
        self._wait_for(f"{self._PREFIX}/notifications/notify_turn")

        self._request_reset_turn()
        player = self._wait_for(f"{self._PREFIX}/notifications/notify_reset_turn")
        self.assertEqual(player, self._RED)

        self._request_turn()
        player = self._wait_for(f"{self._PREFIX}/notifications/notify_turn")
        self.assertEqual(player, self._RED)

        self._request_turn()
        player = self._wait_for(f"{self._PREFIX}/notifications/notify_turn")
        self.assertEqual(player, self._YELLOW)


if __name__ == "__main__":
    unittest.main()
