MODEL_CONNECTOR = "c2/connector-model"
CONTROLLER_CONNECTOR = "c2/connector-controller"

CLOCK = "clock"
STATUS = "status"
BOARD = "board"
BOARD_LOGIC = "board_logic"
TURN_LOGIC = "turn_logic"

# Clock
NOTIFY_NEXT_TICK = "notify_next_tick"

# Status
REQUEST_STATUS = "request_status"
REQUEST_UPDATE_STATUS = "request_update_status"
NOTIFY_STATUS = "notify_status"
NOTIFY_STATUS_CHANGE = "notify_status_change"

# Board
REQUEST_RESET_STATE = "request_reset_state"

# BoardLogic
NOTIFY_RESULT_CHANGE = "notify_result_change"

# TurnLogic
REQUEST_TURN = "request_turn"
REQUEST_RESET_TURN = "request_reset_turn"
NOTIFY_TURN = "notify_turn"
NOTIFY_RESET_TURN = "notify_reset_turn"

TOP_CONNECTORS = {
    CLOCK: MODEL_CONNECTOR,
    STATUS: MODEL_CONNECTOR,
    BOARD: MODEL_CONNECTOR,
    BOARD_LOGIC: CONTROLLER_CONNECTOR,
    TURN_LOGIC: CONTROLLER_CONNECTOR,
}

DOMAIN = {
    # top domain of StatusLogic connects to multiple bottom domains, in this case
    # the Clock, Status, Board, BoardLogic and TurnLogic components
    "top_domain": {
        CLOCK: {
            "requests": [],
            "notifications": [
                NOTIFY_NEXT_TICK,
            ],
        },
        STATUS: {
            "requests": [
                REQUEST_STATUS,
                REQUEST_UPDATE_STATUS,
            ],
            "notifications": [
                NOTIFY_STATUS,
                NOTIFY_STATUS_CHANGE,
            ],
        },
        BOARD: {
            "requests": [
                REQUEST_RESET_STATE,
            ],
            "notifications": [],
        },
        BOARD_LOGIC: {
            "requests": [],
            "notifications": [
                NOTIFY_RESULT_CHANGE,
            ],
        },
        TURN_LOGIC: {
            "requests": [
                REQUEST_TURN,
                REQUEST_RESET_TURN,
            ],
            "notifications": [
                NOTIFY_TURN,
                NOTIFY_RESET_TURN,
            ],
        },
    },
    "bottom_domain": {
        "requests": [],
        "notifications": [],
    },
}


# An attempt at using the c2 style terminology and having a semblance of
# organization for it.
class Domain:
    def __init__(self, domain=DOMAIN, top_connectors=TOP_CONNECTORS):
        self._domain = domain
        self._top_connectors = top_connectors
        self._top_topics = self._define_top_domain_topics()

    # StatusLogic does not have a bottom domain so this will return empty lists
    def get_bottom_domain(self):
        return self._domain["bottom_domain"]

    def get_top_domain(self):
        return self._top_topics

    def _define_top_domain_topics(self):
        topics = {}

        for component, component_domain in self._domain["top_domain"].items():
            topics[component] = self._define_topics(
                component_domain,
                f"{self._top_connectors[component]}/{component}/bottom_domain",
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
