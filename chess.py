# encoding: utf-8

"""
Python chess library by Kristian Glass (mail@doismellburning.co.uk)
"""

import copy


class InvalidSquareException(Exception):
    """
    Raised when trying to represent an invalid (file,rank) pair.
    """
    pass

class NoPieceAtSquareException(Exception):
    """
    Raised when trying to determine moves from a piece at a square with no
    piece.
    """
    pass

class NotYourTurnException(Exception):
    """
    Raised when attempting to move, or find valid moves of, a piece of the wrong
    colour by turn.
    """
    pass

class InvalidMoveException(Exception):
    """
    Raised when attempting to make an invalid move.
    """
    pass

def colour_of_piece(piece):
    """
    Returns "w" or "b" depending on colour of piece string

    >>> colour_of_piece('K')
    'w'

    >>> colour_of_piece('p')
    'b'

    TODO Use piece / colour objects?
    """
    if "A" <= piece <= "Z":
        return "w"
    if "a" <= piece <= "z":
        return "b"

class BoardSquare(object):
    """
    Small wrapper around what is essentially a (file,rank) pair. Note that
    trailing underscores are used for member names; in the case of file, to
    avoid collision; in the case of rank, for consistency
    """

    def __init__(self, *args):
        if len(args) == 1:
            file_rank = args[0]
            file_letter = file_rank[0]
            rank_number = int(file_rank[1])
        elif len(args) == 2:
            file_letter = args[0]
            rank_number = int(args[1])
        else:
            raise TypeError()

        if rank_number < 1 or rank_number > 8:
            raise InvalidSquareException('"%d" is not a valid rank' %
                                         rank_number)
        if file_letter < "a" or file_letter > "h":
            raise InvalidSquareException('"%s" is not a valid file' %
                                         file_letter)
        self.rank_ = rank_number
        self.file_ = file_letter

    def to_board_coordinates(self):
        """
        Turns square into array coordinates suitable for Board object internal
        array

        TODO Move to Board?
        """
        fst = 8 - self.rank_
        snd = ord(self.file_) - ord('a')
        return (fst, snd)

    def __str__(self):
        return "%s%d" % (self.file_, self.rank_)

    def delta(self, file_delta, rank_delta):
        """
        Returns a new BoardSquare offset by (file_delta, rank_delta), or None
        if that would be outside of the board
        """
        try:
            new_square = BoardSquare(chr(ord(self.file_) + file_delta),
                self.rank_ + rank_delta)
            return new_square
        except InvalidSquareException:
            #Boom, tried to move beyond limits
            return None

    def __eq__(self, other):
        return self.rank_ == other.rank_ and self.file_ == other.file_

    def __hash__(self):
        return hash(self.rank_) ^ hash(self.file_)


class CastlingState(object):
    """
    See FEN - tracks what castling is still possible
    """
    def __init__(self, fen=None):
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True

        if fen is not None:
            if 'K' not in fen:
                self.white_kingside = False
            if 'Q' not in fen:
                self.white_queenside = False
            if 'k' not in fen:
                self.black_kingside = False
            if 'q' not in fen:
                self.black_queenside = False

    def __str__(self):
        return self.fen()

    def fen(self):
        retval = ""

        if self.white_kingside:
            retval += "K"

        if self.white_queenside:
            retval += "Q"

        if self.black_kingside:
            retval += "k"

        if self.black_queenside:
            retval += "q"

        if not len(retval):
            retval = "-"

        return retval

