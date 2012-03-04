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

class MoveMissingPromotionException(Exception):
    """
    Raised when a move would take a pawn to the end rank, but includes no
    promotion data
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

    def __repr__(self):
        return '%s.%s(%r, %r)' % (self.__class__.__module__,
                                  self.__class__.__name__,
                                  self.file_,
                                  self.rank_)

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
        if other is None:
            return False

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
    def __init__(self, start, end, promotion=None):
        if not isinstance(start, BoardSquare):
            start = BoardSquare(start)
        if not isinstance(end, BoardSquare):
            end = BoardSquare(end)

        self.start = start
        self.end = end
        self.promotion = promotion

    def __repr__(self):
        return '%s.%s(%r, %r, %r)' % (self.__class__.__module__,
                                      self.__class__.__name__,
                                      self.start,
                                      self.end,
                                      self.promotion)
    def __str__(self):
        string = "(%s -> %s)" % (self.start, self.end)
        if self.promotion is not None:
            string += " -> %s" % self.promotion
        return string

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
        return self.fen()

    def fen(self):
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
        if not isinstance(board_square, BoardSquare):
            board_square = BoardSquare(board_square)
        coords = board_square.to_board_coordinates()
        return self.squares[coords[0]][coords[1]]

    def check_status(self):
        """
        Returns the check status (a colour or None) of the board
        """
        return None
        #TODO raise NotImplementedError()

    def board_from_move(self, move, en_passant):
        """
        Returns a new board to which the supplied move has been applied
        """
        new_board_squares = copy.deepcopy(self.squares)

        start_coords = move.start.to_board_coordinates()
        end_coords = move.end.to_board_coordinates()
        if move.promotion is not None:
            piece = move.promotion
        else:
            piece = new_board_squares[start_coords[0]][start_coords[1]]
        new_board_squares[end_coords[0]][end_coords[1]] = piece
        new_board_squares[start_coords[0]][start_coords[1]] = None

        #Castling... (consider a refactor)
        if piece == 'k' or piece == 'K':
            if abs(ord(move.end.file_) - ord(move.start.file_)) == 2:
                #Grim...
                if (move.end == BoardSquare('c1')):
                    rook_from = BoardSquare('a1')
                    rook_to = BoardSquare('d1')
                elif (move.end == BoardSquare('g1')):
                    rook_from = BoardSquare('h1')
                    rook_to = BoardSquare('f1')
                elif (move.end == BoardSquare('c8')):
                    rook_from = BoardSquare('a8')
                    rook_to = BoardSquare('d8')
                elif (move.end == BoardSquare('g8')):
                    rook_from = BoardSquare('h1')
                    rook_to = BoardSquare('f1')
                rook_start = rook_from.to_board_coordinates()
                rook_end = rook_to.to_board_coordinates()
                piece = new_board_squares[rook_start[0]][rook_start[1]]
                new_board_squares[rook_start[0]][rook_start[1]] = None
                new_board_squares[rook_end[0]][rook_end[1]] = piece

        if move.end == en_passant:
            #Feels like a bit of a hack, but can only be one of two ranks...
            if en_passant.rank_ == 3:
                taken_pawn_coords = move.end.delta(0, 1).to_board_coordinates()
            elif en_passant.rank_ == 6:
                taken_pawn_coords = move.end.delta(0, -1).to_board_coordinates()
            else:
                raise Exception() #TODO
            new_board_squares[taken_pawn_coords[0]][taken_pawn_coords[1]] = None

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
            if en_passant == "-":
                self.en_passant = None
            else:
                self.en_passant = BoardSquare(en_passant)
            self.halfmove = int(halfmove)
            self.fullmove = int(fullmove)

    def fen(self):
        """
        Returns game state in Forsyth-Edwards Notation (FEN)

        http://en.wikipedia.org/wiki/Forsyth-Edwards_Notation
        """
        en_passant_str = self.en_passant or "-"
        return '%s %s %s %s %d %d' % (self.board.fen(), self.active,
                                      self.castling, en_passant_str,
                                      self.halfmove, self.fullmove)

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
        if not isinstance(start, BoardSquare):
            start = BoardSquare(start)

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
                can_take=False))

            for one in (-1, 1):
                moves.update(self.generate_moves(color, start, rank_delta, one,
                    1, must_take=True, can_en_passant=True))
        elif piece == 'k' or piece == 'K':
            for one in (-1, 0, 1):
                for two in (-1, 0, 1):
                    if one == two == 0:
                        continue
                    moves.update(self.generate_moves(color, start, one, two, 1))
            #TODO Disallow castling through check
            #CONSIDER replacing explicit square checks with "can rook->king"
            if piece == 'k':
                if self.castling.black_kingside:
                    if (self.board.piece_at_board_square('f8') is None) and (
                        self.board.piece_at_board_square('g8') is None):
                        moves.add(BasicMove('e8', 'g8'))
                if self.castling.black_queenside:
                    if (self.board.piece_at_board_square('b8') is None) and (
                        self.board.piece_at_board_square('c8') is None) and (
                        self.board.piece_at_board_square('d8') is None):
                        moves.add(BasicMove('e8', 'c8'))
            elif piece == 'K':
                if self.castling.white_kingside:
                    if (self.board.piece_at_board_square('f1') is None) and (
                        self.board.piece_at_board_square('g1') is None):
                        moves.add(BasicMove('e1', 'g1'))
                if self.castling.white_queenside:
                    if (self.board.piece_at_board_square('b1') is None) and (
                        self.board.piece_at_board_square('c1') is None) and (
                        self.board.piece_at_board_square('d1') is None):
                        moves.add(BasicMove('e1', 'c1'))
        elif piece == 'q' or piece == 'Q':
            for one in (-1, 0, 1):
                for two in (-1, 0, 1):
                    if one == two == 0:
                        continue
                    moves.update(self.generate_moves(color, start, one, two, 8))
        else:
            raise NotImplementedError(
                'No idea how to generate moves for %s' % piece)

        # Generate potential boards
        move_boards = zip(moves,
            [self.board.board_from_move(move, self.en_passant) for move in
             moves])

        # Determine check, prune
        valid_moves = set([move_board[0] for move_board in move_boards if
                           move_board[1].check_status() != self.active])

        return valid_moves

    def generate_moves(self, color, start, rank_delta, file_delta, limit,
                       can_take=True, must_take=False, can_en_passant=False):
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
                if (not must_take) or (can_en_passant and
                                       position == self.en_passant):
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

        piece = self.board.piece_at_board_square(move.start)

        #If we're trying to move pawn to end rank, make sure we have promotion
        #data
        if (piece == 'p' and move.end.rank_ == 1) or (
            piece == 'P' and move.end.rank_ == 8):
            if move.promotion is None:
                raise MoveMissingPromotionException()

        new_game = Game(self.fen())
        new_game.board = new_game.board.board_from_move(move, self.en_passant)

        #TODO Update check

        assert(self.active in ('b', 'w'))
        if self.active == 'b':
            new_game.active = 'w'
            new_game.fullmove += 1
        elif self.active == 'w':
            new_game.active = 'b'

        new_game.en_passant = None
        if piece == 'p' or piece == 'P':
            new_game.halfmove = 0
            if move.end.rank_ - move.start.rank_ == 2:
                new_game.en_passant = move.start.delta(0, 1)
            elif move.end.rank_ - move.start.rank_ == -2:
                new_game.en_passant = move.start.delta(0, -1)
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
    'K': u'♔',
    'Q': u'♕',
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
