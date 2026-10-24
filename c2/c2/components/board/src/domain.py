PREFIX = "c2/connector-state/board"

REQUEST_STATE = "request_state"
REQUEST_ACTIONS = "request_actions"
REQUEST_RESULTS = "request_results"

NOTIFY_STATE = "notify_state"
NOTIFY_AVAILABLE_ACTIONS = "notify_available_actions"
NOTIFY_STATE_CHANGE = "notify_state_change"

DOMAIN = {
    "top_domain": {
        "requests": [],
        "notifications": [],
    },
    "bottom_domain": {
        "requests": [
            REQUEST_STATE,
            REQUEST_ACTIONS,
            REQUEST_RESULTS,
        ],
        "notifications": [
            NOTIFY_STATE,
            NOTIFY_AVAILABLE_ACTIONS,
            NOTIFY_STATE_CHANGE,
        ],
    },
}

# An attempt at using the c2 style terminology and having a semblance of 
# organization for it. 
class Domain: 
    def __init__(self, domain=DOMAIN, prefix=PREFIX):
        self._domain = domain
        self._prefix = prefix
        self._bottom_topics = self._define_bottom_domain_topics()

    def get_bottom_domain(self):
        return self._bottom_topics

    # board does not have a top domain so this will return empty. 
    def get_top_domain(self):
        return self._domain["top_domain"]

    def _define_bottom_domain_topics(self):
        return self._define_topics(
            self._domain["bottom_domain"],
            f"{self._prefix}/bottom_domain",
        )

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
