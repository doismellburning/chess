# encoding: utf-8

"""
Python chess library by Kristian Glass (mail@doismellburning.co.uk)
"""

import copy
import pieces

WHITE_PIECES = frozenset('PRNBKQ')
BLACK_PIECES = frozenset([p.lower() for p in WHITE_PIECES])
WHITE_PROMOTION_OPTIONS = WHITE_PIECES - set('P')
BLACK_PROMOTION_OPTIONS = BLACK_PIECES - set('p')

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

class InvalidPromotionDataException(Exception):
    """
    Raised when a move includes promotion data, but would not result in pawn
    promotion, or is not a valid promotion
    """

def _colour_of_piece(piece):
    """
    Returns "w" or "b" depending on colour of piece string

    >>> _colour_of_piece('K')
    'w'

    >>> _colour_of_piece('p')
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
        Turns square into array coordinates suitable for _Board object internal
        array

        TODO Move to _Board?
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


class _CastlingState(object):
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
        """
        Returns Forsyth-Edwards Notation representation of castling state

        >>> _CastlingState().fen()
        'KQkq'
        """
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

class _Board(object):
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
        """
        Returns Forsyth-Edwards Notation representation of game board state

        >>> _Board().fen()
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        """
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
        Returns a set containing any colours in check in the current game state

        TODO: Optimisation for later - have an is_colour_in_check boolean, then
        we can stop generating moves for opposite colour once this becomes true
        """
        white_threats = set()
        black_threats = set()
        white_king_square = None
        black_king_square = None
        for file_ in [chr(ord('a') + x - 1) for x in xrange(1, 9)]:
            for rank_ in xrange(1, 9):
                square = BoardSquare(file_, rank_)
                piece = self.piece_at_board_square(square)
                if piece is None:
                    continue
                if piece == 'K':
                    white_king_square = square
                if piece == 'k':
                    black_king_square = square
                colour = _colour_of_piece(piece)
                piece_object = pieces.PIECE_MAP[piece]()
                threat_squares = piece_object.threat_squares(self, square)
                if colour == 'w':
                    white_threats.update(threat_squares)
                elif colour == 'b':
                    black_threats.update(threat_squares)
        check = []
        if white_king_square in black_threats:
            check.append('w')
        if black_king_square in white_threats:
            check.append('b')
        return set(check)

    def _threat_squares(self, color=None):
        """
        Returns a set of all squares threatened by the supplied color, or by all
        colors if None is supplied.

        Overly similar to check_status() which should probably be fixed...
        """
        threat_squares = set()
        for file_ in [chr(ord('a') + x - 1) for x in xrange(1, 9)]:
            for rank_ in xrange(1, 9):
                square = BoardSquare(file_, rank_)
                piece = self.piece_at_board_square(square)
                if piece is None:
                    continue
                if color != _colour_of_piece(piece):
                    continue
                piece_object = pieces.PIECE_MAP[piece]()
                threat_squares.update(piece_object.threat_squares(self, square))
        return threat_squares

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

        return _Board(squares=new_board_squares)


