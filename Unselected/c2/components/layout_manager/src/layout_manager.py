from copy import deepcopy


#
#
# borrowing from OpenGL bc why not :)  
# https://learnopengl.com/Getting-started/Hello-Triangle#:~:text=this%20so%20called-,normalized%20device%20coordinates,-range%20will%20end
# 
# 
LAYOUT = {
    "message": {"x": 0.0, "y": 0.87},
    "score_red": {"x": -0.4, "y": 0.71},
    "score_yellow": {"x": 0.0, "y": 0.71},
    "score_draws": {"x": 0.4, "y": 0.71},
    "turn_timer_label": {"x": -0.57, "y": 0.58},
    "turn_timer": {"x": 0.57, "y": 0.58},
    "turn_timer_bar": {"x": 0.0, "y": 0.51, "width": 1.4, "height": 0.03},
    "new_game": {"x": -0.79, "y": -0.82},
    "pause_timer": {"x": -0.43, "y": -0.82},
    "resume_timer": {"x": -0.43, "y": -0.82},
    "reset_scores": {"x": -0.02, "y": -0.82},
    "turn_timer_10": {"x": 0.37, "y": -0.82},
    "turn_timer_20": {"x": 0.61, "y": -0.82},
    "turn_timer_30": {"x": 0.85, "y": -0.82},
    "games_played": {"x": 0.0, "y": -0.91},
}

# four edges
BOARD_LEFT = -0.91
BOARD_RIGHT = 0.91
BOARD_TOP = 0.45
BOARD_BOTTOM = -0.75


# LayoutManager adds x and y to the objects from StatusArtist and BoardArtist,
# and width and height to the ones that need a size to be drawn.
class LayoutManager:
    def __init__(self):
        self._status_objects = {}
        self._board_objects = {}

    def get_objects(self):
        objects = {}
        objects.update(deepcopy(self._status_objects))
        objects.update(deepcopy(self._board_objects))
        return objects

    def set_status_objects(self, artist_objects):
        objects = {}

        for name, artist_object in artist_objects.items():
            objects[name] = dict(artist_object)
            objects[name].update(LAYOUT[name])

        self._status_objects = objects

    def set_board_objects(self, artist_objects):
        # count the rows and columns from the cells
        rows = 0
        columns = 0
        for name, artist_object in artist_objects.items():
            if name != "board":
                rows = max(rows, artist_object["row"] + 1)
                columns = max(columns, artist_object["column"] + 1)

        board_width = BOARD_RIGHT - BOARD_LEFT
        board_height = BOARD_TOP - BOARD_BOTTOM

        objects = {}

        for name, artist_object in artist_objects.items():
            objects[name] = dict(artist_object)

            if name == "board":
                objects[name]["x"] = round((BOARD_LEFT + BOARD_RIGHT) / 2, 2)
                objects[name]["y"] = round((BOARD_TOP + BOARD_BOTTOM) / 2, 2)
                objects[name]["width"] = round(board_width, 2)
                objects[name]["height"] = round(board_height, 2)
            else:
                cell_width = board_width / columns
                cell_height = board_height / rows
                column = artist_object["column"]
                row = artist_object["row"]
                objects[name]["x"] = round(BOARD_LEFT + cell_width * (column + 0.5), 2)
                objects[name]["y"] = round(BOARD_TOP - cell_height * (row + 0.5), 2)
                objects[name]["width"] = round(cell_width, 2)
                objects[name]["height"] = round(cell_height, 2)

        self._board_objects = objects
