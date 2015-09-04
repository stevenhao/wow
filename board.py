class Board:

    def __init__(self, size=19):
        self.size = size
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.turn = 1
        self.gameover = False
        self.move_list = []

    def get(self, i, j):
        if not self.in_bounds(i, j):
            return 0
        return self.board[i][j]

    def valid_move(self, i, j):
        return self.in_bounds(i, j) and not self.get(i, j)

    def in_bounds(self, i, j):
        return 0 <= i < self.size and 0 <= j < self.size

    def set(self, i, j):
        self.board[i][j] = self.turn
        self._next_turn()

    def place_piece(self, i, j):
        who = self.turn
        self.set(i, j)

        if self.check_win(who, i, j):
            self.gameover = True
            self.winner = who
        self.move_list.append((i, j))
        return True

    def takeback(self):
        if self.move_list:
            i, j = self.move_list[-1]
            self.undo(i, j)
            self.move_list.pop()
            self.gameover = False
            self.winner = None

    def undo(self, i, j):
        self.board[i][j] = 0
        self._next_turn()
        # self.gameover = False

    def _next_turn(self):
        self.turn = 2 if self.turn == 1 else 1

    def check_win(self, who, i, j):
        for di, dj in [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if abs(x) + abs(y) > 0]:
            for ds in [0, -1, -2, -3, -4]:
              cnt = len([d for d in range(ds, ds + 5) if self.get(i + di * d, j + dj * d) == who])
              if cnt == 5:
                  return True
        return False






