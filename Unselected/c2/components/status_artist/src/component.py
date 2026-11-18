import json
import logging
import threading

from status_artist import StatusArtist, NEW_GAME, RESET_SCORES, PAUSE_TIMER, RESUME_TIMER, TURN_TIMER_OPTIONS
from domain import (
    Domain,
    STATUS,
    REQUEST_STATUS,
    REQUEST_UPDATE_STATUS,
    REQUEST_RESET_STATUS,
    REQUEST_RESTART_TURN_TIMER,
    NOTIFY_STATUS,
    NOTIFY_STATUS_CHANGE,
    REQUEST_OBJECTS,
    REQUEST_CLICK,
    NOTIFY_OBJECTS,
    NOTIFY_OBJECTS_CHANGE,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out
# of this component
class Component:
    def __init__(self, top_host, top_port, bottom_host, bottom_port, top_publish=None, bottom_publish=None):
        self._status_artist = StatusArtist()
        self._lock = threading.Lock()

        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            # ask Status for the current status on connect, in case Status started first
            on_connected=self._request_status,
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
        self._status_requests = top_domain[STATUS]["requests"]
        self._status_notifications = top_domain[STATUS]["notifications"]
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._status_notifications[NOTIFY_STATUS]: self._on_notify_status,
            self._status_notifications[NOTIFY_STATUS_CHANGE]: self._on_notify_status,
        }
        # bottom domain request handlers
        self._bottom_handlers = {
            self._requests[REQUEST_OBJECTS]: self._on_request_objects,
            self._requests[REQUEST_CLICK]: self._on_request_click,
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
    def _on_notify_status(self, client, userdata, message):
        try:
            status = json.loads(message.payload)
            with self._lock:
                self._status_artist.set_status(status)
                objects = self._status_artist.get_objects()
        except (ValueError, TypeError):
            logging.exception("Could not process status")
            return

        self._notify_objects_change(objects)

    def _request_status(self):
        return self._publish_request(self._status_requests, REQUEST_STATUS)

    def _request_update_status(self, status):
        return self._publish_request(
            self._status_requests, REQUEST_UPDATE_STATUS, status
        )

    def _request_reset_status(self):
        return self._publish_request(self._status_requests, REQUEST_RESET_STATUS)

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
            objects = self._status_artist.get_objects()

        self._notify_objects(objects)

    def _on_request_click(self, client, userdata, message):
        try:
            click = json.loads(message.payload)
            name = click["name"]
        except (ValueError, TypeError, KeyError):
            logging.exception("Could not process click")
            return

        if name == NEW_GAME:
            self._request_update_status({"is_game_running": True})
        elif name == RESET_SCORES:
            self._request_reset_status()
        elif name == PAUSE_TIMER:
            self._request_update_status({"is_turn_timer_paused": True})
        elif name == RESUME_TIMER:
            self._request_update_status({"is_turn_timer_paused": False})
        elif name in TURN_TIMER_OPTIONS:
            self._publish_request(
                self._status_requests,
                REQUEST_RESTART_TURN_TIMER,
                TURN_TIMER_OPTIONS[name],
            )

    def _notify_objects(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS, objects)

    def _notify_objects_change(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS_CHANGE, objects)

    def _publish_notification(self, notification, objects):
        topic_name = self._notifications[notification]
        payload = json.dumps(objects)
        return self._bottom_publish(topic_name, payload)
