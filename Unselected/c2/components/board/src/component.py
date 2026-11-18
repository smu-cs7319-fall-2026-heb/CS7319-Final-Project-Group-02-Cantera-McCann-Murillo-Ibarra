import json
import logging

from board import Board
from domain import (
    Domain,
    REQUEST_STATE,
    REQUEST_ACTIONS,
    REQUEST_RESULT,
    REQUEST_RESET_STATE,
    NOTIFY_STATE,
    NOTIFY_AVAILABLE_ACTIONS,
    NOTIFY_STATE_CHANGE,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out 
# of this component 
class Component:
    def __init__(self, host, port, publish=None):
        self._board = Board()
        self._domain = Domain()
        self._event_client = EventClient(
            host,
            port,
            on_connected=self.publish_dummy_data,
            on_message=self._on_message,
        )
        self._publish = (
            self._event_client.publish if publish is None else publish
        )

        bottom_domain = self._domain.get_bottom_domain()
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # bottom domain request handlers 
        self._handlers = {
            self._requests[REQUEST_STATE]: self._on_request_state,
            self._requests[REQUEST_ACTIONS]: self._on_request_actions,
            self._requests[REQUEST_RESULT]: self._on_request_result,
            self._requests[REQUEST_RESET_STATE]: self._on_request_reset_state,
        }

        for topic in self._handlers:
            self._event_client.subscribe(topic)

    def run(self):
        self._event_client.run()

    def disconnect(self):
        self._event_client.disconnect()

    def publish_dummy_data(self):
        self._notify_state()
        self._notify_available_actions()

    def _on_message(self, client, userdata, msg):
        callback = self._handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_request_state(self, client, userdata, message):
        self._notify_state()

    def _on_request_actions(self, client, userdata, message):
        self._notify_available_actions()

    def _on_request_result(self, client, userdata, message):
        try:
            payload = json.loads(message.payload)
            state = self._board.result(payload["p"], payload["a"])
        except Exception:
            logging.exception("Could not process result request")
            return

        self._notify_state_change(state)

    def _on_request_reset_state(self, client, userdata, message):
        state = self._board.reset_state()
        self._notify_state_change(state)

    # just shows current state 
    def _notify_state(self):
        state = self._board.get_state()
        return self._publish_notification(NOTIFY_STATE, state)

    def _notify_available_actions(self):
        actions = self._board.actions()
        return self._publish_notification(NOTIFY_AVAILABLE_ACTIONS, actions)

    # used to respond to player p taking action a and state reset request 
    def _notify_state_change(self, state):
        return self._publish_notification(NOTIFY_STATE_CHANGE, state)

    def _publish_notification(self, notification, value):
        topic_name = self._notifications[notification]
        payload = json.dumps(value.tolist())
        return self._publish(topic_name, payload)

