"""
libchess.py: Python chess library by Kristian Glass (mail@doismellburning.co.uk)
"""

import copy


class InvalidSquareException(Exception):
    """
    Raised when trying to represent an invalid (file,rank) pair
    """
    pass

def colour_of_piece(piece):
    """
    Returns "w" or "b" depending on colour of piece string

    TODO Use piece / colour objects?
    """
    if "A" <= piece <= "Z":
        return "w"
    if "a" <= piece <= "z":
        return "b"

class BoardSquare(object):
    """
    Small wrapper around what is essentially a (file,rank) pair
    """

    def __init__(self, file_letter, rank_number):
        """
        TODO Consider changing this to just take "e5"?
        """
        if rank_number < 1 or rank_number > 8:
            raise InvalidSquareException('"%d" is not a valid rank' %
                                         rank_number)
        if file_letter < "a" or file_letter > "h":
            raise InvalidSquareException('"%s" is not a valid file' %
                                         file_letter)
        self.rank = rank_number
        self.file = file_letter

    def to_board_coordinates(self):
        """
        Turns square into array coordinates suitable for Board object internal
        array

        TODO Move to Board?
        """
        fst = 8 - self.rank
        snd = ord(self.file) - ord('a')
        return (fst, snd)

    def __str__(self):
        return "%s%d" % (self.file, self.rank)

    def delta(self, file_delta, rank_delta):
        """
        Returns a new BoardSquare offset by (file_delta, rank_delta), or None
        if that would be outside of the board
        """
        try:
            new_square = BoardSquare(chr(ord(self.file) + file_delta),
                self.rank + rank_delta)
            return new_square
        except InvalidSquareException:
            #Boom, tried to move beyond limits
            return None

    def __eq__(self, other):
        return self.rank == other.rank and self.file == other.file

    def __hash__(self):
        return hash(self.rank) ^ hash(self.file)


class CastlingState(object):
    """
    See FES notation - tracks what castling is still possible
    """
    def __init__(self):
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True

    def __str__(self):
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
        raise NotImplementedError()

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


class Chess(object):
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
            self.castling = castling
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
        #TODO Check turn etc. - or should valid_moves?
        return move in self.valid_moves(move.start())

    def valid_moves(self, start):
        """
        Returns the set of moves that the piece at the given square can make
        """
        piece = self.board.piece_at_board_square(start)

        assert(piece != None)

        color = colour_of_piece(piece)

        assert(self.active == color)

        # Generate moves
        moves = set()
        if piece == 'r' or piece == 'R':
            #TODO Figure out what loop I want for this?
            moves.update(self.generate_moves(color, start, 0, +1, 8))
            moves.update(self.generate_moves(color, start, 0, -1, 8))
            moves.update(self.generate_moves(color, start, +1, 0, 8))
            moves.update(self.generate_moves(color, start, -1, 0, 8))
        elif piece == 'n' or piece == 'N':
            for rank_delta in (-1, 1):
                for file_delta in (-2, 2):
                    moves.update(self.generate_moves(color, start, rank_delta,
                        file_delta, 1))
                    moves.update(self.generate_moves(color, start, file_delta,
                        rank_delta, 1))
        elif piece == 'p' or piece == 'P':
            starting_rank = False
            rank_delta = 0
            if piece == 'p':
                rank_delta = -1
                if start.rank == 7:
                    starting_rank = True
            if piece == 'P':
                rank_delta = 1
                if start.rank == 2:
                    starting_rank = True
            moves.update(self.generate_moves(color, start, rank_delta, 0, 1,
                False))

            if starting_rank:
                moves.update(self.generate_moves(color, start, 2 * rank_delta,
                    0, 1, False))

            #TODO Capturing moves...
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
        assert(self.is_move_valid(move))

        raise NotImplementedError()

    def display_move(self, move):
        assert(self.is_move_valid(move))

        raise NotImplementedError()

    def __str__(self):
        return self.fen()