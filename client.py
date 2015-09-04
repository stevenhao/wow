from sys import argv
from socket import socket as Socket, AF_INET, SOCK_STREAM, error as SocketError
import Tkinter as tk
from board import Board
from gui import BoardGui

class GoClient:

    def __init__(self, IP='127.0.0.1', port=5005):
        self.root = tk.Tk()
        self.IP = IP
        self.port = port
        self.players = []

    def start_game(self, player, size):
        self.players.append(player)
        self.board = Board(size)
        print 'beginning game as player %d' % player
        self.make_display()
        self.gui.start_game()

    def made_move(self, i, j):
        self.board.place_piece(i, j)
        self.gui.made_move()

    def passed_turn(self):
        self.board.pass_turn()
        self.gui.passed_turn()

    def game_over(self, score1, score2):
        self.gui.set_message('Game Over, Black: %d White: %d' % (score1, score2))
        self.board.gameover = True

    def on_click(self, i, j):
        if self.board.turn in self.players:
            self.send('MAKEMOVE %d %d' % (i, j))
            # self.receive('MADEMOVE %d %d' % (i, j))

    def on_quit(self):
        send('QUIT')
        self.gui.parent.destroy()

    def on_pass(self):
        if self.board.turn in self.players:
            self.send('PASSTURN')

    def run(self):
        # self.start_game(1)
        # self.start_game(2)
        self.connect_to_server()
        self.root.title('Python Online Five-In-A-Row')
        # root.resizable(0,0)
        self.root.mainloop()
        # print 'received data:', data

    def make_display(self):
        self.gui = BoardGui(parent=self.root, board=self.board, players=self.players)
        self.gui.on_click.append(self.on_click)
        self.gui.on_pass.append(self.on_pass)
        self.gui.pack(side='top', fill='both', expand='true', padx=4, pady=4)
       
    def receive(self, data):
        print 'receiving [%s]' % data
        data = data.split()
        if not data:
            return
        message = data[0]
        if message == 'BEGINGAME':
            self.start_game(int(data[1]), int(data[2]))
        elif message == 'MADEMOVE':
            i, j = map(int, data[1:3])
            self.made_move(i, j)
        elif message == 'PASSEDTURN':
            self.passed_turn()
        elif message == 'GAMEOVER':
            a, b = map(int, data[1:3])
            self.game_over(a, b)

    def send(self, data):
        print 'sending %s' % data
        self.skt.send(data)

    def connect_to_server(self):
        BUFFER_SIZE = 1024

        self.skt = Socket(AF_INET, SOCK_STREAM)
        self.skt.connect((self.IP, self.port))
        self.skt.setblocking(0)
        def listen():
            try:
                data = self.skt.recv(BUFFER_SIZE)
            except SocketError:
                pass
            else:
                if not data:
                    return
                for line in data.split('\n'):
                    self.receive(line)
            self.root.after(500, listen)

        listen()


if __name__ == '__main__':
    IP = '18.111.55.149'
    port = 5005
    if len(argv) >= 2:
        port = int(argv[1])
    if len(argv) >= 3:
        IP = argv[2]

    client = GoClient(IP=IP, port=port)
    client.run()