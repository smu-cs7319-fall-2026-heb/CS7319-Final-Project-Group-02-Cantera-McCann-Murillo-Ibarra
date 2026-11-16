TOP_CONNECTOR = "c2/connector-model"
PREFIX = "c2/connector-artist/status_artist"

STATUS = "status"

# Status
REQUEST_STATUS = "request_status"
REQUEST_UPDATE_STATUS = "request_update_status"
REQUEST_RESET_STATUS = "request_reset_status"
REQUEST_RESTART_TURN_TIMER = "request_restart_turn_timer"
NOTIFY_STATUS = "notify_status"
NOTIFY_STATUS_CHANGE = "notify_status_change"

# StatusArtist
REQUEST_OBJECTS = "request_objects"
REQUEST_CLICK = "request_click"
NOTIFY_OBJECTS = "notify_objects"
NOTIFY_OBJECTS_CHANGE = "notify_objects_change"

DOMAIN = {
    "top_domain": {
        STATUS: {
            "requests": [
                REQUEST_STATUS,
                REQUEST_UPDATE_STATUS,
                REQUEST_RESET_STATUS,
                REQUEST_RESTART_TURN_TIMER,
            ],
            "notifications": [
                NOTIFY_STATUS,
                NOTIFY_STATUS_CHANGE,
            ],
        },
    },
    # bottom domain does not need to worry about component names since it sends out
    # notifications without knowing who receives them and accepts requests without
    # needing to know who sent them
    "bottom_domain": {
        "requests": [
            REQUEST_OBJECTS,
            REQUEST_CLICK,
        ],
        "notifications": [
            NOTIFY_OBJECTS,
            NOTIFY_OBJECTS_CHANGE,
        ],
    },
}


# An attempt at using the c2 style terminology and having a semblance of
# organization for it.
class Domain:
    def __init__(self, domain=DOMAIN, prefix=PREFIX, top_connector=TOP_CONNECTOR):
        self._domain = domain
        self._prefix = prefix
        self._top_connector = top_connector
        self._top_topics = self._define_top_domain_topics()
        self._bottom_topics = self._define_bottom_domain_topics()

    def get_bottom_domain(self):
        return self._bottom_topics

    def get_top_domain(self):
        return self._top_topics

    def _define_bottom_domain_topics(self):
        return self._define_topics(
            self._domain["bottom_domain"],
            f"{self._prefix}/bottom_domain",
        )

    # components above publish on their own bottom domain
    def _define_top_domain_topics(self):
        topics = {}

        for component, component_domain in self._domain["top_domain"].items():
            topics[component] = self._define_topics(
                component_domain,
                f"{self._top_connector}/{component}/bottom_domain",
            )

        return topics

    def _define_topics(self, domain, prefix):
        topics = {}

        # base case
        if isinstance(domain, list):
            for topic_level in domain:
                topics[topic_level] = f"{prefix}/{topic_level}"

        # recursive call
        elif isinstance(domain, dict):
            for topic_level, remaining_levels in domain.items():
                topics[topic_level] = self._define_topics(
                    remaining_levels, f"{prefix}/{topic_level}"
                )

        else:
            raise ValueError("Domain levels must be dictionaries or lists")

        return topics
