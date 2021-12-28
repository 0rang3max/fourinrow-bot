from game import GameBoard


game = GameBoard()
game.game_board = [
    ['Y', 'R', 'Y', 'R', None, None], 
    ['Y', 'Y', 'R', None,  None, None], 
    ['Y', 'R', None, None, None, None], 
    ['R', None, None, None, None, None], 
    [None, None, None, None, None, None], 
    [None, None, None, None, None, None], 
    [None, None, None, None, None, None]
]

assert game.check_move(3, 0)
assert game.check_move(2, 1)
assert game.check_move(1, 2)
assert game.check_move(0, 3)


game.game_board = [
    ['Y', 'R', 'Y', 'R', None, None], 
    ['Y', 'Y', 'R', None,  None, None], 
    ['Y', 'Y', 'Y', None, None, None], 
    ['R', None, None, 'Y', None, None], 
    [None, None, None, None, None, None], 
    [None, None, None, None, None, None], 
    [None, None, None, None, None, None]
]

assert game.check_move(3, 3)
