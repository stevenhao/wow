import Tkinter as tk
from sys import argv
from gui import BoardGui
from collections import defaultdict
from board import Board
from copy import deepcopy
import random


class AI:
    def count_partial(self, num, side):
        def count(processed):
            return processed[num][side]
        return count

    def process(self, board, turn, move):
        c2, c1 = turn, (1 if turn == 2 else 2)

        n = len(board)
        def in_bounds((i, j)):
            return 0 <= i < n and 0 <= j < n

        ret = [[0] * 3 for _ in range(6)]

        for di, dj in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
            if move:
                pi, pj = move
                squares = [(pi + di*d, pj + dj*d) for d in range(-4, 5)]
                squares = filter(in_bounds, squares)
                a, b = [[0] * (len(squares) + 1) for _ in range(2)]
                for pos, (i, j)in enumerate(squares):
                    for prf, c in [(a, c1), (b, c2)]:
                        prf[pos + 1] = prf[pos] + (1 if board[i][j] == c else 0)

                ab = zip(a, b)
                for start, end in zip(ab, ab[5:]):
                    a, b = (e - s for s, e in zip(start, end))
                    if a == 1:
                        ret[b][2] -= 1
                    elif b == 0:
                        ret[a][1] += 1
                        ret[a - 1][1] -= 1
            else:
                for i in range(n):
                    for j in range(n):
                        squares = [(i + di*d, j + dj*d) for d in range(5)]
                        if in_bounds(squares[-1]):
                            a, b = (sum(board[i][j] == c for i, j in squares) for c in [c1, c2])                
                            if a == 0:
                                ret[b][2] += 1
                            elif b == 0:
                                ret[a][1] += 1

        return ret

    def gain(self, x):
        return lambda y: x * y


    def make_features(self): # positive -> white, negative -> black
        c = lambda x: self.count_partial(x, 1)
        d = lambda x: self.count_partial(x, 2)
        g = self.gain
        features = [
            (c(1), g(1)),
            (c(2), g(10)),
            (c(3), g(100)),
            (c(4), g(1000)),
            (c(5), g(1000000)),
            (d(1), g(-1)),
            (d(2), g(-18)),
            (d(3), g(-180)),
            (d(4), g(-1800)),
            (d(5), g(-1800000))
            ]
        self.features = features

    def __init__(self):
        self.make_features()

    def score_board(self, board, lastmove=None, verbose=False):
        if self.explored != None:
            self.explored += 1
        self.explored += 1
        processed = self.process(board.board, board.turn, lastmove)
        sm = 0
        for feature, func in self.features:
            ft = feature(processed)
            val = func(ft)
            if verbose:
                print 'ft, val: %d, %d' % (ft, val)
            sm += val
        return sm


    def best_move(self, board, depth=4, cands=3):
        n = board.size
        legal_moves = [(i, j) for i in range(n) for j in range(n) if board.valid_move(i, j)]
        def feasible_move((i, j)):
            neighbors = ((i + di, j + dj) for di in [-2, -1, 0, 1, 2] for dj in [-2, -1, 0, 1, 2])
            return any(board.get(ni, nj) for ni, nj in neighbors)
        
        def score_move((i, j), depth=0, cands=1):
            # next = deepcopy(board)
            if cands <= 0:
                cands = 1
            board.set(i, j)

            ret = self.score_board(board, (i, j))
            if depth:
                score, move = self.best_move(board, depth - 1, cands)            
                ret -= score
            board.undo(i, j)
            noise = random.randint(0, 5)
            ret += noise
            return ret

        filtered_moves = filter(feasible_move, legal_moves)
        scored_moves = sorted([(score_move(move), move) for move in filtered_moves])

        if depth == 0:
            return scored_moves[-1]

        best_score, best_move = scored_moves[-1]
        thres = best_score - (abs(best_score) * (.7 if best_score > 0 else 2))

        best_moves = [move for score, move in scored_moves[-cands:] if score >= thres]

        winning_moves = [(score, move) for score, move in scored_moves[-cands:] if score >= 100000]
        if winning_moves:
            return winning_moves[0]
        scored_best_moves = [(score_move(move, depth, cands), move) for move in best_moves]
        scored_best_moves.sort()

        return scored_best_moves[-1]



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Python Five-In-A-Row vs Computer')
    size = 19
    if len(argv) >= 2:
        size = int(argv[1])
    board = Board(size)
   
    gui = BoardGui(parent=root, board=board, players=[1])
    ai = AI()
    comp_player = 2

    def computer_move():
        ai.explored = 0
        score, move = ai.best_move(board)
        print 'explored %d positions' % ai.explored
        print 'making move %s, move score = %d' % (move, score)
        i, j = move
        board.place_piece(i, j)
        curscore = ai.score_board(board)
        print 'board score: %d' % curscore
        gui.made_move()
#        if not board.gameover:
#            root.after(1000, computer_move)
        
    def on_undo():
        board.takeback()
        gui.made_move()

    def on_new_game():
        print 'new game'
        board.__init__()
        gui.made_move()

    def on_click(i, j):
        if board.gameover:
            return
        if board.turn == 2:
            return
        if board.valid_move(i, j):
            who = board.turn
            board.place_piece(i, j)
            gui.made_move()
            if not board.gameover and board.turn == comp_player:
                root.after(10, computer_move)
            
    def on_pass():
        board.pass_turn()
        gui.passed_turn()

    gui.on_click.append(on_click)
    gui.on_pass.append(on_pass)
    gui.on_undo.append(on_undo)
    gui.on_new_game.append(on_new_game)
    gui.pack(side='top', fill='both', expand='true', padx=4, pady=4)

    # root.resizable(0,0)
    root.mainloop()
