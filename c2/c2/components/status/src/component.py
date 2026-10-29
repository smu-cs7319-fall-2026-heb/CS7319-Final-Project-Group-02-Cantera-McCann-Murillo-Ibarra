import json
import logging

from status import Status
from domain import (
    Domain,
    REQUEST_STATUS,
    REQUEST_UPDATE_STATUS,
    NOTIFY_STATUS,
    NOTIFY_STATUS_CHANGE,
)
from event_client import EventClient


# just defines the handler functions requests/notifications in/out 
# of this component 
class Component:
    def __init__(self, host, port):
        self._status = Status()
        self._domain = Domain()
        self._event_client = EventClient(
            host, port, on_connect=self._notify_status
        )

        bottom_domain = self._domain.get_bottom_domain()
        self._requests = bottom_domain["requests"]
        self._notifications = bottom_domain["notifications"]

        # bottom domain request handler 
        handlers = {
            REQUEST_STATUS: self._on_request_status,
            REQUEST_UPDATE_STATUS: self._on_request_update_status,
        }

        for request, topic_name in self._requests.items():
            self._event_client.subscribe(topic_name, handlers[request])

    def run(self):
        self._event_client.run()

    def disconnect(self):
        self._event_client.disconnect()

    def _on_request_status(self, client, userdata, message):
        self._notify_status()

    def _on_request_update_status(self, client, userdata, message):
        try:
            changes = json.loads(message.payload)
            status = self._status.update_status(changes)
        except (ValueError, TypeError):
            logging.exception("Could not process status update request")
            return

        self._notify_status_change(status)

    # just shows current status 
    def _notify_status(self):
        status = self._status.get_status()
        return self._publish_notification(NOTIFY_STATUS, status)

    # only used to responed to _on_request_update_status bc something changed   
    def _notify_status_change(self, status):
        return self._publish_notification(NOTIFY_STATUS_CHANGE, status)

    def _publish_notification(self, notification, value):
        topic_name = self._notifications[notification]
        payload = json.dumps(value)
        return self._event_client.publish(topic_name, payload)
