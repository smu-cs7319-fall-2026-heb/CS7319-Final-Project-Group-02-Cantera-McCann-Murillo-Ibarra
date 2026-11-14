import random

RED = 1
YELLOW = -1
RED_WIN = "red"
YELLOW_WIN = "yellow"
DRAW = "draw"
NEXT_MOVE = None

# return column picked at random represents a move from available actions 
def random_player(state, actions, player=None):
    return random.choice(actions)


# play() plays N games and returns the count of red wins, yellow wins and draws 
def play(red, yellow, component, N=100):
    results = {RED_WIN: 0, YELLOW_WIN: 0, DRAW: 0}

    for iii in range(N):
        board = component.start_game()
        # waits until Status reports the turn of RED started 
        component.wait_for_turn(RED)
        while True:
            # 
            # RED moves:
            # 
            # asks Board for the available actions 
            actions = component.actions()
            # red picks action 
            a = red(board, actions, player=RED)
            # sends the move to the Board component and gets a new board 
            board = component.result(p=RED, a=a)
            # waits until Status reports the turn of YELLOW started 
            win = component.wait_for_turn(YELLOW)
            # game ended, keep track of what happened 
            if win != NEXT_MOVE:
                results[win] += 1
                break
            # 
            # YELLOW moves:
            #  
            # asks Board for the available actions 
            actions = component.actions()
            # yellow picks action 
            a = yellow(board, actions, player=YELLOW)
            # sends the move to the Board component and gets a new board 
            board = component.result(p=YELLOW, a=a)
            # waits until Status reports the turn of RED started 
            win = component.wait_for_turn(RED)
            # game ended, keep track of what happened 
            if win != NEXT_MOVE:
                results[win] += 1
                break

        print(f"play() game {iii + 1} of {N} results={results}")

    return results
