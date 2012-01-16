import unittest
from libchess import Chess, BoardSquare

class TestChess(unittest.TestCase):

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def test_starting(self):
        chess = Chess()

        self.assertEqual(chess.fen(), self.STARTING_FEN)

    def test_constructor(self):
        def test(fen):
            chess = Chess(fen)
            self.assertEqual(chess.fen(), fen)

        test(self.STARTING_FEN)
        #TODO More fens

    def test_squares(self):
        BoardSquare('e', 5)
        BoardSquare('a', 1)
        BoardSquare('c', 3)
        BoardSquare('g', 2)

        def expect_fail(file, rank):
            try:
                BoardSquare(file, rank)
                pass
            except AssertionError:
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

if __name__ == '__main__':
    unittest.main()