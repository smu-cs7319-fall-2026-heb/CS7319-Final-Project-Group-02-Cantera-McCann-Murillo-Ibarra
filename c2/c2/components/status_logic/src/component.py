import json
import logging

from status_logic import StatusLogic
from domain import (
    Domain,
    CLOCK,
    STATUS,
    BOARD,
    BOARD_LOGIC,
    TURN_LOGIC,
    NOTIFY_NEXT_TICK,
    REQUEST_STATUS,
    REQUEST_UPDATE_STATUS,
    NOTIFY_STATUS,
    NOTIFY_STATUS_CHANGE,
    REQUEST_RESET_STATE,
    NOTIFY_RESULT_CHANGE,
    REQUEST_TURN,
    REQUEST_RESET_TURN,
    NOTIFY_TURN,
    NOTIFY_RESET_TURN,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, top_host, top_port, turn_seconds, top_publish=None):
        self._status_logic = StatusLogic(turn_seconds)
        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            # ask Status for the current status on connect, in case Status started first
            on_connected=self._request_status,
            on_message=self._on_top_message,
        )
        self._top_publish = (
            self._top_event_client.publish if top_publish is None else top_publish
        )

        top_domain = self._domain.get_top_domain()
        self._clock_notifications = top_domain[CLOCK]["notifications"]
        self._status_requests = top_domain[STATUS]["requests"]
        self._status_notifications = top_domain[STATUS]["notifications"]
        self._board_requests = top_domain[BOARD]["requests"]
        self._board_logic_notifications = top_domain[BOARD_LOGIC]["notifications"]
        self._turn_logic_requests = top_domain[TURN_LOGIC]["requests"]
        self._turn_logic_notifications = top_domain[TURN_LOGIC]["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._clock_notifications[NOTIFY_NEXT_TICK]: self._on_notify_next_tick,
            self._status_notifications[NOTIFY_STATUS]: self._on_notify_status,
            self._status_notifications[NOTIFY_STATUS_CHANGE]: self._on_notify_status,
            self._board_logic_notifications[NOTIFY_RESULT_CHANGE]: self._on_notify_result_change,
            self._turn_logic_notifications[NOTIFY_TURN]: self._on_notify_turn,
            self._turn_logic_notifications[NOTIFY_RESET_TURN]: self._on_notify_reset_turn,
        }

        for topic in self._top_handlers:
            self._top_event_client.subscribe(topic)

    def run(self):
        self._top_event_client.run()

    def disconnect(self):
        self._top_event_client.disconnect()

    def _on_top_message(self, client, userdata, msg):
        callback = self._top_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_notify_next_tick(self, client, userdata, message):
        self._status_logic.next_tick()
        self._publish_needed_requests()

    def _on_notify_status(self, client, userdata, message):
        try:
            status = json.loads(message.payload)
            self._status_logic.set_status(status)
        except (ValueError, TypeError):
            logging.exception("Could not process status")
            return

        self._publish_needed_requests()

    def _on_notify_result_change(self, client, userdata, message):
        try:
            payload = json.loads(message.payload)
            result = payload["result"]

            # BoardLogic gives red, yellow or draw when the game is over
            if isinstance(result, str):
                self._status_logic.end_game(result)
            # otherwise it gives the disc count, above 0 means a move was made
            elif isinstance(result, int) and result > 0:
                self._status_logic.end_turn()
            # an empty board is not a move, so there is nothing to publish
            else:
                return
        except (ValueError, TypeError, KeyError):
            logging.exception("Could not process result")
            return

        self._publish_needed_requests()

    def _on_notify_turn(self, client, userdata, message):
        try:
            player = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process turn")
            return

        self._status_logic.set_turn(player)
        self._publish_needed_requests()

    def _on_notify_reset_turn(self, client, userdata, message):
        self._status_logic.reset_turn()
        self._publish_needed_requests()

    # used after every top domain notification to request what StatusLogic says is needed
    def _publish_needed_requests(self):
        # a reset means an empty the Board and set TurnLogic back to the first player 
        if self._status_logic.is_reset_needed():
            self._request_reset_state()
            self._request_reset_turn()

        if self._status_logic.is_status_changed():
            self._request_update_status(self._status_logic.get_status())

        if self._status_logic.is_turn_needed():
            self._request_turn()

    def _request_status(self):
        return self._publish_request(self._status_requests, REQUEST_STATUS)

    def _request_update_status(self, status):
        return self._publish_request(
            self._status_requests, REQUEST_UPDATE_STATUS, status
        )

    def _request_reset_state(self):
        return self._publish_request(self._board_requests, REQUEST_RESET_STATE)

    def _request_turn(self):
        return self._publish_request(self._turn_logic_requests, REQUEST_TURN)

    def _request_reset_turn(self):
        return self._publish_request(self._turn_logic_requests, REQUEST_RESET_TURN)

    def _publish_request(self, requests, request, value=None):
        topic_name = requests[request]
        payload = None
        if value is not None:
            payload = json.dumps(value)
        return self._top_publish(topic_name, payload)
