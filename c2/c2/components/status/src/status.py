from copy import deepcopy


RED = 1
YELLOW = -1


def INITIAL_STATUS():
    return {
        "current_player": None,
        "players": {
            "player_1": {
                "color": RED,
                "wins": 0,
            },
            "player_2": {
                "color": YELLOW,
                "wins": 0,
            },
        },
        "turn_seconds_remaining": None,
        "game_seconds_elapsed": 0,
        "games_played": 0,
    }


class Status:
    def __init__(self, status=None):
        self._status = INITIAL_STATUS() 

        if status is not None:
            self.update_status(status)

    def get_status(self):
        return deepcopy(self._status)

    def update_status(self, changes):
        if not isinstance(changes, dict):
            raise ValueError("Status updates must be dictionaries")

        status = self.get_status()
        self._apply_updates(status, changes)
        self._status = status

        return self.get_status()

    def _apply_updates(self, status, changes):
        for name, value in changes.items():
            if name not in status:
                raise ValueError(f"Unknown status field: {name}")

            if not isinstance(status[name], dict):
                status[name] = deepcopy(value)
                continue

            if not isinstance(value, dict):
                raise ValueError(
                    f"Status field {name} must be a dictionary"
                )

            self._apply_updates(status[name], value)
