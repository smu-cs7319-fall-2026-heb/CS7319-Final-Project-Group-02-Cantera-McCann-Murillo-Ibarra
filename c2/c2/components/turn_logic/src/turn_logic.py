RED = 1
YELLOW = -1

# nice and simple  
class TurnLogic:
    def __init__(self):
        self._player = RED

    def get_turn(self):
        player = self._player
        self._player = YELLOW if player == RED else RED
        return player

    # every new game starts with RED
    def reset_turn(self):
        self._player = RED
        return self._player
