import json
import logging
import threading

from board_artist import BoardArtist
from domain import (
    Domain,
    BOARD,
    STATUS,
    REQUEST_STATE,
    REQUEST_RESULT,
    NOTIFY_STATE,
    NOTIFY_STATE_CHANGE,
    REQUEST_STATUS,
    NOTIFY_STATUS,
    NOTIFY_STATUS_CHANGE,
    REQUEST_OBJECTS,
    REQUEST_CLICK,
    REQUEST_HOVER,
    NOTIFY_OBJECTS,
    NOTIFY_OBJECTS_CHANGE,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, top_host, top_port, bottom_host, bottom_port, top_publish=None, bottom_publish=None):
        self._board_artist = BoardArtist()
        self._lock = threading.Lock()

        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            # ask Board for the current board and Status for the current status 
            # on connect, in case they started first
            on_connected=self._on_connected,
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
        self._status_requests = top_domain[STATUS]["requests"]
        self._status_notifications = top_domain[STATUS]["notifications"]
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._board_notifications[NOTIFY_STATE]: self._on_notify_state,
            self._board_notifications[NOTIFY_STATE_CHANGE]: self._on_notify_state,
            self._status_notifications[NOTIFY_STATUS]: self._on_notify_status,
            self._status_notifications[NOTIFY_STATUS_CHANGE]: self._on_notify_status,
        }
        # bottom domain request handlers
        self._bottom_handlers = {
            self._requests[REQUEST_OBJECTS]: self._on_request_objects,
            self._requests[REQUEST_CLICK]: self._on_request_click,
            self._requests[REQUEST_HOVER]: self._on_request_hover,
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

    # issue notifications about more drawable objects
    def _on_notify_state(self, client, userdata, message):
        try:
            state = json.loads(message.payload)
            with self._lock:
                self._board_artist.set_state(state)
                objects = self._board_artist.get_objects()
        except (ValueError, TypeError):
            logging.exception("Could not process board state")
            return

        self._notify_objects_change(objects)

    def _on_notify_status(self, client, userdata, message):
        try:
            status = json.loads(message.payload)
            with self._lock:
                before = self._board_artist.get_objects()
                self._board_artist.set_status(status)
                objects = self._board_artist.get_objects()
        except (ValueError, TypeError):
            logging.exception("Could not process status")
            return

        if objects != before:
            self._notify_objects_change(objects)

    def _on_connected(self):
        self._request_state()
        self._request_status()

    def _request_state(self):
        return self._publish_request(self._board_requests, REQUEST_STATE)

    def _request_status(self):
        return self._publish_request(self._status_requests, REQUEST_STATUS)

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

    def _on_bottom_message(self, client, userdata, msg):
        callback = self._bottom_handlers.get(msg.topic)
        if callback is not None:
            callback(client, userdata, msg)

    def _on_request_objects(self, client, userdata, message):
        with self._lock:
            objects = self._board_artist.get_objects()

        self._notify_objects(objects)

    def _on_request_click(self, client, userdata, message):
        try:
            click = json.loads(message.payload)
            with self._lock:
                move = self._board_artist.accept_move(click["name"])
        except (ValueError, TypeError, KeyError):
            logging.exception("Could not process click")
            return

        if move is not None:
            player, column = move
            self._request_result(player, column)

    def _on_request_hover(self, client, userdata, message):
        try:
            hover = json.loads(message.payload)
            with self._lock:
                before = self._board_artist.get_objects()
                self._board_artist.set_hover(hover["name"])
                objects = self._board_artist.get_objects()
        except (ValueError, TypeError, KeyError):
            logging.exception("Could not process hover")
            return

        if objects != before:
            self._notify_objects_change(objects)

    def _notify_objects(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS, objects)

    def _notify_objects_change(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS_CHANGE, objects)

    def _publish_notification(self, notification, objects):
        topic_name = self._notifications[notification]
        payload = json.dumps(objects)
        return self._bottom_publish(topic_name, payload)
