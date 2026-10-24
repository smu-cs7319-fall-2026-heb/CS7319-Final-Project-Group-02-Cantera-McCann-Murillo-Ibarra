import numpy as np    

#
# Attempt at reducing magic numbers  
# 
YELLOW = -1 
RED = 1 
EMPTY = 0 

CAN_DROP_DISK = 1  
CAN_NOT_DROP_DISK = 0  
DEFAULT_BOARD_SHAPE = (6,7) 
#NEXT_MOVE = "N"
#DRAW = 0 



def INITIAL_STATE(size: tuple = DEFAULT_BOARD_SHAPE) -> np.ndarray:    
    return np.full(shape=size, fill_value=0, dtype=np.int8)    

# legal moves in state s.   
def ACTIONS(s):      
    """ Will return an array the size of col with 0 or 1 where a  
    disk can be dropped  

    Parameters:  
        s (np.ndarray): State represented as a numpy 2D array   
    
    Returns:  
        np.ndarray: A list of 0's and 1's representing where a disc 
                can be dropped or not. Index of number represent 
                which column a disk can be dropped.  
                e.g. [0,1,0] a disk can be dropped in the second  
                column only. other columns have no more space   
    """  
    assert len(s) > 0   
    #only need to look at top row of state to see if column is full    
    res = np.where(s[0] == EMPTY, CAN_DROP_DISK, CAN_NOT_DROP_DISK)    
    return np.array([iii for iii in range(len(res)) if res[iii] == CAN_DROP_DISK], dtype=np.int8)     

def RESULT(s, p, a, verbose=False):     
#    print(f"RESULT \n{s=}\n {p=},{a=}")   
    """ 
        Will return the next state s_prime after taking action a 
        in state s  

    Parameters:  
        s (np.ndarray)      : State represented as a numpy 2D array    
        p (int)             : integer representing the player whose turn it is  
                            (e.g. 1 = red, -1 = yellow)   
        a (int)             : an integer defining what column to drop the disk into   
        verbose(bool)         : debug flag  

    Returns: 
        board (np.ndarray)  : deep copy of state as new state after taking action a  
    """ 

    board = s.copy()  
    #make sure there is at least one spot left in column to drop a disk, 
    # by looking at the "top" row for an empty spot in that column  
    if board[0][a] != EMPTY: 
        if verbose: print("exception happened board=") 
        if verbose: print(board)  
        raise Exception(f"Illegal action {a} by player {p} on board {board}")   
        
    # grab column as an array  
#    column = np.squeeze(s[:, a: a+1])  # squeeze not supported by njit atm  
    column = np.transpose(board[:, a: a+1])[0]   
          
    # set row_index as last row in column of interest bc for loop may NOT 
    # set the index (e.g. if column has no disks place in it)   
    row_index = len(column) - 1       
    # check down that row for first occurance of a NON-EMPTY spot 
    for iii, col in enumerate(column):   
        if col == RED or col == YELLOW:  
            # if NON-EMPTY spot found, grab it's index-1 as the next row     
            # to place a disk and break out of loop  
            row_index = iii - 1  
            break  

    board[row_index][a] = p   
    return board 


# Mostly just meant to hold a reference to the board 
class Board: 
    _board_shape = None 
    _state: np.ndarray = None 

    def __init__(self, state: np.ndarray = None, board_shape = DEFAULT_BOARD_SHAPE): 
        if state is None: 
            self._state = INITIAL_STATE(board_shape) 
        else: 
            self._state = state.copy() 
        self._board_shape = self._state.shape 

    def get_state(self,): 
        return self._state.copy() 

    def actions(self):
        return ACTIONS(self._state)

    def result(self, p, a, verbose=False):
        self._state = RESULT(self._state, p, a, verbose=verbose)
        return self.get_state()

