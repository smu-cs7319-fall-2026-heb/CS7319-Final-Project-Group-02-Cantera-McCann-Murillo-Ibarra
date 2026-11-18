import numpy as np
from scipy.signal import convolve2d

# TODO: get these constants from the Board compoenent instead. not a high priority 
YELLOW = -1
RED = 1
EMPTY = 0
# Keep winners distinct from move numbers: RED is also the number 1.
RED_WIN = "red"
YELLOW_WIN = "yellow"
DRAW = "draw"
WIN_LENGTH = 4


def check_board_conv(board):
    board_kernel = np.ones(shape=board.shape, dtype=np.int8)
    horizontal_kernel = np.ones(shape=(1, WIN_LENGTH), dtype=np.int8)
    vertical_kernel = np.ones(shape=(WIN_LENGTH, 1), dtype=np.int8)
    diag1_kernel = np.eye(WIN_LENGTH, dtype=np.int8)
    diag2_kernel = np.copy(np.fliplr(diag1_kernel))

    #3d array of non-homogeneous 2d arrays, so can't store it in a numpy array
    detection_kernels = [
        horizontal_kernel,
        vertical_kernel,
        diag1_kernel,
        diag2_kernel,
    ]

    for kernel in detection_kernels:
        #only compute once each
        red_conv_res = (
            convolve2d(board == RED, kernel, mode="valid") == WIN_LENGTH
        ).any()
        yellow_conv_res = (
            convolve2d(board == YELLOW, kernel, mode="valid") == WIN_LENGTH
        ).any()

        if red_conv_res:
            return RED_WIN
        if yellow_conv_res:
            return YELLOW_WIN

    #
    # check for a draw last before returning the successful move number
    #
    board_conv = convolve2d(board == EMPTY, board_kernel, mode="valid")
    if (board_conv == EMPTY).any():
        return DRAW

    return int(np.count_nonzero(board != EMPTY))


class BoardLogic:
    _state: np.ndarray = None

    def __init__(self, state=None):
        self._state = None

        if state is not None:
            self.set_state(state)

    def set_state(self, state):
        candidate = np.asarray(state)

        if candidate.ndim != 2:
            raise ValueError("Board state must be a rectangular 2D array")

        if any(size < WIN_LENGTH for size in candidate.shape):
            raise ValueError(
                f"Board must have at least {WIN_LENGTH} rows and columns"
            )

        if not np.isin(candidate, [YELLOW, EMPTY, RED]).all():
            raise ValueError(
                f"Board cells must contain {YELLOW}, {EMPTY}, or {RED}"
            )

        self._state = np.array(candidate, dtype=np.int8, copy=True)

    def has_state(self):
        return self._state is not None

    def check_board(self):
        if self._state is None:
            raise ValueError("Board state is unavailable")

        return check_board_conv(self._state)

    def is_terminal(self):
        return self.check_board() in (RED_WIN, YELLOW_WIN, DRAW)
