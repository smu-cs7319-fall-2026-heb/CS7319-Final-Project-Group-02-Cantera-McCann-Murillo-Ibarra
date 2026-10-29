PREFIX = "c2/connector-state/status"

REQUEST_STATUS = "request_status"
REQUEST_UPDATE_STATUS = "request_update_status"

NOTIFY_STATUS = "notify_status"
NOTIFY_STATUS_CHANGE = "notify_status_change"

# keeping topics simple, so just passing entire status as notification 
DOMAIN = {
    "top_domain": {
        "requests": [],
        "notifications": [],
    },
    "bottom_domain": {
        "requests": [
            REQUEST_STATUS,
            REQUEST_UPDATE_STATUS,
        ],
        "notifications": [
            NOTIFY_STATUS,
            NOTIFY_STATUS_CHANGE,
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

    def get_top_domain(self):
        return self._domain["top_domain"]

    def _define_bottom_domain_topics(self):
        return self._define_topics(
            self._domain["bottom_domain"],
            f"{self._prefix}/bottom_domain",
        )

    def _define_topics(self, domain, prefix):
        topics = {}

        # Base case
        if isinstance(domain, list):
            for topic_level in domain:
                topics[topic_level] = f"{prefix}/{topic_level}"

        # Recursive call
        elif isinstance(domain, dict):
            for topic_level, remaining_levels in domain.items():
                topics[topic_level] = self._define_topics(
                    remaining_levels, f"{prefix}/{topic_level}"
                )

        else:
            raise ValueError("Domain levels must be dictionaries or lists")

        return topics
