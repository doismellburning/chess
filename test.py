import unittest
from chess import Game, BoardSquare, InvalidSquareException, BasicMove, NoPieceAtSquareException, MoveMissingPromotionException

class TestChess(unittest.TestCase):

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    PAWNLESS_FEN = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w KQkq - 0 1"
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

        def f(game, start, ends):
            moves = set([BasicMove(start, end) for end in ends])
            self.assertSetEqual(game.valid_moves(start), moves)

        f(game, 'a1', set())
        f(game, 'a2', {'a3', 'a4'})
        f(game, 'b2', {'b3', 'b4'})
        f(game, 'b1', {'a3', 'c3'})
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
            empty_square = 'c5'
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

        new_game = game.move(BasicMove('a2', 'a4'))

        self.assertEqual(new_game.fen(), "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1")

    def test_pawn_starting_move(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/Pr6/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        game = Game(fen)
        moves = game.valid_moves('b2')

        self.assertEqual(moves, set())

    def test_pawn_taking(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/Pr6/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        game = Game(fen)

        def f(start, ends):
            moves = game.valid_moves(start)
            self.assertEqual(moves,
                set([BasicMove(start, end) for end in ends]))

        f('a2', ['b3'])
        f('c2', ['b3', 'c3', 'c4'])

    def test_move_counters(self):
        game = Game(self.STARTING_FEN)

        self.assertEqual(game.halfmove, 0)
        self.assertEqual(game.fullmove, 1)
        game = game.move(BasicMove('e2', 'e4'))
        self.assertEqual(game.halfmove, 0)
        self.assertEqual(game.fullmove, 1)
        game = game.move(BasicMove('c7', 'c5'))
        self.assertEqual(game.halfmove, 0)
        self.assertEqual(game.fullmove, 2)
        game = game.move(BasicMove('g1', 'f3'))
        self.assertEqual(game.halfmove, 1)
        self.assertEqual(game.fullmove, 2)
        game = game.move(BasicMove('a7', 'a5'))
        self.assertEqual(game.halfmove, 0)
        self.assertEqual(game.fullmove, 3)
        #TODO Full check of FEN?

    def test_en_passant_updating(self):
        game = Game(self.STARTING_FEN)

        self.assertEqual(game.en_passant, None)
        game = game.move(BasicMove('e2', 'e4'))
        self.assertEqual(game.en_passant, BoardSquare('e3'))
        game = game.move(BasicMove('c7', 'c5'))
        self.assertEqual(game.en_passant, BoardSquare('c6'))
        game = game.move(BasicMove('g1', 'f3'))
        self.assertEqual(game.en_passant, None)
        game = game.move(BasicMove('a7', 'a5'))
        self.assertEqual(game.en_passant, BoardSquare('a6'))

    def test_en_passant_taking(self):
        game = Game('rnbqkbnr/pppppppp/8/8/p7/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

        game = game.move(BasicMove('b2', 'b4'))
        self.assertEqual(game.en_passant, BoardSquare('b3'))
        game = game.move(BasicMove('a4', 'b3'))
        self.assertEqual(game.en_passant, None)
        self.assertEqual(game.board.piece_at_board_square(BoardSquare('b4')), None)

    def test_castling(self):
        game = Game(self.PAWNLESS_FEN)

        self.assertEqual(game.castling.fen(), 'KQkq')
        game = game.move(BasicMove('a1', 'a2'))
        self.assertEqual(game.castling.fen(), 'Kkq')
        game = game.move(BasicMove('e8', 'e7'))
        self.assertEqual(game.castling.fen(), 'K')
        game = game.move(BasicMove('e1', 'e2'))
        self.assertEqual(game.castling.fen(), '-')

    def test_promotion(self):
        game = Game('4k3/P7/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

        try:
            game = game.move(BasicMove('a7', 'a8'))
            self.assertFail('Should not accept promotion move without promotion data')
        except MoveMissingPromotionException:
            pass

        game = game.move(BasicMove('a7', 'a8', 'Q'))
        self.assertEqual(game.fen(), 'Q3k3/8/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1')

if __name__ == '__main__':
    unittest.main()
