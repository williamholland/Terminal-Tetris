#!/usr/bin/python

initial_fall_rate = 0.5
level = 0

def game_over():
    print "Game over."
    exit(0)

import locale

locale.setlocale(locale.LC_ALL, '')

logfile = open("tetris-log.txt","w")
def log(msg):
    logfile.write(str(msg)+"\n")

import copy
import os
import random
import select
import sys
import termios
import time
import tty
import curses

class colours:
    black = 90
    red = 1
    green = 2
    yellow = 3
    dark_yellow = 4
    blue = 5
    magenta = 6
    cyan = 7
    white = 8

class Score():

    def __init__(self):
        self.row = 1
        width = 2
        self.col = 13 * width
        self.score = 0

    def single_row(self):
        self.score += 40 * (level + 1)

    def double_row(self):
        self.score += 100 * (level + 1)

    def triple_row(self):
        self.score += 300 * (level + 1)

    def quad_row(self):
        self.score += 1200 * (level + 1)

    def draw(self, screen):
        screen.addstr(self.row, self.col, str(self.score))

class Cell():

    def draw(self, screen, x, y):
        width = 2
        if self.colour == 3:
            colour = curses.color_pair(self.colour) | curses.A_BOLD
        else:
            colour = curses.color_pair(self.colour)
        screen.addstr(y, x * width, self.string(), colour)

class Air(Cell):
    char = " "

    def __init__(self):
        self.colour = colours.white

    def __nonzero__(self):
        return False

    def __str__(self):
        return "Air"

    def string(self):
        #return self.char
        return "  "

class Solid(Cell):
    char = u"\u2588".encode('utf-8')

    def __nonzero__(self):
        return True

    def __str__(self):
        return "Solid"

    def string(self):
        return " %s" % self.char

class Edge(Solid):
    char = u"\u2588".encode('utf-8')

    def __init__(self):
        self.colour = colours.white

    def __str__(self):
        return "Edge"

class Tile(Solid):

    def __init__(self,colour):
        self.colour = colour

    def __str__(self):
        return "Tile"

    #def string(self):
        #return self.colour+self.char+colours.ENDC

class Input(object):

    def next(self):
        select.select( [sys.__stdin__.fileno()], [], [], None)
        return os.read(sys.__stdin__.fileno(), 1)

    def __init__(self):
        self.original_stty = termios.tcgetattr(sys.__stdin__)
        tty.setcbreak(sys.__stdin__, termios.TCSANOW)

    def exit(self):
        try:
            termios.tcsetattr(sys.__stdin__, termios.TCSANOW, self.original_stty)
        except:
            pass

    def __iter__(self):
        return self

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

    def draw(self, screen):
        for row in range(self.height()):
            for col in range(self.width()):
                cell = self[row][col]
                if cell:
                    y = self.row+row
                    x = self.col+col
                    cell.draw(screen, x, y)

    def disp(self):
        to_return = ''
        for row in self:
            for col in row:
                if col:
                    to_return+='#'
                else:
                    to_return+=' '
            to_return+='\n'
        return to_return

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
        if self.frozen:
            return
        self.col -= 1
        if not self.overlap_check(board):
            self.col += 1

    def move_right(self, board):
        if self.frozen:
            return
        self.col += 1
        if not self.overlap_check(board):
            self.col -= 1

    def move_down(self, board):
        if self.frozen:
            return
        self.row += 1
        if not self.overlap_check(board):
            self.row -= 1
            board.merge_piece(self)
            return False
        return True

    def rotate_clockwise(self):
        if self.frozen:
            return
        rows = []

        while self:
            rows.append(self.pop())

        for row in zip(*rows):
            self.append(row)

    def rotate(self, n, board):
        if self.frozen:
            return
        n = n % 4
        for _ in range(n):
            self.rotate_clockwise()
        if not self.overlap_check(board):
            for _ in range(4-n):
                self.rotate_clockwise()

    def __init__(self, tetrimino):

        self.frozen = False
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

