import json
import threading
import unittest
from copy import deepcopy
import paho.mqtt.client as mqtt


class TestStatus(unittest.TestCase):
    # class level variables
    _host = "localhost"
    _port = 1883
    _connection_timeout = 5
    _connected_event = None
    _client = None

    # instance level variables
    _PREFIX = "c2/connector-model/status/bottom_domain"
    _RED = 1
    _YELLOW = -1
    _received_timeout = 2
    _subscribed_timeout = 5
    _subscribed = None
    _received = None
    _response = None
    _initial_status = {
        "is_game_running": False,
        "is_turn_timer_paused": False,
        "outcome": None,
        "current_player": None,
        "players": {
            "player_1": {
                "color": _RED,
                "wins": 0,
            },
            "player_2": {
                "color": _YELLOW,
                "wins": 0,
            },
        },
        "turn_seconds": 0,
        "turn_seconds_remaining": None,
        "game_seconds_elapsed": 0,
        "games_played": 0,
        "draws": 0,
    }

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
                f"{self._PREFIX}/notifications/notify_status_change"
            )
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
            self._reset_status()
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        self._client.unsubscribe([
            f"{self._PREFIX}/notifications/notify_status",
            f"{self._PREFIX}/notifications/notify_status_change",
        ])
        self._client.on_subscribe = None
        self._client.on_message = None

    def _reset_status(self):
        self._client.publish(f"{self._PREFIX}/requests/request_reset_status")
        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_status)

        self._client.unsubscribe(
            f"{self._PREFIX}/notifications/notify_status_change"
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

    def test_request_status(self):
        self._client.subscribe(f"{self._PREFIX}/notifications/notify_status")
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        self._client.publish(f"{self._PREFIX}/requests/request_status")

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_status)

    def test_request_update_status(self):
        self._client.subscribe(
            f"{self._PREFIX}/notifications/notify_status_change"
        )
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        changes = {
            "current_player": self._RED,
            "players": {"player_1": {"wins": 1}},
        }
        self._client.publish(
            f"{self._PREFIX}/requests/request_update_status",
            json.dumps(changes),
        )

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        expected_status = deepcopy(self._initial_status)
        expected_status["current_player"] = self._RED
        expected_status["players"]["player_1"]["wins"] = 1
        self.assertEqual(self._response, expected_status)

    def test_request_reset_status(self):
        self._client.subscribe(
            f"{self._PREFIX}/notifications/notify_status_change"
        )
        self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")

        changes = {
            "games_played": 1,
            "players": {"player_1": {"wins": 1}},
        }
        self._client.publish(
            f"{self._PREFIX}/requests/request_update_status",
            json.dumps(changes),
        )
        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response["games_played"], 1)
        self.assertEqual(self._response["players"]["player_1"]["wins"], 1)
        self._received.clear()
        self._response = None

        self._client.publish(f"{self._PREFIX}/requests/request_reset_status")

        self.assertTrue(self._received.wait(self._received_timeout), "Response timed out")
        self.assertEqual(self._response, self._initial_status)


if __name__ == "__main__":
    unittest.main()
