import random

from event_client import EventClient


def main() -> None:
    event_client = EventClient("connector-state", 1883)
    move_from = (random.randint(0, 6), random.randint(0, 7))
    move_to = (random.randint(0, 6), random.randint(0, 7))
    event_client.publish(
        "piece_moved", f"piece moved from {move_from} to {move_to}"
    )


if __name__ == "__main__":
    main()
