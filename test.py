import unittest
from chess import Game, BoardSquare, InvalidSquareException, BasicMove, NoPieceAtSquareException

class TestChess(unittest.TestCase):

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    SIMPLE_ROOK_FEN = "k7/8/8/8/8/8/8/3R4 w - - 0 1"
    SIMPLE_BISHOP_FEN = "k7/8/8/8/8/8/8/3B4 w - - 0 1"

    def test_starting(self):
        game = Game()

        self.assertEqual(game.fen(), self.STARTING_FEN)

    def test_constructor(self):
        def test(fen):
            game = Game(fen)
            self.assertEqual(game.fen(), fen)

        test(self.STARTING_FEN)
        test(self.SIMPLE_ROOK_FEN)
        #TODO More fens

    def test_squares(self):
        BoardSquare('e5')
        BoardSquare('a1')
        BoardSquare('c3')
        BoardSquare('g2')

        def expect_fail(file_rank):
            try:
                BoardSquare(file_rank)
                self.fail("BoardSquare expected to have thrown InvalidSquareException for %s%d" % (file, rank))
            except InvalidSquareException:
                pass

        expect_fail('z1')
        expect_fail('a0')

    def test_square_fetch(self):
        game = Game()

        def f(file_rank):
            sq = BoardSquare(file_rank)
            return game.board.piece_at_board_square(sq)

        self.assertEqual(f('d4'), None)
        self.assertEqual(f('a1'), "R")
        self.assertEqual(f('f7'), "p")

    def test_valid_moves(self):
        game = Game()

        def f(game, file_rank, ends):
            start = BoardSquare(file_rank)
            moves = set([BasicMove(start, end) for end in ends])
            self.assertSetEqual(game.valid_moves(start), moves)

        f(game, 'a1', set())
        f(game, 'a2', {BoardSquare('a3'), BoardSquare('a4')})
        f(game, 'b2', {BoardSquare('b3'), BoardSquare('b4')})
        f(game, 'b1', {BoardSquare('a3'), BoardSquare('c3')})
        f(game, 'c1', set())
        f(Game(self.SIMPLE_BISHOP_FEN), 'd1', {BoardSquare('c2'),
                                               BoardSquare('b3'),
                                               BoardSquare('a4'),
                                               BoardSquare('e2'),
                                               BoardSquare('f3'),
                                               BoardSquare('g4'),
                                               BoardSquare('h5')})

    def test_moving_no_piece(self):
        game = Game()

        try:
            empty_square = BoardSquare('c5')
            game.valid_moves(empty_square)
            self.fail('valid_moves expected to have raised NoPieceAtSquareException for moves from %s' % start)
        except NoPieceAtSquareException:
            pass

    def test_square_adjustments(self):
        sq = BoardSquare('c3')

        self.assertEqual(sq.delta(1, 1), BoardSquare('d4'))
        self.assertIsNone(sq.delta(10, 10))
        self.assertIsNone(sq.delta(-10, -10))
        self.assertEqual(sq.delta(-1, -1), BoardSquare('b2'))

    def test_move(self):
        game = Game()

        new_game = game.move(BasicMove(BoardSquare('a2'), BoardSquare('a4')))

        self.assertEqual(new_game.fen(), "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq - 0 1")

if __name__ == '__main__':
    unittest.main()
