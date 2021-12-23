class ColumnIsFullError(Exception):
    pass


class GameBoard:
    red = 'R'
    yellow = 'Y'
    tokens_repr = {
        None: '⚪',
        red: '🔴',
        yellow: '🟡',
    }

    def __init__(self, columns = 7, rows = 6, win_sequence_count = 4) -> None:
        self.columns, self.rows = columns, rows
        self.win_sequence_count = win_sequence_count
        self.game_board = [[None for _ in range(self.rows)] for _ in range(self.columns)]
        self.moves_counter = 0

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
            raise ColumnIsFullError
        column[row_idx] = token
        self.game_board[column_idx] = column
        self.moves_counter += 1
        return column_idx, row_idx

    def check_move(self, x, y):
        token = self.game_board[x][y]
        def _associates(_x,_y):
            return self.game_board[_x][_y] == token

        w_to_e, s_to_n, sw_to_ne, nw_to_se = 0, 0, 0, 0
        for offset in range(-3, 3):
            offset_x, offset_y, inv_offset_y = x + offset, y + offset, y - offset

            x_offset_fits = offset_x >= 0 and offset_x <= self.rows -1
            y_offset_fits = offset_y >= 0 and offset_y <= self.columns - 1
            inv_offset_y_fits = inv_offset_y >= 0 and offset_y <= self.columns - 1

            w_to_e = w_to_e + 1 if x_offset_fits and _associates(offset_x, y) else 0
            s_to_n = s_to_n + 1 if y_offset_fits and _associates(x, offset_y) else 0
            sw_to_ne = sw_to_ne + 1 if x_offset_fits and y_offset_fits and _associates(offset_x, offset_y) else 0
            nw_to_se = nw_to_se + 1 if x_offset_fits and inv_offset_y_fits and _associates(x, offset_y) else 0
            
            if self.win_sequence_count in (w_to_e, s_to_n, sw_to_ne, nw_to_se):
                return True
