TOP_CONNECTOR = "c2/connector-model"

STATUS = "status"
BOARD = "board"

# Status
REQUEST_UPDATE_STATUS = "request_update_status"
REQUEST_RESET_STATUS = "request_reset_status"
NOTIFY_STATUS_CHANGE = "notify_status_change"

# Board
REQUEST_ACTIONS = "request_actions"
REQUEST_RESULT = "request_result"
NOTIFY_AVAILABLE_ACTIONS = "notify_available_actions"
NOTIFY_STATE_CHANGE = "notify_state_change"

DOMAIN = {
    # the top domain of AutoPlay lists the requests AutoPlay sends to Status and Board,
    # and the notifications AutoPlay receives from Status and Board
    "top_domain": {
        STATUS: {
            "requests": [
                REQUEST_UPDATE_STATUS,
                REQUEST_RESET_STATUS,
            ],
            "notifications": [
                NOTIFY_STATUS_CHANGE,
            ],
        },
        BOARD: {
            "requests": [
                REQUEST_ACTIONS,
                REQUEST_RESULT,
            ],
            "notifications": [
                NOTIFY_AVAILABLE_ACTIONS,
                NOTIFY_STATE_CHANGE,
            ],
        },
    },
    # no bottom domain requests accepted or notifications are sent out 
    "bottom_domain": {
        "requests": [],
        "notifications": [],
    },
}


# An attempt at using the c2 style terminology and having a semblance of
# organization for it.
class Domain:
    def __init__(self, domain=DOMAIN, top_connector=TOP_CONNECTOR):
        self._domain = domain
        self._top_connector = top_connector
        self._top_topics = self._define_top_domain_topics()

    # AutoPlay has no bottom domain, so Domain.get_bottom_domain() returns {"requests": [], "notifications": []}
    def get_bottom_domain(self):
        return self._domain["bottom_domain"]

    def get_top_domain(self):
        return self._top_topics

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
