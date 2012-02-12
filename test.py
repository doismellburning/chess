import unittest
from chess import Chess, BoardSquare, InvalidSquareException, BasicMove, NoPieceAtSquareException

class TestChess(unittest.TestCase):

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    SIMPLE_ROOK_FEN = "k7/8/8/8/8/8/8/3R4 w - - 0 1"
    SIMPLE_BISHOP_FEN = "k7/8/8/8/8/8/8/3B4 w - - 0 1"

    def test_starting(self):
        chess = Chess()

        self.assertEqual(chess.fen(), self.STARTING_FEN)

    def test_constructor(self):
        def test(fen):
            chess = Chess(fen)
            self.assertEqual(chess.fen(), fen)

        test(self.STARTING_FEN)
        test(self.SIMPLE_ROOK_FEN)
        #TODO More fens

    def test_squares(self):
        BoardSquare('e', 5)
        BoardSquare('a', 1)
        BoardSquare('c', 3)
        BoardSquare('g', 2)

        def expect_fail(file, rank):
            try:
                BoardSquare(file, rank)
                self.fail("BoardSquare expected to have thrown InvalidSquareException for %s%d" % (file, rank))
            except InvalidSquareException:
                pass

        expect_fail('z', 1)
        expect_fail('a', -1)

    def test_square_fetch(self):
        chess = Chess()

        def f(file, rank):
            sq = BoardSquare(file, rank)
            return chess.board.piece_at_board_square(sq)

        self.assertEqual(f('d', 4), None)
        self.assertEqual(f('a', 1), "R")
        self.assertEqual(f('f', 7), "p")

    def test_valid_moves(self):
        chess = Chess()

        def f(chess, file, rank, ends):
            start = BoardSquare(file, rank)
            moves = set([BasicMove(start, end) for end in ends])
            self.assertSetEqual(chess.valid_moves(start), moves)

        f(chess, 'a', 1, set())
        f(chess, 'a', 2, {BoardSquare('a', 3), BoardSquare('a', 4)})
        f(chess, 'b', 2, {BoardSquare('b', 3), BoardSquare('b', 4)})
        f(chess, 'b', 1, {BoardSquare('a', 3), BoardSquare('c', 3)})
        f(chess, 'c', 1, set())
        f(Chess(self.SIMPLE_BISHOP_FEN), 'd', 1, {BoardSquare('c', 2),
                                                  BoardSquare('b', 3),
                                                  BoardSquare('a', 4),
                                                  BoardSquare('e', 2),
                                                  BoardSquare('f', 3),
                                                  BoardSquare('g', 4),
                                                  BoardSquare('h', 5)})

    def test_moving_no_piece(self):
        chess = Chess()

        try:
            empty_square = BoardSquare('c', 5)
            chess.valid_moves(empty_square)
            self.fail('valid_moves expected to have raised NoPieceAtSquareException for moves from %s' % start)
        except NoPieceAtSquareException:
            pass

    def test_square_adjustments(self):
        sq = BoardSquare('c', 3)

        self.assertEqual(sq.delta(1, 1), BoardSquare('d', 4))
        self.assertIsNone(sq.delta(10, 10))
        self.assertIsNone(sq.delta(-10, -10))
        self.assertEqual(sq.delta(-1, -1), BoardSquare('b', 2))

if __name__ == '__main__':
    unittest.main()