class BasicMove(object):
    """
    Thin wrapper around a (start,end) pair of board squares
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return "(%s -> %s)" % (self.start, self.end)

    def __eq__(self, other):
        return self.start.__eq__(other.start) and self.end.__eq__(other.end)

    def __hash__(self):
        #TODO This means reverse move has same hash - consider fixing?
        return hash(self.start) ^ hash(self.end)

class Board(object):
    """
    Represents a chess board...
    """
    def __init__(self, squares=None, fen=None):
        if squares is not None:
            assert(len(squares) == 8)
            for rank_or_file_i_forget in squares:
                assert(len(rank_or_file_i_forget) == 8)
            self.squares = squares
        elif fen is not None:
            fen_lines = fen.split('/')
            squares = []
            for line in fen_lines:
                row = []
                for char in line:
                    #TODO Replace with less grim "is_int"
                    if char >= '1' and char <= '8':
                        for _ in xrange(int(char)):
                            row.append(None)
                    else:
                        row.append(char)
                assert(len(row) == 8)
                squares.append(row)
            assert(len(squares) == 8)
            self.squares = squares
        else:
            self.squares = [[None for _ in xrange(8)] for _ in xrange(8)]
            self.squares[0] = list('rnbqkbnr')
            self.squares[1] = ['p' for _ in xrange(8)]
            self.squares[6] = ['P' for _ in xrange(8)]
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
        """
        Returns (currently a string) representing the piece at the given square
        """
        coords = board_square.to_board_coordinates()
        return self.squares[coords[0]][coords[1]]

    def check_status(self):
        """
        Returns the check status (a colour or None) of the board
        """
        return None
        #TODO raise NotImplementedError()

    def board_from_move(self, move):
        """
        Returns a new board to which the supplied move has been applied
        """
        new_board_squares = copy.deepcopy(self.squares)

        #TODO Move this into a board.move()?
        start_coords = move.start.to_board_coordinates()
        end_coords = move.end.to_board_coordinates()
        new_board_squares[end_coords[0]][end_coords[1]] = \
            new_board_squares[start_coords[0]][start_coords[1]]
        new_board_squares[start_coords[0]][start_coords[1]] = None

        return Board(squares=new_board_squares)


class Game(object):
    """
    Represents a whole game of chess (board state plus additional game state
    such as turn)
    """
	
    def __init__(self, fen=None):
        self.board = Board()
        self.active = "w" #TODO Better
        self.castling = CastlingState()
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1

        if fen:
            (board_str, active, castling, en_passant, halfmove, fullmove) = \
                fen.split(' ')
            self.board = Board(fen=board_str)
            self.active = active
            self.castling = CastlingState(castling)
            self.en_passant = en_passant
            self.halfmove = int(halfmove)
            self.fullmove = int(fullmove)

    def fen(self):
        """
        Returns game state in Forsyth-Edwards Notation (FEN)

        http://en.wikipedia.org/wiki/Forsyth-Edwards_Notation
        """
        en_passant_str = self.en_passant or "-"
        return '%s %s %s %s %d %d' % (self.board, self.active, self.castling,
                                      en_passant_str, self.halfmove,
                                      self.fullmove)

    def is_move_valid(self, move):
        """
        Determines validity of the given move with respect to the game
        """
        #print [str(move) for move in self.valid_moves(move.start)]
        return bool(move in self.valid_moves(move.start))

    def valid_moves(self, start):
        """
        Returns the set of moves that the piece at the given square can make
        """
        piece = self.board.piece_at_board_square(start)

        if piece is None:
            raise NoPieceAtSquareException('No piece at %s' % start)

        color = colour_of_piece(piece)

        if self.active != color:
            raise NotYourTurnException()

        # Generate moves
        moves = set()
        if piece == 'r' or piece == 'R':
            #TODO Figure out what loop I want for this?
            moves.update(self.generate_moves(color, start, 0, +1, 8))
            moves.update(self.generate_moves(color, start, 0, -1, 8))
            moves.update(self.generate_moves(color, start, +1, 0, 8))
            moves.update(self.generate_moves(color, start, -1, 0, 8))
        elif piece == 'n' or piece == 'N':
            for one in (-1, 1):
                for two in (-2, 2):
                    moves.update(self.generate_moves(color, start, one,
                        two, 1))
                    moves.update(self.generate_moves(color, start, two,
                        one, 1))
        elif piece == 'b' or piece == 'B':
            for one in (-1, 1):
                for two in (-1, 1):
                    moves.update(self.generate_moves(color, start, one,
                        two, 8))
        elif piece == 'p' or piece == 'P':
            starting_rank = False
            rank_delta = 0
            if piece == 'p':
                rank_delta = -1
                if start.rank_ == 7:
                    starting_rank = True
            if piece == 'P':
                rank_delta = 1
                if start.rank_ == 2:
                    starting_rank = True

            if starting_rank:
                limit = 2
            else:
                limit = 1

            moves.update(self.generate_moves(color, start, rank_delta, 0, limit,
                False))

            #TODO Capturing moves...
        elif piece == 'k' or piece == 'K':
            for one in (-1, 0, 1):
                for two in (-1, 0, 1):
                    if one == two == 0:
                        continue
                    moves.update(self.generate_moves(color, start, one, two, 1))
            #TODO Castling
        else:
            raise NotImplementedError()

        # Generate potential boards
        move_boards = zip(moves, map(self.board.board_from_move, moves))

        # Determine check, prune
        valid_moves = set([move_board[0] for move_board in move_boards if
                           move_board[1].check_status() != self.active])

        return valid_moves

    def generate_moves(self, color, start, rank_delta, file_delta, limit,
                       can_take=True):
        """
        TODO Document this in a way that doesn't feel silly
        """
        #print "Generating moves from %s with delta (%d,%d) and limit %d" % \
        #      (start, rank_delta, file_delta, limit)
        ends = []
        position = start
        for _ in xrange(limit):
            position = position.delta(rank_delta=rank_delta,
                file_delta=file_delta)
            if position is None:
                break

            end_piece = self.board.piece_at_board_square(position)

            if end_piece is None:
                ends.append(position)
            else:
                if can_take and colour_of_piece(end_piece) != color:
                    ends.append(position)
                break

        moves = set([BasicMove(start, end) for end in ends])
        return moves

    def move(self, move):
        if not self.is_move_valid(move):
            raise InvalidMoveException()

        new_game = Game(self.fen())
        new_game.board = new_game.board.board_from_move(move)

        #TODO Castling
        #TODO Promotion
        #TODO Update check
        #TODO Update en passant

        assert(self.active in ('b', 'w'))
        if self.active == 'b':
            new_game.active = 'w'
            new_game.fullmove += 1
        elif self.active == 'w':
            new_game.active = 'b'

        piece = self.board.piece_at_board_square(move.start)
        if piece == 'p' or piece == 'P':
            new_game.halfmove = 0
        else:
            new_game.halfmove += 1

        #Loose but sufficient checks for castling
        if piece == 'r':
            if move.start.file_ == 'a':
                new_game.castling.black_queenside = False
            elif move.start.file_ == 'h':
                new_game.castling.black_kingside = False
        elif piece == 'k':
            new_game.castling.black_queenside = False
            new_game.castling.black_kingside = False
        elif piece == 'R':
            if move.start.file_ == 'a':
                new_game.castling.white_queenside = False
            elif move.start.file_ == 'h':
                new_game.castling.white_kingside = False
        elif piece == 'K':
            new_game.castling.white_queenside = False
            new_game.castling.white_kingside = False

        return new_game

    def display_move(self, move):
        if not self.is_move_valid(move):
            raise InvalidMoveException()

        raise NotImplementedError()

    def __str__(self):
        return self.fen()

FEN_TO_UNICODE_MAP = {
    'K': u'♕',
    'Q': u'♔',
    'R': u'♖',
    'B': u'♗',
    'N': u'♘',
    'P': u'♙',
    'k': u'♚',
    'q': u'♛',
    'r': u'♜',
    'b': u'♝',
    'n': u'♞',
    'p': u'♟',
    None: None,
}

def fen_to_unicode(piece):
    return FEN_TO_UNICODE_MAP[piece]
