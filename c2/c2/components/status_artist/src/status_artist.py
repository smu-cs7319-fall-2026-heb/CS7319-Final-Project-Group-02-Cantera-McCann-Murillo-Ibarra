from copy import deepcopy


RED = 1
YELLOW = -1
RED_WIN = "red"
YELLOW_WIN = "yellow"
DRAW = "draw"

NEW_GAME = "new_game"
RESET_SCORES = "reset_scores"
PAUSE_TIMER = "pause_timer"
RESUME_TIMER = "resume_timer"

TURN_TIMER_OPTIONS = {
    "turn_timer_10": 10,
    "turn_timer_20": 20,
    "turn_timer_30": 30,
}


# StatusArtist turns a status from the Status component into drawable objects.
class StatusArtist:
    def __init__(self):
        # internal representation of the Status component (yes it is not much 
        # different, but had the game been more complicated there would be   
        # more/different representations)
        self._objects = {}

    def get_objects(self):
        return deepcopy(self._objects)

    # build the internal representation of Status to then pass on to components below 
    def set_status(self, status):
        outcome = status["outcome"]
        current_player = status["current_player"]
        turn_seconds = status["turn_seconds"]
        turn_seconds_remaining = status["turn_seconds_remaining"]
        games_played = status["games_played"]
        draws = status["draws"]

        wins = {}
        for player in status["players"].values():
            wins[player["color"]] = player["wins"]

        objects = {}

        if outcome == RED_WIN:
            objects["message"] = {
                "type": "heading",
                "parts": [{"value": "Red", "color": "red"}, {"value": " wins!"}],
            }
        elif outcome == YELLOW_WIN:
            objects["message"] = {
                "type": "heading",
                "parts": [{"value": "Yellow", "color": "yellow"}, {"value": " wins!"}],
            }
        elif outcome == DRAW:
            objects["message"] = {
                "type": "heading",
                "parts": [{"value": "It's a draw!", "color": "gray"}],
            }
        elif current_player == RED:
            objects["message"] = {
                "type": "heading",
                "parts": [{"value": "Red", "color": "red"}, {"value": "'s turn"}],
            }
        elif current_player == YELLOW:
            objects["message"] = {
                "type": "heading",
                "parts": [{"value": "Yellow", "color": "yellow"}, {"value": "'s turn"}],
            }

        objects["score_red"] = {
            "type": "badge",
            "value": f"Red: {wins[RED]}",
            "color": "red",
        }
        objects["score_yellow"] = {
            "type": "badge",
            "value": f"Yellow: {wins[YELLOW]}",
            "color": "yellow",
        }
        objects["score_draws"] = {
            "type": "badge",
            "value": f"Draws: {draws}",
            "color": "gray",
        }

        if turn_seconds_remaining is not None:
            # how much of the turn is left, from 1 down to 0
            fraction = round(turn_seconds_remaining / turn_seconds, 2)

            if fraction > 0.5:
                color = "green"
            elif fraction > 0.25:
                color = "yellow"
            else:
                color = "red"

            objects["turn_timer_label"] = {"type": "text", "value": "Turn timer"}
            objects["turn_timer"] = {
                "type": "text",
                "value": f"{turn_seconds_remaining}s{' (paused)' if status['is_turn_timer_paused'] else ''}",
                "color": color,
            }
            objects["turn_timer_bar"] = {"type": "bar", "value": fraction, "color": color}

        if (status["is_game_running"]
            and turn_seconds_remaining is not None
        ):
            if status["is_turn_timer_paused"]:
                objects[RESUME_TIMER] = {"type": "button", "value": "Resume", "color": "blue"}
            else:
                objects[PAUSE_TIMER] = {"type": "button", "value": "Pause", "color": "blue"}

            for name, seconds in TURN_TIMER_OPTIONS.items():
                objects[name] = {
                    "type": "button",
                    "value": f"{seconds}s",
                    "color": "blue" if seconds == turn_seconds else "gray",
                }

        objects[NEW_GAME] = {"type": "button", "value": "New game", "color": "blue"}
        objects[RESET_SCORES] = {"type": "button", "value": "Reset scores", "color": "gray"}

        objects["games_played"] = {"type": "caption", "value": f"Games played: {games_played}"}

        self._objects = objects
