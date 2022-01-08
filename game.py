import random
from typing import List, Optional
from exceptions import game_exceptions


class GameBoard:
    red = 'R'
    yellow = 'Y'
    tokens_repr = {
        None: '⚪',
        red: '🔴',
        yellow: '🟡',
    }

    def __init__(
        self, 
        columns: int = 7, 
        rows: int = 6, 
        win_sequence_count: int = 4,
        game_board: Optional[List[list]] = None,
        moves_counter: Optional[int] = None
    ) -> None:
        self.columns, self.rows = columns, rows
        self.win_sequence_count = win_sequence_count
        self.game_board = game_board or [[None for _ in range(self.rows)] for _ in range(self.columns)]
        self.moves_counter = moves_counter or 0

    def __str__(self) -> str:
        rows = []
        for row_num in range(self.rows):
            row = []
            for column_num in range(self.columns):
                row.append(self.tokens_repr[self.game_board[column_num][row_num]])
            rows.append(row)
        rows.reverse()
        return '\n'.join([''.join(row) for row in rows])

    @property
    def moves_left(self):
        return  self.columns * self.rows - self.moves_counter

    def make_move(self, column_idx, token):
        column = self.game_board[column_idx]
        try:
            row_idx = column.index(None)
        except ValueError:
            raise game_exceptions.ColumnIsFullError

        column[row_idx] = token
        self.game_board[column_idx] = column
        self.moves_counter += 1

        return column_idx, row_idx

    def check_move(self, x, y):
        move_value = self.game_board[x][y]

        def _is_players_color(check_x, check_y):
            return self.game_board[check_x][check_y] == move_value

        w_to_e, s_to_n, sw_to_ne, nw_to_se = 0, 0, 0, 0
        for offset in range(-3, 4):
            offset_x, offset_y, inv_offset_y = x + offset, y + offset, y - offset
            x_offset_fits = offset_x >= 0 and offset_x <= self.columns - 1
            y_offset_fits = offset_y >= 0 and offset_y <= self.rows - 1
            inv_offset_y_fits = inv_offset_y >= 0 and inv_offset_y <= self.rows - 1
            
            w_to_e = w_to_e + 1 if x_offset_fits and _is_players_color(offset_x, y) else 0
            s_to_n = s_to_n + 1 if y_offset_fits and _is_players_color(x, offset_y) else 0
            sw_to_ne = sw_to_ne + 1 if x_offset_fits and y_offset_fits and \
                _is_players_color(offset_x, offset_y) else 0
            nw_to_se = nw_to_se + 1 if x_offset_fits and inv_offset_y_fits and \
                _is_players_color(offset_x, inv_offset_y) else 0

            if self.win_sequence_count in (w_to_e, s_to_n, sw_to_ne, nw_to_se):
                return True
    
    def serialize(self):
        return {
            'columns': self.columns,
            'rows': self.rows,
            'winSequenceCount': self.win_sequence_count,
            'gameBoard': self.game_board,
            'movesCounter': self.moves_counter,
        }
    
    @classmethod
    def deserialize(cls, data):
        return cls(
            columns = data['columns'],
            rows = data['rows'],
            win_sequence_count = data['winSequenceCount'],
            game_board = data['gameBoard'],
            moves_counter = data['movesCounter'],
        )


class Game:
    moves = [GameBoard.red, GameBoard.yellow]
    def __init__(
        self,
        players: list,
        game_id: Optional[int] = None,
        current_move: Optional[str] = None,
        game_board_data: Optional[dict] = None,
    ) -> None:
        self.game_id = game_id
        self.game_board = GameBoard.deserialize(game_board_data) \
            if game_board_data else GameBoard()
        self.current_move: str = current_move or random.choice(self.moves)
        self.players: dict = dict(zip(self.moves, players))

    def check_players_move_order(self, username):
        if self.players[self.current_move] != username:
            raise game_exceptions.WrongPlayerMoveError

    def make_move(self, username, players_move):
        self.check_players_move_order(username)
        if players_move < 0 or players_move > 6:
            raise game_exceptions.BadColumnChoiceError

        token_pos = self.game_board.make_move(players_move, self.current_move)
        self.current_move = (
            GameBoard.yellow if self.current_move == GameBoard.red 
            else GameBoard.red
        )

        return self.game_board.check_move(*token_pos)

    @property
    def game_field_str(self):
        return f'1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{str(self.game_board)}'

    @property
    def current_move_str(self):
        return (
            f'Current move: {GameBoard.tokens_repr[self.current_move]}'
            f'@{self.players[self.current_move]}'
        )

    def serialize(self) -> dict:
        return {
            'gameId': self.game_id,
            'players': list(self.players.values()),
            'currentMove': self.current_move,
            'gameBoardData': self.game_board.serialize(),
        }
    
    @classmethod
    def deserialize(cls, data):
        return cls(
            game_id = data['gameId'],
            players = data['players'],
            current_move = data['currentMove'],
            game_board_data = data['gameBoardData'],
        )
