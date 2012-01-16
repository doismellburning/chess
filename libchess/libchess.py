
class BoardSquare(object):
    def __init__(self, file, rank): #TODO Consider changing this to just take "e5"?
        assert(rank >= 1 and rank <= 8)
        assert(file >= "a" and file <= "h")
        self.rank = rank
        self.file = file

    def to_board_coordinates(self):
        fst = 8 - self.rank
        snd = ord(self.file) - ord('a')
        return (fst, snd)

class CastlingState(object):
    def __init__(self):
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True

    def __str__(self):
        str = ""

        if self.white_kingside:
            str += "K"

        if self.white_queenside:
            str += "Q"

        if self.black_kingside:
            str += "k"

        if self.black_queenside:
            str += "q"

        if not len(str):
            str = "-"

        return str

class BasicMove(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Board(object):
    def __init__(self):
        self.squares = [[None for i in xrange(8)] for j in xrange(8)]
        self.squares[0] = list('rnbqkbnr')
        self.squares[1] = ['p' for i in xrange(8)]
        self.squares[6] = ['P' for i in xrange(8)]
        self.squares[7] = list('RNBQKBNR')

    def __str__(self):
        rows = list()
        for row in self.squares:
            row_str = ''
            empty_count = 0
            for square in row:
                if square == None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += "%d" % empty_count
                        empty_count = 0
                    row_str += square
            if empty_count > 0:
                row_str += "%d" % empty_count
            rows.append(row_str)

        return "/".join(rows)

    def piece_at_board_square(self, board_square):
        coords = board_square.to_board_coordinates()
        return self.squares[coords[0]][coords[1]]

class Chess(object):
	
    def __init__(self, fen=None):
        self.board = Board()
        self.active = "w" #TODO Better
        self.castling = CastlingState()
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1

        if fen:
            raise NotImplementedError()

    def fen(self):
        en_passant_str = self.en_passant or "-"
        return '%s %s %s %s %d %d' % (self.board, self.active, self.castling, en_passant_str, self.halfmove, self.fullmove)

    def is_move_valid(self, move):
        return self.valid_moves(move.start()).contains(move)

    def valid_moves(self, start):
        raise NotImplementedError()

    def move(self, move):
        assert(self.is_move_valid(move))

        raise NotImplementedError()

    def display_move(self, move):
        assert(self.is_move_valid(move))

        raise NotImplementedError()