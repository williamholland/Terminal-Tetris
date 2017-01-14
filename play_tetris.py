#!/usr/bin/python

def game_over():
    print "Game over."
    exit(0)

logfile = open("tetris-log.txt","w")
def log(msg):
    logfile.write(str(msg)+"\n")

import os
import random
import sys

import termios
import fcntl

class colours:
    black = '\033[91m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    dark_yellow = '\033[0;33m'
    blue = '\033[94m'
    magenta = '\033[95m'
    cyan = '\033[96m'
    white = '\033[97m'
    ENDC = '\033[0m'

class Air():
    char = " "

    def __nonzero__(self):
        return False

    def __str__(self):
        return "Air"

    def string(self):
        return self.char

class Solid():
    char = u"\u2588".encode('utf-8')

    def __nonzero__(self):
        return True

    def __str__(self):
        return "Solid"

    def string(self):
        return self.char

class Edge(Solid):
    char = u"\u2588".encode('utf-8')

    def __str__(self):
        return "Edge"

class Tile(Solid):

    def __init__(self,colour):
        self.colour = colour

    def __str__(self):
        return "Tile"

    def string(self):
        return self.colour+self.char+colours.ENDC

def getch():
  fd = sys.stdin.fileno()

  oldterm = termios.tcgetattr(fd)
  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)

  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

  try:
    while 1:
      try:
        c = sys.stdin.read(1)
        break
      except IOError: pass
  finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  return c

# DECLARE ALL THE CONSTANTS
BOARD_WIDTH = 12
BOARD_HEIGHT = 22

r = Tile(colours.red)
g = Tile(colours.green)
y = Tile(colours.yellow)
b = Tile(colours.blue)
m = Tile(colours.magenta)
c = Tile(colours.cyan)
o = Tile(colours.dark_yellow)

a = Air()

class Tetrimino(list):

    def __init__(self, colour, shape):

        self.colour = colour

        for i in [[col for col in row] for row in shape]:
            self.append(i)

class Piece(list):

    def tilize(self, val):
        if val:
            return Tile(self.colour)
        return Air()

    def get_random_position(self):

        self.row = 0
        self.col = random.randrange(1, BOARD_WIDTH-self.width())

    def position(self):
        return self.col, self.row


    def overlap_check(self, board):
        for row in range(self.height()):
            for col in range(self.width()):
                if isinstance(board[self.row+row][self.col+col],Solid) and isinstance(self[row][col],Solid):
                    return False
        return True

    def move_left(self, board):
        self.col -= 1
        if not self.overlap_check(board):
            self.col += 1

    def move_right(self, board):
        self.col += 1
        if not self.overlap_check(board):
            self.col -= 1

    def move_down(self, board):
        self.row += 1
        if not self.overlap_check(board):
            self.row -= 1
            board.merge_piece(self)
            return False
        return True

    def rotate_clockwise(self):
        rows = []

        while self:
            rows.append(self.pop())

        for row in zip(*rows):
            self.append(row)

    def rotate(self, n, board):
        n = n % 4
        for _ in range(n):
            self.rotate_clockwise()
        if not self.overlap_check(board):
            for _ in range(4-n):
                self.rotate_clockwise()

    def __init__(self, tetrimino):

        self.colour = tetrimino.colour

        for i in [[self.tilize(col) for col in row] for row in tetrimino]:
            self.append(i)

        self.get_random_position()

    def width(self):
        return len(self[0])

    def height(self):
        return len(self)

I = Tetrimino(colours.cyan,
        [[1], [1], [1], [1]])

J = Tetrimino(colours.blue,
    [[0, 1],
     [0, 1],
     [1, 1]])

L = Tetrimino(colours.dark_yellow,
    [[1, 0],
     [1, 0],
     [1, 1]])

O = Tetrimino(colours.yellow,
    [[1, 1],
     [1, 1]])

S = Tetrimino(colours.green,
    [[1, 0],
     [1, 1],
     [0, 1]])

