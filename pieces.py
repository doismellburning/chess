# encoding: utf-8

"""
Base class, and classes for, chess pieces
"""

import chess

def _colour_of_piece(piece):
    return chess._colour_of_piece(piece)

class Piece:
    """
    Represents a chess piece. Extend this class if attempting to add your own
    piece type.
    """
    fen = None

    def __init__(self):
        pass

    def color(self):
        """
        Returns piece's color (currently either 'w' or 'b' - this is likely to
        change in future versions)
        """
        return _colour_of_piece(self.fen)

    def move_squares(self, board, start):
        """
        Returns a set of squares to which, given the board state, this piece
        could move to.

        Compare with threat_squares. For many standard chess pieces,
        threat_squares returns a superset of move_squares (see below note about
        things not included by move_squares); for the Pawn, this method will
        only return the non-diagonal forward moves.

        Currently this does not include squares to which this piece could move
        by taking another piece - see end_squares for this. Perhaps it should.
        Semantics of this method are likely to change in future versions.
        """
        raise NotImplementedError()

    def threat_squares(self, board, start):
        """
        Returns the union of the set of squares at which if there were an
        opposing piece, this piece could capture it, and the squares at which
        there is an opposing piece that this piece could capture.

        Compare with move_squares. For many standard chess pieces, this will
        return a superset of move_squares, but for the Pawn, this will return
        the two diagonal movements but not the directly forwards ones.

        Semantics of this method are likely to change in future versions.
        """
        raise NotImplementedError()

    def end_squares(self, board, start):
        """
        Returns the set of all possible squares at which this piece could end
        after a movement. Generally this is the union of move_squares and
        threat_squares, but for some Fairy pieces, this will not be the case.
        """
        return self.move_squares(board, start).union(self.threat_squares(board,
            start))

    def _generate_ends(self, board, start, rank_delta, file_delta, limit,
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

            end_piece = board.piece_at_board_square(position)

            if end_piece is None:
                ends.append(position)
            else:
                if can_take and _colour_of_piece(end_piece) != self.color():
                    ends.append(position)
                break

        return ends

class Knight(Piece):
    def move_squares(self, board, start):
        ends = set()
        for one in (-1, 1):
            for two in (-2, 2):
                ends.update(self._generate_ends(board, start, one, two, 1))
                ends.update(self._generate_ends(board, start, two, one, 1))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)

class BlackKnight(Knight):
    fen = 'n'

class WhiteKnight(Knight):
    fen = 'N'

class Rook(Piece):
    def move_squares(self, board, start):
        ends = set()
        ends.update(self._generate_ends(board, start, 0, +1, 8))
        ends.update(self._generate_ends(board, start, 0, -1, 8))
        ends.update(self._generate_ends(board, start, +1, 0, 8))
        ends.update(self._generate_ends(board, start, -1, 0, 8))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)

class BlackRook(Rook):
    fen = 'r'

class WhiteRook(Rook):
    fen = 'R'

class Bishop(Piece):
    def move_squares(self, board, start):
        ends = set()
        for one in (-1, 1):
            for two in (-1, 1):
                ends.update(self._generate_ends(board, start, one, two, 8))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)

class BlackBishop(Bishop):
    fen = 'b'

class WhiteBishop(Bishop):
    fen = 'B'

class Queen(Piece):
    def move_squares(self, board, start):
        ends = set()
        for one in (-1, 0, 1):
            for two in (-1, 0, 1):
                if one == two == 0:
                    continue
                ends.update(self._generate_ends(board, start, one, two, 8))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)

class BlackQueen(Queen):
    fen = 'q'

class WhiteQueen(Queen):
    fen = 'Q'

class Pawn(Piece):
    def move_squares(self, board, start):
        ends = set()

        starting_rank = False
        rank_delta = 0
        if self.fen == 'p':
            rank_delta = -1
            if start.rank_ == 7:
                starting_rank = True
        if self.fen == 'P':
            rank_delta = 1
            if start.rank_ == 2:
                starting_rank = True

        if starting_rank:
            limit = 2
        else:
            limit = 1

        ends.update(self._generate_ends(board, start, rank_delta, 0, limit,
            can_take=False))

        return ends

    def threat_squares(self, board, start):
        ends = set()

        rank_delta = 0
        if self.fen == 'p':
            rank_delta = -1
        if self.fen == 'P':
            rank_delta = 1

        for one in (-1, 1):
            ends.update(self._generate_ends(board, start, rank_delta, one, 1))

        return ends

class BlackPawn(Pawn):
    fen = 'p'

class WhitePawn(Pawn):
    fen = 'P'

class King(Piece):
    def move_squares(self, board, start):
        ends = set()
        for one in (-1, 0, 1):
            for two in (-1, 0, 1):
                if one == two == 0:
                    continue
                ends.update(self._generate_ends(board, start, one, two, 1))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)

class BlackKing(King):
    fen = 'k'

class WhiteKing(King):
    fen = 'K'

#TODO Check with Chris for a less grim copypasta way of doing this
PIECE_MAP = {}
def populate(piece):
    PIECE_MAP[piece.fen] = piece
populate(BlackKnight)
populate(WhiteKnight)
populate(BlackRook)
populate(WhiteRook)
populate(BlackBishop)
populate(WhiteBishop)
populate(BlackQueen)
populate(WhiteQueen)
populate(BlackPawn)
populate(WhitePawn)
populate(BlackKing)
populate(WhiteKing)
