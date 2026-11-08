import json
import threading
import unittest
from copy import deepcopy
import paho.mqtt.client as mqtt


class TestBoard(unittest.TestCase):
    # class level variables 
    _PREFIX = "c2/connector-state/board/bottom_domain"
    _host = "localhost"
    _port = 1883
    _connection_timeout = 5
    _connected_event = None
    _client = None

    # instance level variables 
    _received_timeout = 2
    _subscribed_timeout = 5
    _subscribed = None
    _received = None
    _response = None
    _initial_state = [[0] * 7 for _ in range(6)]

    @classmethod
    def setUpClass(cls):
        cls._connected_event = threading.Event()
        cls._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        cls._client.on_connect = cls._on_connect
        try:
            cls._client.connect(cls._host, cls._port)
            cls._client.loop_start()
            if not cls._connected_event.wait(cls._connection_timeout):
                raise AssertionError("Connection timed out")
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        cls._client.disconnect()
        cls._client.loop_stop()

    def setUp(self):
        self._subscribed = threading.Event()
        self._received = threading.Event()
        self._response = None
        self._client.on_subscribe = self._on_subscribe
        self._client.on_message = self._on_message
        try:
            self._client.subscribe(
                f"{self._PREFIX}/notifications/notify_state_change"
            )
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
            self._reset_board()
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        self._client.unsubscribe([
            f"{self._PREFIX}/notifications/notify_state",
            f"{self._PREFIX}/notifications/notify_available_actions",
            f"{self._PREFIX}/notifications/notify_state_change",
        ])
        self._client.on_subscribe = None
        self._client.on_message = None

    def _reset_board(self):
        self._client.publish(f"{self._PREFIX}/requests/request_reset_state")
        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_state)

        self._client.unsubscribe(
            f"{self._PREFIX}/notifications/notify_state_change"
        )
        self._subscribed.clear()
        self._received.clear()
        self._response = None

    @classmethod
    def _on_connect(
        cls, client, userdata, flags, reason_code, properties
    ):
        if reason_code.is_failure:
            return

        cls._connected_event.set()

    def _on_subscribe(
        self, client, userdata, mid, reason_code_list, properties
    ):
        if reason_code_list[0].is_failure:
            return

        self._subscribed.set()

    def _on_message(self, client, userdata, msg):
        self._response = json.loads(msg.payload)
        self._received.set()

    def test_request_state(self):
        self._client.subscribe(f"{self._PREFIX}/notifications/notify_state")
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        self._client.publish(f"{self._PREFIX}/requests/request_state")

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_state)

    def test_request_actions(self):
        self._client.subscribe(
            f"{self._PREFIX}/notifications/notify_available_actions"
        )
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        self._client.publish(f"{self._PREFIX}/requests/request_actions")

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, list(range(7)))

    def test_request_results(self):
        self._client.subscribe(
            f"{self._PREFIX}/notifications/notify_state_change"
        )
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        self._client.publish(
            f"{self._PREFIX}/requests/request_results",
            json.dumps({"p": 1, "a": 0}),
        )

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        expected_state = deepcopy(self._initial_state)
        expected_state[5][0] = 1
        self.assertEqual(self._response, expected_state)

    def test_request_reset_state(self):
        self._client.subscribe(
            f"{self._PREFIX}/notifications/notify_state_change"
        )
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        self._client.publish(
            f"{self._PREFIX}/requests/request_results",
            json.dumps({"p": 1, "a": 0}),
        )
        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response[5][0], 1)
        self._received.clear()
        self._response = None

        self._client.publish(f"{self._PREFIX}/requests/request_reset_state")

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_state)


if __name__ == "__main__":
    unittest.main()