T = Tetrimino(colours.magenta,
    [[1, 0],
     [1, 1],
     [1, 0]])

Z = Tetrimino(colours.red,
    [[0, 1],
     [1, 1],
     [1, 0]])

PIECES = [I,J,L,O,S,T,Z]

class MOVE():
    pass

class MOVE_LEFT(MOVE):
    pass

class MOVE_RIGHT(MOVE):
    pass

class ROTATE_ANTICLOCKWISE(MOVE):
    pass

class ROTATE_CLOCKWISE(MOVE):
    pass

class NO_MOVE(MOVE):
    pass

class QUIT_GAME(MOVE):
    pass

player_moves = {
    'a': MOVE_LEFT,
    'h': MOVE_LEFT,
    'd': MOVE_RIGHT,
    'l': MOVE_RIGHT,
    'w': ROTATE_ANTICLOCKWISE,
    ' ': ROTATE_ANTICLOCKWISE,
    'e': ROTATE_CLOCKWISE,
    'k': ROTATE_CLOCKWISE,
    'i': ROTATE_CLOCKWISE,
    's': NO_MOVE,
    'j': NO_MOVE,
    'q': QUIT_GAME,
}

class Board(list):

    def draw(self, curr_piece):
        os.system('cls' if os.name=='nt' else 'clear')
        
        import copy
        to_print = copy.deepcopy(self)

        for row in range(curr_piece.height()):
            for col in range(curr_piece.width()):
                if curr_piece[row][col]:
                   to_print[curr_piece.row+row][curr_piece.col+col] = curr_piece[row][col]

        for row in to_print:
            for cell in row:
                print cell.string(),
            print ""

    def merge_piece(self, piece):
        if piece.row == 0:
            game_over()
        for row in range(piece.height()):
            for col in range(piece.width()):
                self[piece.row+row][piece.col+col] = piece[row][col] or self[piece.row+row][piece.col+col]

        self.remove_full_rows()

    def remove_full_rows(self):
        # TODO row object
        empty_row = [Air() for _ in range(BOARD_WIDTH)]
        empty_row[0] = Edge()
        empty_row[BOARD_WIDTH-1] = Edge()

        def filled(row):
            return all(row) and not all([isinstance(x, Edge) for x in row])

        filled_rows = []
        for i, row in enumerate(self):
            if filled(row):
                filled_rows.append(i)

        for i in reversed(filled_rows):
            self.pop(i)

        for _ in filled_rows:
            self.insert(0, empty_row)

    def __init__(self):
        board = [[Air() for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
        for i in range(BOARD_HEIGHT):
            board[i][0] = Edge()
            board[i][BOARD_WIDTH-1] = Edge()
        for i in range(BOARD_WIDTH):
            board[BOARD_HEIGHT-1][i] = Edge()

        for row in board:
            self.append(row)

    def height(self):
        return len(self)

    def width(self):
        return len(self[0])


class Game():

    def get_random_piece(self):
        return Piece(random.choice(PIECES))

    def __init__(self):

        self.board = Board()
        self.curr_piece = self.get_random_piece()
        self.actions = {
            MOVE_LEFT: lambda: self.curr_piece.move_left(self.board),
            MOVE_RIGHT: lambda: self.curr_piece.move_right(self.board),
            ROTATE_ANTICLOCKWISE: lambda: self.curr_piece.rotate(3, self.board),
            ROTATE_CLOCKWISE: lambda: self.curr_piece.rotate(1, self.board),
            QUIT_GAME: lambda: sys.exit(0),
        }

    def play(self):

        while True:

            self.board.draw(self.curr_piece)

            player_move = getch()

            move_down = lambda: None
            player_move = player_moves[player_move]
            self.actions.get(player_move, move_down)()

            if not self.curr_piece.move_down(self.board):
                del self.curr_piece
                self.curr_piece = self.get_random_piece()

if __name__ == "__main__":
    game = Game()
    game.play()
