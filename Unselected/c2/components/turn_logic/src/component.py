import json

from turn_logic import TurnLogic
from domain import (
    Domain,
    REQUEST_TURN,
    REQUEST_RESET_TURN,
    NOTIFY_TURN,
    NOTIFY_RESET_TURN,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, bottom_host, bottom_port, bottom_publish=None):
        self._turn_logic = TurnLogic()
        self._domain = Domain()
        # bottom domain connector
        self._bottom_event_client = EventClient(
            bottom_host,
            bottom_port,
            on_message=self._on_bottom_message,
        )
        self._bottom_publish = (
            self._bottom_event_client.publish if bottom_publish is None else bottom_publish
        )

        bottom_domain = self._domain.get_bottom_domain()
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # bottom domain request handlers
        self._bottom_handlers = {
            self._requests[REQUEST_TURN]: self._on_request_turn,
            self._requests[REQUEST_RESET_TURN]: self._on_request_reset_turn,
        }

        for topic in self._bottom_handlers:
            self._bottom_event_client.subscribe(topic)

    def run(self):
        self._bottom_event_client.run()

    def disconnect(self):
        self._bottom_event_client.disconnect()

    def _on_bottom_message(self, client, userdata, msg):
        callback = self._bottom_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_request_turn(self, client, userdata, message):
        player = self._turn_logic.get_turn()
        self._notify_turn(player)

    def _on_request_reset_turn(self, client, userdata, message):
        player = self._turn_logic.reset_turn()
        self._notify_reset_turn(player)

    def _notify_turn(self, player):
        return self._publish_notification(NOTIFY_TURN, player)

    # used to respond to a turn reset request 
    def _notify_reset_turn(self, player):
        return self._publish_notification(NOTIFY_RESET_TURN, player)

    def _publish_notification(self, notification, player):
        topic_name = self._notifications[notification]
        payload = json.dumps(player)
        return self._bottom_publish(topic_name, payload)
