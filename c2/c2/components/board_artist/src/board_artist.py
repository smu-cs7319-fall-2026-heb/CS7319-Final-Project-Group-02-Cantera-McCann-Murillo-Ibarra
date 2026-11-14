from copy import deepcopy


RED = 1
YELLOW = -1
EMPTY = 0

COLORS = {
    RED: "red",
    YELLOW: "yellow",
    EMPTY: "white",
}

PREVIEW_OPACITY = 0.5


# BoardArtist turns a state from the Board component into more drawable object 
class BoardArtist:
    def __init__(self):
        self._objects = {}
        self._state = []
        self._current_player = None
        self._is_turn_running = False
        self._hover_name = None

    def get_objects(self):
        objects = deepcopy(self._objects)
        move = self.get_move(self._hover_name)

        if move is not None:
            player, column = move
            row = self._get_landing_row(column)

            if row is not None:
                objects[f"cell_{row}_{column}"]["color"] = COLORS[player]
                objects[f"cell_{row}_{column}"]["opacity"] = PREVIEW_OPACITY

        return objects

    def set_hover(self, name):
        self._hover_name = name

    def set_status(self, status):
        self._current_player = status["current_player"]
        self._is_turn_running = status["turn_seconds_remaining"] is not None

    def get_move(self, name):
        is_cell = name in self._objects and name != "board"

        if not is_cell or not self._is_turn_running:
            return None

        return self._current_player, self._objects[name]["column"]

    def _get_landing_row(self, column):
        landing_row = None

        for row in range(len(self._state)):
            if self._state[row][column] == EMPTY:
                landing_row = row

        return landing_row

    def set_state(self, state):
        self._state = state
        objects = {}

        objects["board"] = {"type": "rectangle", "color": "blue"}

        # one circle for each cell of the board. row 0 is the top row, same as in the state
        for row in range(len(state)):
            for column in range(len(state[row])):
                objects[f"cell_{row}_{column}"] = {
                    "type": "circle",
                    "color": COLORS[state[row][column]],
                    "row": row,
                    "column": column,
                }

        self._objects = objects
