import unittest
from libchess import Chess

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




if __name__ == '__main__':
    unittest.main()