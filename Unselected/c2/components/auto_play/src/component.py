import json
import logging
import queue
import threading

from auto_play import play, random_player
from domain import (
    Domain,
    STATUS,
    BOARD,
    REQUEST_UPDATE_STATUS,
    REQUEST_RESET_STATUS,
    NOTIFY_STATUS_CHANGE,
    REQUEST_ACTIONS,
    REQUEST_RESULT,
    NOTIFY_AVAILABLE_ACTIONS,
    NOTIFY_STATE_CHANGE,
)
from event_client import EventClient

WAIT_SECONDS = 10


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, top_host, top_port, games, top_publish=None):
        self._games = games
        # keep track fo when event_client is connected to the connector-view broker so run() does not start before that  
        self._connected = threading.Event()
        self._statuses = queue.Queue()
        self._states = queue.Queue()
        self._actions = queue.Queue()

        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            on_connected=self._connected.set,
            on_message=self._on_top_message,
        )
        self._top_publish = (
            self._top_event_client.publish if top_publish is None else top_publish
        )

        top_domain = self._domain.get_top_domain()
        self._status_requests = top_domain[STATUS]["requests"]
        self._status_notifications = top_domain[STATUS]["notifications"]
        self._board_requests = top_domain[BOARD]["requests"]
        self._board_notifications = top_domain[BOARD]["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._status_notifications[NOTIFY_STATUS_CHANGE]: self._on_notify_status_change,
            self._board_notifications[NOTIFY_AVAILABLE_ACTIONS]: self._on_notify_available_actions,
            self._board_notifications[NOTIFY_STATE_CHANGE]: self._on_notify_state_change,
        }

        for topic in self._top_handlers:
            self._top_event_client.subscribe(topic)

    def run(self):
        # start event client in a thread since it blocks 
        top_thread = threading.Thread(
            target=self._top_event_client.run, daemon=True
        )
        top_thread.start()

        try:
            self._connected.wait()
            self.reset_status()
            play(random_player, random_player, self, N=self._games)
        finally:
            self.disconnect()

    def disconnect(self):
        self._top_event_client.disconnect()

    def reset_status(self):
        self._request_reset_status()
        is_game_running = True
        while is_game_running:
            status = self._statuses.get(timeout=WAIT_SECONDS)
            is_game_running = status["is_game_running"]

    def start_game(self):
        self._request_update_status({"is_game_running": True})
        return self._states.get(timeout=WAIT_SECONDS)

    def actions(self):
        self._request_actions()
        return self._actions.get(timeout=WAIT_SECONDS)

    def result(self, p, a):
        self._request_result(p, a)
        return self._states.get(timeout=WAIT_SECONDS)

    def wait_for_turn(self, player):
        while True:
            status = self._statuses.get(timeout=WAIT_SECONDS)
            is_game_over = not status["is_game_running"]
            is_turn_started = (
                status["current_player"] == player
                and status["turn_seconds_remaining"] is not None
            )

            if is_game_over or is_turn_started:
                return status["outcome"]

    def _on_top_message(self, client, userdata, msg):
        callback = self._top_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_notify_status_change(self, client, userdata, message):
        try:
            status = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process status")
            return

        self._statuses.put(status)

    def _on_notify_available_actions(self, client, userdata, message):
        try:
            actions = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process available actions")
            return

        self._actions.put(actions)

    def _on_notify_state_change(self, client, userdata, message):
        try:
            state = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process board state")
            return

        self._states.put(state)

    def _request_update_status(self, status):
        return self._publish_request(
            self._status_requests, REQUEST_UPDATE_STATUS, status
        )

    def _request_reset_status(self):
        return self._publish_request(self._status_requests, REQUEST_RESET_STATUS)

    def _request_actions(self):
        return self._publish_request(self._board_requests, REQUEST_ACTIONS)

    def _request_result(self, p, a):
        return self._publish_request(
            self._board_requests, REQUEST_RESULT, {"p": p, "a": a}
        )

    def _publish_request(self, requests, request, value=None):
        topic_name = requests[request]
        payload = None
        if value is not None:
            payload = json.dumps(value)
        return self._top_publish(topic_name, payload)
