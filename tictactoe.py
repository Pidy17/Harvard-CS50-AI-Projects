
"""
Tic-Tac-Toe AI using the Minimax algorithm.
"""

# Represents the two players
X = "X"
O = "O"

# Represents an empty cell
EMPTY = None


def initial_state():
    """
    Returns the starting state of the board.
    """

    return [
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]
    ]


def player(board):
    """
    Returns the player who has the next turn.

    X always plays first.
    """

    x_count = 0
    o_count = 0

    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1

    if x_count == o_count:
        return X

    return O


def actions(board):
    """
    Returns a set of all possible actions.

    Each action is represented as (i, j).
    """

    possible_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns a new board after making a move.

    The original board is not modified.
    """

    if action not in actions(board):
        raise ValueError("Invalid action")

    new_board = [row.copy() for row in board]

    i, j = action

    new_board[i][j] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game.

    Checks horizontal, vertical and diagonal lines.
    """

    # Check horizontal rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not EMPTY:
            return row[0]

    # Check vertical columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j]:
            if board[0][j] is not EMPTY:
                return board[0][j]

    # Check diagonal from top-left to bottom-right
    if board[0][0] == board[1][1] == board[2][2]:
        if board[0][0] is not EMPTY:
            return board[0][0]

    # Check diagonal from top-right to bottom-left
    if board[0][2] == board[1][1] == board[2][0]:
        if board[0][2] is not EMPTY:
            return board[0][2]

    return None


def terminal(board):
    """
    Returns True if the game is over.
    """

    if winner(board) is not None:
        return True

    for row in board:
        if EMPTY in row:
            return False

    return True


def utility(board):
    """
    Returns the utility value of a terminal board.

    X wins:  1
    O wins: -1
    Tie:     0
    """

    game_winner = winner(board)

    if game_winner == X:
        return 1

    elif game_winner == O:
        return -1

    return 0


def max_value(board):
    """
    Finds the maximum possible utility for X.
    """

    if terminal(board):
        return utility(board)

    value = -2

    for action in actions(board):
        value = max(value, min_value(result(board, action)))

    return value


def min_value(board):
    """
    Finds the minimum possible utility for O.
    """

    if terminal(board):
        return utility(board)

    value = 2

    for action in actions(board):
        value = min(value, max_value(result(board, action)))

    return value


def minimax(board):
    """
    Returns the optimal move using the Minimax algorithm.

    X tries to maximize the score.
    O tries to minimize the score.
    """

    if terminal(board):
        return None

    best_action = None

    if player(board) == X:

        best_value = -2

        for action in actions(board):

            value = min_value(result(board, action))

            if value > best_value:
                best_value = value
                best_action = action

    else:

        best_value = 2

        for action in actions(board):

            value = max_value(result(board, action))

            if value < best_value:
                best_value = value
                best_action = action

    return best_action