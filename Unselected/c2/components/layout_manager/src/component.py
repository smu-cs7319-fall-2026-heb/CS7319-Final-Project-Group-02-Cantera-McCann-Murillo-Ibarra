import json
import logging
import threading

from layout_manager import LayoutManager
from domain import (
    Domain,
    STATUS_ARTIST,
    BOARD_ARTIST,
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
        self._layout_manager = LayoutManager()
        self._lock = threading.Lock()

        self._domain = Domain()
        # top domain connector
        self._top_event_client = EventClient(
            top_host,
            top_port,
            on_connected=self._request_objects,
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
        self._status_artist_requests = top_domain[STATUS_ARTIST]["requests"]
        self._status_artist_notifications = top_domain[STATUS_ARTIST]["notifications"]
        self._board_artist_requests = top_domain[BOARD_ARTIST]["requests"]
        self._board_artist_notifications = top_domain[BOARD_ARTIST]["notifications"]
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # top domain notification handlers
        self._top_handlers = {
            self._status_artist_notifications[NOTIFY_OBJECTS]: self._on_notify_status_objects,
            self._status_artist_notifications[NOTIFY_OBJECTS_CHANGE]: self._on_notify_status_objects,
            self._board_artist_notifications[NOTIFY_OBJECTS]: self._on_notify_board_objects,
            self._board_artist_notifications[NOTIFY_OBJECTS_CHANGE]: self._on_notify_board_objects,
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

    # add x and y to the objects from StatusArtist, then send the objects out
    def _on_notify_status_objects(self, client, userdata, message):
        try:
            artist_objects = json.loads(message.payload)
            with self._lock:
                self._layout_manager.set_status_objects(artist_objects)
                objects = self._layout_manager.get_objects()
        except (ValueError, TypeError):
            logging.exception("Could not process status objects")
            return

        self._notify_objects_change(objects)

    # add x and y to the objects from BoardArtist, then send the objects out
    def _on_notify_board_objects(self, client, userdata, message):
        try:
            artist_objects = json.loads(message.payload)
            with self._lock:
                self._layout_manager.set_board_objects(artist_objects)
                objects = self._layout_manager.get_objects()
        except (ValueError, TypeError):
            logging.exception("Could not process board objects")
            return

        self._notify_objects_change(objects)

    def _request_objects(self):
        self._publish_request(self._status_artist_requests, REQUEST_OBJECTS)
        self._publish_request(self._board_artist_requests, REQUEST_OBJECTS)

    def _request_click(self, click):
        self._publish_request(self._status_artist_requests, REQUEST_CLICK, click)
        self._publish_request(self._board_artist_requests, REQUEST_CLICK, click)

    def _request_hover(self, hover):
        self._publish_request(self._board_artist_requests, REQUEST_HOVER, hover)

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

    # answer with the current objects. Empty until objects arrive from an artist
    def _on_request_objects(self, client, userdata, message):
        with self._lock:
            objects = self._layout_manager.get_objects()

        self._notify_objects(objects)

    def _on_request_click(self, client, userdata, message):
        try:
            click = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process click")
            return

        self._request_click(click)

    def _on_request_hover(self, client, userdata, message):
        try:
            hover = json.loads(message.payload)
        except ValueError:
            logging.exception("Could not process hover")
            return

        self._request_hover(hover)

    # answers request_objects with the current objects
    def _notify_objects(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS, objects)

    # sent every time objects arrive from StatusArtist or BoardArtist
    def _notify_objects_change(self, objects):
        return self._publish_notification(NOTIFY_OBJECTS_CHANGE, objects)

    def _publish_notification(self, notification, objects):
        topic_name = self._notifications[notification]
        payload = json.dumps(objects)
        return self._bottom_publish(topic_name, payload)
