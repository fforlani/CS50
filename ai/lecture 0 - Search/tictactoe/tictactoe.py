"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # considering it is not important if the game it is over i avoid to check it for efficiency
    x, o = countNumberOfMoves(board)
    return X if x <= o else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # considering it is not important if the game it is over i avoid to check it for efficiency
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                moves.append((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if terminal(board):
        return None
    board[action[0]][action[1]] = player(board)
    return board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # checking the rows
    for row in board:
        if row[0] is None:
            continue
        if row[0] == row[1] and row[1] == row[2]:
            return row[0]
    # checking the columns
    for i in range(3):
        if board[0][i] is None:
            continue
        if board[0][i] == board[1][i] and board[1][i] == board[2][i]:
            return board[0][i]
    # checking the diagonals
    if board[0][0] is not None and board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]
    if board[2][0] is not None and board[2][0] == board[1][1] and board[1][1] == board[0][2]:
        return board[2][0]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    full = True
    for row in board:
        for cell in row:
            if cell is None:
                full = False
    if full:
        return True
    return winner(board) is not None


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win is None:
        return 0
    return 1 if win == X else -1


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if board == initial_state():
        return 0,0
    if terminal(board):
        return None
    next = player(board)
    moves = actions(board)
    bestMove = None
    for move in moves:
        val = evaluateMoves(board, move)
        if next == X and val == 1:
            return move
        if next == O and val == -1:
            return move
        if val == 0:
            bestMove = move
    return bestMove if bestMove is not None else moves[0]


def evaluateMoves(board, nextMove):
    newBoard = result(copy.deepcopy(board), nextMove)
    if terminal(newBoard):
        return utility(newBoard)
    next = player(newBoard)
    moves = actions(newBoard)
    # I will consider X as a max player and O as min player
    best = -1 if next == X else 1
    for move in moves:
        val = evaluateMoves(newBoard, move)
        if next == X:
            if val == 1:
                return 1
            best = max(best, val)
        else:
            if val == -1:
                return -1
            best = min(best, val)
    return best


def countNumberOfMoves(board):
    x = 0
    o = 0
    for row in board:
        for cell in row:
            if cell == X:
                x += 1
            elif cell == O:
                o += 1
    return x, o
