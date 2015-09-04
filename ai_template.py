import Tkinter as tk
from sys import argv
from gui import BoardGui
from collections import defaultdict
from board import Board
from copy import deepcopy
import random

class AI:
    def best_move(self, board):
        n = board.size
        legal_moves = [(i, j) for i in range(n) for j in range(n) if board.valid_move(i, j)]

        def feasible_move((i, j)):
            neighbors = ((i + di, j + dj) for di in [-2, -1, 0, 1, 2] for dj in [-2, -1, 0, 1, 2])
            return any(board.get(ni, nj) for ni, nj in neighbors)

        filtered_moves = filter(feasible_move, legal_moves)
        
        rnd = random.randint(0, len(filtered_moves) - 1)
        return 0, filtered_moves[rnd]



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Python Five-In-A-Row vs Computer')
    size = 19
    if len(argv) >= 2:
        size = int(argv[1])
    board = Board(size)
   
    gui = BoardGui(parent=root, board=board, players=[1, 2])
    ai = AI()

    def computer_move():
        score, move = ai.best_move(board)
        print 'making move %s, score = %d' % (move, score)
        i, j = move
        board.place_piece(i, j)
        # ai.score_board(board, verbose=True)
        gui.made_move()
        # if not board.gameover:
            # root.after(1000, computer_move)
        
    def on_click(i, j):
        if board.turn == 2:
            return
        if board.valid_move(i, j):
            who = board.turn
            board.place_piece(i, j)
            gui.made_move()
            if not board.gameover:
                root.after(10, computer_move)
            
    def on_pass():
        board.pass_turn()
        gui.passed_turn()

    gui.on_click.append(on_click)
    gui.on_pass.append(on_pass)
    gui.pack(side='top', fill='both', expand='true', padx=4, pady=4)

    # root.resizable(0,0)
    root.mainloop()