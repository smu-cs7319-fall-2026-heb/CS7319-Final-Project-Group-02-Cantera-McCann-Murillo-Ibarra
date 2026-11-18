import json
import logging
import threading

from board_logic import BoardLogic
from domain import (
    Domain,
    BOARD,
    CLOCK,
    REQUEST_STATE,
    NOTIFY_STATE,
    NOTIFY_STATE_CHANGE,
    NOTIFY_NEXT_TICK,
    REQUEST_RESULT,
    NOTIFY_RESULT,
    NOTIFY_RESULT_CHANGE,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, top_host, top_port, bottom_host, bottom_port, top_publish=None, bottom_publish=None):
        self._board_logic = BoardLogic()
        # lock bc both connector threads access _tick and _result, through _set_latest and _get_latest
        self._lock = threading.Lock()
        self._result = None
        self._tick = None

        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            # ask Board for the current board on connect, in case Board started first
            on_connected=self._request_state,
            on_message=self._on_top_message,
        )
        # bottom domain connector
        self._bottom_event_client = EventClient(
            bottom_host,
            bottom_port,
            on_message=self._on_bottom_message,
        )
        self._top_publish = (
            self._top_event_client.publish if top_publish is None else top_publish
        )
        self._bottom_publish = (
            self._bottom_event_client.publish if bottom_publish is None else bottom_publish
        )

        top_domain = self._domain.get_top_domain()
        bottom_domain = self._domain.get_bottom_domain()
        self._board_requests = top_domain[BOARD]["requests"]
        self._board_notifications = top_domain[BOARD]["notifications"]
        self._clock_notifications = top_domain[CLOCK]["notifications"]
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._board_notifications[NOTIFY_STATE]: self._on_notify_state,
            self._board_notifications[NOTIFY_STATE_CHANGE]: self._on_notify_state,
            self._clock_notifications[NOTIFY_NEXT_TICK]: self._on_notify_next_tick,
        }
        # bottom domain request handlers
        self._bottom_handlers = {
            self._requests[REQUEST_RESULT]: self._on_request_result,
        }

        for topic in self._top_handlers:
            self._top_event_client.subscribe(topic)

        for topic in self._bottom_handlers:
            self._bottom_event_client.subscribe(topic)

    # a thead per connector client bc loop_forever blocks 
    def run(self):
        top_thread = threading.Thread(
            target=self._top_event_client.run, daemon=True
        )
        bottom_thread = threading.Thread(
            target=self._bottom_event_client.run, daemon=True
        )

        top_thread.start()
        bottom_thread.start()

        try:
            top_thread.join()
            bottom_thread.join()
        finally:
            self.disconnect()

    def disconnect(self):
        self._top_event_client.disconnect()
        self._bottom_event_client.disconnect()

    def _on_top_message(self, client, userdata, msg):
        callback = self._top_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_notify_state(self, client, userdata, message):
        try:
            state = json.loads(message.payload)
            self._board_logic.set_state(state)
        except (ValueError, TypeError):
            logging.exception("Could not process board state")

    def _on_notify_next_tick(self, client, userdata, message):
        try:
            tick = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process clock tick")
            return

        _, previous_result = self._get_latest()
        result = previous_result
        if self._board_logic.has_state():
            result = self._board_logic.check_board()

        self._set_latest(tick, result)

        # only announce when the result changes
        if result != previous_result:
            self._notify_result_change(tick, result)

    def _request_state(self):
        return self._publish_request(REQUEST_STATE)

    def _publish_request(self, request):
        topic_name = self._board_requests[request]
        return self._top_publish(topic_name, None)

    def _on_bottom_message(self, client, userdata, msg):
        callback = self._bottom_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_request_result(self, client, userdata, message):
        tick, result = self._get_latest()
        self._notify_result(tick, result)

    # just shows current result
    def _notify_result(self, tick, result):
        return self._publish_notification(NOTIFY_RESULT, tick, result)

    # used after a Clock tick changes the result
    def _notify_result_change(self, tick, result):
        return self._publish_notification(NOTIFY_RESULT_CHANGE, tick, result)

    def _publish_notification(self, notification, tick, result):
        topic_name = self._notifications[notification]
        payload = json.dumps({"tick": tick, "result": result})
        return self._bottom_publish(topic_name, payload)

    def _set_latest(self, tick, result):
        with self._lock:
            self._tick = tick
            self._result = result

    def _get_latest(self):
        with self._lock:
            return self._tick, self._result
