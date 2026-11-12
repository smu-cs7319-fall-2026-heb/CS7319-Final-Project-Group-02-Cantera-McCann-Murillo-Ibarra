from copy import deepcopy


RED = 1
YELLOW = -1
RED_WIN = "red"
YELLOW_WIN = "yellow"
DRAW = "draw"

# the states for StatusLogic
GAME_STOPPED = "game_stopped"
GAME_START_REQUESTED = "game_start_requested"
TURN_REQUESTED = "turn_requested"
TURN_STARTED = "turn_started"
GAME_STOP_REQUESTED = "game_stop_requested"


# Since it sits below two layers of connectors/components it can keep track of them
class StatusLogic:
    def __init__(self, turn_seconds):
        # how long a player has to make a move
        self._turn_seconds = turn_seconds
        # an internal representation of what Status component has
        self._status = None
        self._state = GAME_STOPPED
        self._is_status_changed = False
        self._is_reset_needed = False
        self._is_turn_needed = False

    def get_status(self):
        return deepcopy(self._status)

    def is_status_changed(self):
        return self._is_status_changed

    def is_reset_needed(self):
        return self._is_reset_needed

    def is_turn_needed(self):
        return self._is_turn_needed

    def next_tick(self):
        self._clear_needs()

        if self._state != TURN_STARTED:
            return

        # not a transition, just counts one second of the running turn
        self._status["game_seconds_elapsed"] += 1
        self._status["turn_seconds_remaining"] -= 1
        self._is_status_changed = True

        if self._status["turn_seconds_remaining"] == 0:
            self._turn_requested()

    def set_status(self, status):
        self._clear_needs()

        if not isinstance(status, dict):
            raise ValueError("Status must be a dictionary")

        # the only fields needed from Status
        for name in (
            "is_game_running",
            "outcome",
            "current_player",
            "players",
            "turn_seconds_remaining",
            "game_seconds_elapsed",
            "games_played",
        ):
            if name not in status:
                raise ValueError(f"Status is missing field: {name}")

        # Status says no game is running, this is also how a requested stop gets confirmed
        if not status["is_game_running"]:
            self._status = deepcopy(status)
            self._game_stopped()
        # a game can only start from GAME_STOPPED
        elif self._state == GAME_STOPPED:
            self._status = deepcopy(status)
            self._game_start_requested()

    def end_turn(self):
        self._clear_needs()

        if self._state == TURN_STARTED:
            self._turn_requested()

    def end_game(self, outcome):
        self._clear_needs()

        if outcome not in (RED_WIN, YELLOW_WIN, DRAW):
            raise ValueError(f"Outcome is not valid: {outcome}")

        if self._state in (TURN_REQUESTED, TURN_STARTED):
            self._game_stop_requested(outcome)

    def set_turn(self, player):
        self._clear_needs()

        if self._state == TURN_REQUESTED:
            self._turn_started(player)

    def reset_turn(self):
        self._clear_needs()

        if self._state == GAME_START_REQUESTED:
            self._turn_requested()

    def _clear_needs(self):
        self._is_status_changed = False
        self._is_reset_needed = False
        self._is_turn_needed = False

    # a new game needs an empty board, and a cleared game status
    def _game_start_requested(self):
        self._status["outcome"] = None
        self._status["current_player"] = None
        self._status["turn_seconds_remaining"] = None
        self._status["game_seconds_elapsed"] = 0
        self._state = GAME_START_REQUESTED
        self._is_status_changed = True
        self._is_reset_needed = True

    # entered when the game starts, after a move and after a timeout
    def _turn_requested(self):
        self._state = TURN_REQUESTED
        self._is_turn_needed = True

    def _turn_started(self, player):
        self._status["current_player"] = player
        self._status["turn_seconds_remaining"] = self._turn_seconds
        self._state = TURN_STARTED
        self._is_status_changed = True

    def _game_stop_requested(self, outcome):
        self._status["outcome"] = outcome
        self._status["turn_seconds_remaining"] = None
        self._status["is_game_running"] = False
        self._status["games_played"] += 1

        winner = self._get_winner(outcome)

        if winner is not None:
            self._status["players"][winner]["wins"] += 1

        self._state = GAME_STOP_REQUESTED
        self._is_status_changed = True

    def _game_stopped(self):
        self._state = GAME_STOPPED

    def _get_winner(self, outcome):
        if outcome == RED_WIN:
            color = RED
        elif outcome == YELLOW_WIN:
            color = YELLOW
        else:
            return None

        for name, player in self._status["players"].items():
            if player["color"] == color:
                return name

        return None
