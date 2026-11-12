import json
import os
import queue
import threading
import time
import unittest
import paho.mqtt.client as mqtt


class TestStatusLogic(unittest.TestCase):
    _host = "localhost"
    _model_port = 1883
    _controller_port = 1884
    _connection_timeout = 5
    _model_client = None
    _controller_client = None

    _STATUS_PREFIX = "c2/connector-model/status/bottom_domain"
    _BOARD_PREFIX = "c2/connector-model/board/bottom_domain"
    _BOARD_LOGIC_PREFIX = "c2/connector-controller/board_logic/bottom_domain"
    _RED = 1
    _YELLOW = -1
    _TURN_SECONDS = int(os.getenv("TURN_SECONDS", "30"))
    _received_timeout = 5
    _subscribed_timeout = 5
    _poll_interval = 0.25
    _subscribed = None
    _statuses = None
    _results = None

    @classmethod
    def setUpClass(cls):
        try:
            cls._model_client = cls._connect(cls._model_port)
            cls._controller_client = cls._connect(cls._controller_port)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        for client in (cls._model_client, cls._controller_client):
            if client is not None:
                client.disconnect()
                client.loop_stop()

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
        self._statuses = queue.Queue()
        self._results = queue.Queue()
        self._model_client.on_subscribe = self._on_subscribe
        self._model_client.on_message = self._on_status
        self._controller_client.on_subscribe = self._on_subscribe
        self._controller_client.on_message = self._on_result
        try:
            self._model_client.subscribe([
                (f"{self._STATUS_PREFIX}/notifications/notify_status", 0),
                (f"{self._STATUS_PREFIX}/notifications/notify_status_change", 0),
            ])
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
            self._subscribed.clear()
            self._controller_client.subscribe([
                (f"{self._BOARD_LOGIC_PREFIX}/notifications/notify_result", 0),
            ])
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
            self._reset_status()
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        self._model_client.publish(f"{self._STATUS_PREFIX}/requests/request_reset_status")
        self._model_client.unsubscribe([
            f"{self._STATUS_PREFIX}/notifications/notify_status",
            f"{self._STATUS_PREFIX}/notifications/notify_status_change",
        ])
        self._controller_client.unsubscribe([
            f"{self._BOARD_LOGIC_PREFIX}/notifications/notify_result",
        ])
        for client in (self._model_client, self._controller_client):
            client.on_subscribe = None
            client.on_message = None

    def _reset_status(self):
        self._model_client.publish(f"{self._STATUS_PREFIX}/requests/request_reset_status")
        self._wait_for_status({
            "is_game_running": False,
            "outcome": None,
            "games_played": 0,
        })
        self._statuses = queue.Queue()

    def _start_game(self):
        self._model_client.publish(
            f"{self._STATUS_PREFIX}/requests/request_update_status",
            json.dumps({"is_game_running": True}),
        )
        status = self._wait_for_status({
            "is_game_running": True,
            "current_player": self._RED,
            "turn_seconds_remaining": self._TURN_SECONDS,
        })
        self._wait_for_empty_board()
        return status

    def _wait_for_empty_board(self):
        deadline = time.monotonic() + self._received_timeout
        while time.monotonic() < deadline:
            self._controller_client.publish(
                f"{self._BOARD_LOGIC_PREFIX}/requests/request_result"
            )
            try:
                payload = self._results.get(timeout=self._poll_interval)
            except queue.Empty:
                continue

            if payload["result"] == 0:
                return
            time.sleep(self._poll_interval)

        self.fail("BoardLogic did not report an empty board after the game started")

    def _drop_discs(self, actions):
        for player, action in actions:
            self._model_client.publish(
                f"{self._BOARD_PREFIX}/requests/request_result",
                json.dumps({"p": player, "a": action}),
            )

    def _red_wins(self):
        self._drop_discs([
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0),
        ])
        return self._wait_for_status({
            "is_game_running": False,
            "outcome": "red",
        })

    def _wait_for_status(self, expected, timeout=None):
        if timeout is None:
            timeout = self._received_timeout

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = max(0, deadline - time.monotonic())
            try:
                status = self._statuses.get(timeout=remaining)
            except queue.Empty:
                break

            if self._matches(status, expected):
                return status

        self.fail(f"Timed out waiting for status {expected!r}")

    def _matches(self, status, expected):
        for name, value in expected.items():
            if status[name] != value:
                return False

        return True

    def _on_subscribe(
        self, client, userdata, mid, reason_code_list, properties
    ):
        if reason_code_list[0].is_failure:
            return

        self._subscribed.set()

    def _on_status(self, client, userdata, msg):
        self._statuses.put(json.loads(msg.payload))

    def _on_result(self, client, userdata, msg):
        self._results.put(json.loads(msg.payload))

    def test_request_update_status_on_game_start(self):
        status = self._start_game()
        self.assertIsNone(status["outcome"])
        self.assertEqual(status["game_seconds_elapsed"], 0)

    def test_request_update_status_on_next_tick(self):
        self._start_game()
        self._wait_for_status({"turn_seconds_remaining": self._TURN_SECONDS - 1})
        self._wait_for_status({"turn_seconds_remaining": self._TURN_SECONDS - 2})

    def test_request_turn_on_successful_move(self):
        self._start_game()

        self._drop_discs([(self._RED, 0)])
        self._wait_for_status({
            "current_player": self._YELLOW,
            "turn_seconds_remaining": self._TURN_SECONDS,
        })

        self._drop_discs([(self._YELLOW, 1)])
        self._wait_for_status({
            "current_player": self._RED,
            "turn_seconds_remaining": self._TURN_SECONDS,
        })

    def test_request_turn_on_timeout(self):
        self._start_game()
        self._wait_for_status(
            {
                "current_player": self._YELLOW,
                "turn_seconds_remaining": self._TURN_SECONDS,
            },
            timeout=self._TURN_SECONDS + 5,
        )

    def test_request_update_status_on_win(self):
        self._start_game()
        status = self._red_wins()
        self.assertEqual(status["games_played"], 1)
        self.assertEqual(status["players"]["player_1"]["wins"], 1)
        self.assertEqual(status["players"]["player_2"]["wins"], 0)
        self.assertIsNone(status["turn_seconds_remaining"])

    def test_request_update_status_on_next_game(self):
        self._start_game()
        self._red_wins()

        status = self._start_game()
        self.assertIsNone(status["outcome"])
        self.assertEqual(status["games_played"], 1)
        self.assertEqual(status["players"]["player_1"]["wins"], 1)


if __name__ == "__main__":
    unittest.main()