class Game(object):
    """
    Represents a whole game of chess (board state plus additional game state
    such as turn)
    """
	
    def __init__(self, fen=None):
        self.board = _Board()
        self.active = "w"
        self.castling = _CastlingState()
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1

        if fen:
            (board_str, active, castling, en_passant, halfmove, fullmove) = \
                fen.split(' ')
            self.board = _Board(fen=board_str)
            self.active = active
            self.castling = _CastlingState(castling)
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

    def _is_promotion_move(self, move):
        """
        Determines if a move should or shouldn't have promotion data
        """
        piece = self.board.piece_at_board_square(move.start)

        return (piece == 'p' and move.end.rank_ == 1) or (
            piece == 'P' and move.end.rank_ == 8)


    def validate_move(self, move):
        """
        Determines validity of the given move with respect to the game.

        Returns nothing, but may raise one of a number of exceptions relating
        to move invalidity
        """
        piece = self.board.piece_at_board_square(move.start)

        if piece is None:
            raise NoPieceAtSquareException()

        if not move.end in self.valid_ends(move.start):
            raise InvalidMoveException() #TODO More specific exception?

        if move.promotion:
            if not self._is_promotion_move(move):
                raise InvalidPromotionDataException()
            colour = _colour_of_piece(piece)
            if colour == 'w' and move.promotion not in WHITE_PROMOTION_OPTIONS:
                raise InvalidPromotionDataException()
            if colour == 'b' and move.promotion not in BLACK_PROMOTION_OPTIONS:
                raise InvalidPromotionDataException()
        else:
            if self._is_promotion_move(move):
                raise MoveMissingPromotionException()

    def valid_ends(self, start, check_check=True):
        """
        Returns the set of moves that the piece at the given square can make
        """
        if not isinstance(start, BoardSquare):
            start = BoardSquare(start)

        piece = self.board.piece_at_board_square(start)

        if piece is None:
            raise NoPieceAtSquareException('No piece at %s' % start)

        color = _colour_of_piece(piece)

        if self.active != color:
            raise NotYourTurnException()

        # Generate end squares
        ends = set()
        piece_object = pieces.PIECE_MAP[piece]()
        move_squares = piece_object.move_squares(self.board, start)
        threat_squares = piece_object.threat_squares(self.board, start)

        ends.update(move_squares)

        for threat_square in threat_squares - move_squares:
            if self.board.piece_at_board_square(threat_square) is not None:
                ends.add(threat_square)
            if self.en_passant == threat_square:
                if piece == 'p' or piece == 'P':
                    ends.add(threat_square)

        other_color = 'b' if color == 'w' else 'w' #Ugh
        opposing_threats = self.board._threat_squares(other_color)
        if piece == 'k' or piece == 'K' and start not in opposing_threats:
            def _can_castle_through_or_to(square_str):
                return self.board.piece_at_board_square(
                    square_str) is None and BoardSquare(
                    square_str) not in opposing_threats

            if piece == 'k':
                if self.castling.black_kingside:
                    if _can_castle_through_or_to(
                        'f8') and _can_castle_through_or_to('g8'):
                        ends.add(BoardSquare('g8'))
                if self.castling.black_queenside:
                    if _can_castle_through_or_to(
                        'b8') and _can_castle_through_or_to(
                        'c8') and _can_castle_through_or_to('d8'):
                        ends.add(BoardSquare('c8'))
            elif piece == 'K':
                if self.castling.white_kingside:
                    if _can_castle_through_or_to(
                        'f1') and _can_castle_through_or_to('g1'):
                        ends.add(BoardSquare('g1'))
                if self.castling.white_queenside:
                    if _can_castle_through_or_to(
                        'b1') and _can_castle_through_or_to(
                        'c1') and _can_castle_through_or_to('d1'):
                        ends.add(BoardSquare('c1'))

        if check_check:
            # Generate potential boards
            move_boards = zip(ends, [
            self.board.board_from_move(BasicMove(start, end), self.en_passant)
            for end in ends])

            # Determine check, prune
            valid_ends = set([move_board[0] for move_board in move_boards if
                               self.active not in move_board[1].check_status()])
        else:
            valid_ends = ends

        return valid_ends

    def _generate_ends(self, color, start, rank_delta, file_delta, limit,
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
                if can_take and _colour_of_piece(end_piece) != color:
                    ends.append(position)
                break

        return ends

    def move(self, move):
        """
        Returns a new Game instance with move applied

        >>> g1 = Game()
        >>> g1.fen()
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        >>> g2 = g1.move(BasicMove('a2', 'a4'))
        >>> g2.fen()
        'rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1'
        >>> g1.fen()
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        >>> g1.fen() == g2.fen()
        False
        """
        self.validate_move(move)

        piece = self.board.piece_at_board_square(move.start)

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

    def _can_move(self):
        """Returns True if the current side cannot move"""
        for file_ in [chr(ord('a') + x - 1) for x in xrange(1, 9)]:
            for rank_ in xrange(1, 9):
                square = BoardSquare(file_, rank_)
                piece = self.board.piece_at_board_square(square)
                if piece is None:
                    continue
                colour = _colour_of_piece(piece)
                if colour != self.active:
                    continue
                if self.valid_ends(square):
                    return True
        return False

    def is_checkmate(self):
        """
        Returns True if we are in checkmate, i.e. in check and unable to move

        >>> g = Game()
        >>> g.fen()
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        >>> g.is_checkmate()
        False

        >>> g = Game('rr2k3/8/8/8/8/8/8/K7 w - - 0 1')
        >>> g.is_checkmate()
        True
        """
        if self.active not in self.board.check_status():
            return False

        return not self._can_move()

    def is_stalemate(self):
        """
        Returns True if we are in stalemate, i.e. not in check but unable to
        move

        >>> g = Game()
        >>> g.fen()
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        >>> g.is_stalemate()
        False

        >>> g = Game('r1r5/1K6/7r/8/8/8/8/8 w - - 0 1')
        >>> g.is_stalemate()
        True
        """
        if self.active in self.board.check_status():
            return False

        return not self._can_move()

    def __str__(self):
        return self.fen()

_FEN_TO_UNICODE_MAP = {
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
}

def fen_to_unicode(piece):
    """
    Takes the Forsyth-Edwards representation of a piece and returns the
    Unicode symbol, or None if piece is None
    """
    if piece is None:
        return None
    return _FEN_TO_UNICODE_MAP[piece]