class MOVE_DOWN(MOVE):
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
    's': MOVE_DOWN,
    'j': MOVE_DOWN,
    'q': QUIT_GAME,
}

class Curses():
    def __enter__(self):

        screen = curses.initscr()

        curses.curs_set(0)

        curses.start_color()

        curses.init_pair(1,curses.COLOR_RED,curses.COLOR_BLACK)
        curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
        curses.init_pair(3,curses.COLOR_YELLOW,curses.COLOR_BLACK)
        curses.init_pair(4,curses.COLOR_YELLOW,curses.COLOR_BLACK)
        curses.init_pair(5,curses.COLOR_BLUE,curses.COLOR_BLACK)
        curses.init_pair(6,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
        curses.init_pair(7,curses.COLOR_CYAN,curses.COLOR_BLACK)
        curses.init_pair(8,curses.COLOR_WHITE,curses.COLOR_BLACK)

        return screen

    def __exit__(self, type, value, traceback):
        os.system('clear')
        curses.endwin()

class Board(list):

    def draw(self, piece):

        # draw board
        for y, row in enumerate(self):
            for x, cell in enumerate(row):
                cell.draw(self.screen, x, y)

        #. draw piece
        piece.draw(self.screen)

        #. draw score
        self.score.draw(self.screen)

        self.screen.refresh()

    def merge_piece(self, piece):

        piece.frozen = True

        log("here")
        if piece.row == 0:
            game_over()

        for row in range(piece.height()):
            for col in range(piece.width()):
                self[piece.row+row][piece.col+col] = piece[row][col] or self[piece.row+row][piece.col+col]

        del piece

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

        if len(filled_rows) == 1:
            self.score.single_row()
        elif len(filled_rows) == 2:
            self.score.double_row()
        elif len(filled_rows) == 3:
            self.score.triple_row()
        elif len(filled_rows) == 4:
            self.score.quad_row()

        for i in reversed(filled_rows):
            self.pop(i)

        for _ in filled_rows:
            self.insert(0, empty_row)

    def __init__(self, screen):

        self.screen = screen
        self.score = Score()

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

from threading import Thread, Event

class MoveDown(Thread):
    def __init__(self, event, game):
        self.game = game

        Thread.__init__(self)

        self.stopped = event

    def run(self):
        while not self.stopped.wait(self.game.fall_rate):
            self.game.move_down()

class Game():

    def get_random_piece(self):
        return Piece(random.choice(PIECES))

    def quit(self, exit_val):
        self.input_generator.exit()
        self.stopFlag.set()
        curses.curs_set(1)
        exit(exit_val)

    def __init__(self, screen):

        self.fall_rate = initial_fall_rate
        self.board = Board(screen)
        self.curr_piece = self.get_random_piece()

        self.stopFlag = Event()
        thread = MoveDown(self.stopFlag, self)
        thread.start()
        self.input_generator = Input()

        self.actions = {
            MOVE_LEFT: lambda: self.curr_piece.move_left(self.board),
            MOVE_RIGHT: lambda: self.curr_piece.move_right(self.board),
            MOVE_DOWN: lambda: self.curr_piece.move_down(self.board),
            ROTATE_ANTICLOCKWISE: lambda: self.curr_piece.rotate(3, self.board),
            ROTATE_CLOCKWISE: lambda: self.curr_piece.rotate(1, self.board),
            QUIT_GAME: lambda: self.quit(0),
        }

    def move_down(self):
        if not self.curr_piece.move_down(self.board):
            self.curr_piece = self.get_random_piece()
        self.board.draw(self.curr_piece)

    def play(self):
        self.game_loop()
        try:
            self.game_loop()
        except:
            self.quit(0)

    def game_loop(self):
        while True:

            self.board.draw(self.curr_piece)

            key = self.input_generator.next()

            player_move = player_moves[key]

            self.actions.get(player_move, lambda: None)()

if __name__ == "__main__":
    with Curses() as screen:
        game = Game(screen)
        game.play()
