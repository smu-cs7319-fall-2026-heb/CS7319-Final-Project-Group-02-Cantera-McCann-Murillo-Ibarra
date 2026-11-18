import json
import queue
import threading
import time
import unittest
import paho.mqtt.client as mqtt


class TestBoardLogic(unittest.TestCase):
    # class level variables
    _host = "localhost"
    # tests run on the host, so the port is the only way to 
    # differentiate between connectors running behind the docker compose network 
    _model_port = 1883
    _controller_port = 1884
    _connection_timeout = 5
    _model_client = None
    _controller_client = None

    # instance level variables
    _BOARD_PREFIX = "c2/connector-model/board/bottom_domain"
    _PREFIX = "c2/connector-controller/board_logic/bottom_domain"
    _RED = 1
    _YELLOW = -1
    _received_timeout = 3
    _subscribed_timeout = 5
    _poll_interval = 0.25
    _subscribed = None
    _messages = None

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
        self._messages = queue.Queue()
        self._controller_client.on_subscribe = self._on_subscribe
        self._controller_client.on_message = self._on_message
        try:
            self._controller_client.subscribe([
                (f"{self._PREFIX}/notifications/notify_result", 0),
                (f"{self._PREFIX}/notifications/notify_result_change", 0),
            ])
            self.assertTrue(self._subscribed.wait(self._subscribed_timeout), "Subscription timed out")
            self._reset_board()
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        self._controller_client.unsubscribe([
            f"{self._PREFIX}/notifications/notify_result",
            f"{self._PREFIX}/notifications/notify_result_change",
        ])
        self._controller_client.on_subscribe = None
        self._controller_client.on_message = None

    def _reset_board(self):
        self._model_client.publish(f"{self._BOARD_PREFIX}/requests/request_reset_state")

        # BoardLogic only sees the reset on the next Clock tick, so ask until it reports an empty board
        deadline = time.monotonic() + self._received_timeout
        while time.monotonic() < deadline:
            self._controller_client.publish(f"{self._PREFIX}/requests/request_result")
            payload = self._wait_for(f"{self._PREFIX}/notifications/notify_result")
            if payload["result"] == 0:
                # drop messages from the reset so each test starts clean
                self._messages = queue.Queue()
                return
            time.sleep(self._poll_interval)

        self.fail("BoardLogic did not report an empty board after reset")

    def _drop_discs(self, actions):
        for player, action in actions:
            self._model_client.publish(
                f"{self._BOARD_PREFIX}/requests/request_result",
                json.dumps({"p": player, "a": action}),
            )

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
            if result is None or payload["result"] == result:
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

    def test_notify_result_change_on_successful_moves(self):
        self._drop_discs([(self._RED, 0)])
        self._wait_for(
            f"{self._PREFIX}/notifications/notify_result_change", result=1
        )

        self._drop_discs([(self._YELLOW, 1)])
        self._wait_for(
            f"{self._PREFIX}/notifications/notify_result_change", result=2
        )

    # red wins vertically in column 0, so the result changes to "red"
    def test_notify_result_change_on_win(self):
        self._drop_discs([
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0), (self._YELLOW, 1),
            (self._RED, 0),
        ])

        payload = self._wait_for(
            f"{self._PREFIX}/notifications/notify_result_change", result="red"
        )
        self.assertIsInstance(payload["tick"], int)


if __name__ == "__main__":
    unittest.main()
