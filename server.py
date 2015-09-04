from sys import argv
import socket
from board import Board
import random, string

def generate_id(N):
    return ''.join(random.choice(string.letters) for i in xrange(N))

class GoServer:

    def __init__(self, IP='127.0.0.1', port=5005, BUFFER_SIZE=1024, size=19):
        self.TCP_IP = IP
        self.TCP_PORT = port
        self.BUFFER_SIZE = BUFFER_SIZE
        self.board = Board(size)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.TCP_IP, self.TCP_PORT))
        s.listen(1)
        self.size = size
        self.s = s

    def receive_players(self):
        self.conn = [None]*2
        self.addr = [None]*2

        for i in range(2):
            conn, addr = self.s.accept()
            print 'made connection %d: %s ' % (i, addr)
            self.conn[i] = conn
            self.addr[i] = addr

        self.game_num = {} # maps connection number {0, 1} to game number {1, 2}
        self.conn_num = {} # maps game number {1, 2} to connection number {0, 1}

        first_player_num = random.randint(1, 2)
        self.game_num[0] = first_player_num
        self.game_num[1] = 2 if first_player_num == 1 else 1

        self.conn_num[1] = 0 if first_player_num == 1 else 1
        self.conn_num[2] = 1 if first_player_num == 1 else 0

    def terminate(self):
        print 'closing connection'
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        print 'connection closed'
        for conn in self.conn:
            if conn:
                conn.close()

    def run_game(self):
        for i in range(2):
            self.send('BEGINGAME %d %d\n' % (self.game_num[i], self.size), i)
        
        while True:
            curr_player = self.board.turn
            curr_conn_num = self.conn_num[curr_player]
            data = self.conn[curr_conn_num].recv(self.BUFFER_SIZE)
            if not data:
                break

            print 'received %s from %s' % (data, self.addr[curr_conn_num])
            if data.startswith('MAKEMOVE'):
                tokens = data.split()
                if len(tokens) == 3:
                    try:
                        i = int(tokens[1])
                        j = int(tokens[2])
                    except ValueError:
                        continue

                    if self.board.place_piece(i, j):
                        self.send_all('MADEMOVE ' + str(i) + ' ' + str(j) + '\n')
            elif data.startswith('PASSTURN'):
                if self.board.pass_turn():
                    self.send_all('PASSEDTURN' + '\n')
                    if self.board.gameover:
                        score_white, score_black = self.board.score()
                        self.send_all('GAMEOVER %d %d \n' % (score_black, score_white))
                        break
            elif data.startswith('QUIT'):
                self.board.gameover = True
                score_white, score_black = self.board.score()
                self.send_all('GAMEOVER %d %d \n' % (score_black, score_white))
                break
        print 'done serving'

    def send(self, message, player):
        self.conn[player].send(message)

    def send_all(self, message):
        for conn in self.conn:
            conn.send(message)


            
if __name__ == '__main__':
    IP = '18.111.55.149'
    port = 5005
    size = 19
    if len(argv) >= 2:
        port = int(argv[1])
    if len(argv) == 3:
        try:
            size = int(argv[2])
        except ValueError:
            IP = argv[2]
    if len(argv) >= 4:
        IP = argv[2]
        size = int(argv[3])

    print 'serving on %s, port %d, size %d' % (IP, port, size)
    server = GoServer(IP=IP, port=port, size=size)
    try:
        server.receive_players()
        server.run_game()
    except Exception, err:
        print Exception, err
        print 'broke oops'
        server.terminate()
