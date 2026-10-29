import json
import logging

from board import Board
from domain import (
    Domain,
    REQUEST_STATE,
    REQUEST_ACTIONS,
    REQUEST_RESULTS,
    NOTIFY_STATE,
    NOTIFY_AVAILABLE_ACTIONS,
    NOTIFY_STATE_CHANGE,
)
from event_client import EventClient

# just defines the handler functions requests/notifications in/out 
# of this component 
class Component:
    def __init__(self, host, port):
        self._board = Board()
        self._domain = Domain()
        self._event_client = EventClient(
            host, port, on_connect=self.publish_dummy_data
        )

        bottom_domain = self._domain.get_bottom_domain()
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # bottom domain request handlers 
        handlers = {
            REQUEST_STATE: self._on_request_state,
            REQUEST_ACTIONS: self._on_request_actions,
            REQUEST_RESULTS: self._on_request_results,
        }

        for request, topic_name in self._requests.items():
            self._event_client.subscribe(topic_name, handlers[request])

    def run(self):
        self._event_client.run()

    def disconnect(self):
        self._event_client.disconnect()

    def publish_dummy_data(self):
        self._notify_state()
        self._notify_available_actions()

    def _on_request_state(self, client, userdata, message):
        self._notify_state()

    def _on_request_actions(self, client, userdata, message):
        self._notify_available_actions()

    def _on_request_results(self, client, userdata, message):
        try:
            payload = json.loads(message.payload)
            state = self._board.result(payload["p"], payload["a"])
        except Exception:
            logging.exception("Could not process result request")
            return

        self._notify_state_change(state)

    # just shows current state 
    def _notify_state(self):
        state = self._board.get_state()
        return self._publish_notification(NOTIFY_STATE, state)

    def _notify_available_actions(self):
        actions = self._board.actions()
        return self._publish_notification(NOTIFY_AVAILABLE_ACTIONS, actions)

    # only used to respond to _on_request_results after player p takes action a 
    def _notify_state_change(self, state):
        return self._publish_notification(NOTIFY_STATE_CHANGE, state)

    def _publish_notification(self, notification, value):
        topic_name = self._notifications[notification]
        if notification == NOTIFY_STATE:
            rows = [json.dumps(row) for row in value.tolist()]
            payload = "[\n" + ",\n".join(rows) + "\n]"
        else:
            payload = json.dumps(value.tolist())
        return self._event_client.publish(topic_name, payload)
