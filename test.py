import unittest
from chess import Game, BoardSquare, InvalidSquareException, BasicMove, NoPieceAtSquareException, MoveMissingPromotionException, InvalidPromotionDataException

class TestChess(unittest.TestCase):

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    PAWNLESS_FEN = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w KQkq - 0 1"
    SIMPLE_ROOK_FEN = "k7/8/8/8/8/8/8/3R4 w - - 0 1"
    SIMPLE_BISHOP_FEN = "k7/8/8/8/8/8/8/3B4 w - - 0 1"
    CHECK_FEN = 'rnbqkbnr/8/8/1B6/8/8/8/RNBQK1NR b KQkq - 1 1'

    def _squarify(self, square_strs):
        return set([BoardSquare(square_str) for square_str in square_strs])

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

    def test_valid_ends(self):
        game = Game()

        self.assertSetEqual(game.valid_ends('a1'), set())
        self.assertSetEqual(game.valid_ends('a2'), self._squarify({'a3', 'a4'}))
        self.assertSetEqual(game.valid_ends('b2'), self._squarify({'b3', 'b4'}))
        self.assertSetEqual(game.valid_ends('b1'), self._squarify({'a3', 'c3'}))
        self.assertSetEqual(game.valid_ends('c1'), set())
        self.assertSetEqual(Game(self.SIMPLE_BISHOP_FEN).valid_ends('d1'),
                {BoardSquare('c2'),
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
            game.valid_ends(empty_square)
            self.fail('valid_ends expected to have raised NoPieceAtSquareException for moves from %s' % start)
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
        self.assertEqual(game.valid_ends('b2'), set())

    def test_pawn_taking(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/Pr6/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        game = Game(fen)

        self.assertSetEqual(game.valid_ends('a2'), self._squarify(['b3']))
        self.assertSetEqual(game.valid_ends('c2'), self._squarify(['b3', 'c3', 'c4']))

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

    def test_castling_state(self):
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
            self.fail('Should not accept promotion move without promotion data')
        except MoveMissingPromotionException:
            pass

        try:
            game.move(BasicMove('a7', 'a8', 'LLAMA'))
            self.fail('Should not accept non-promotion move with promotion data')
        except InvalidPromotionDataException:
            pass

        game = game.move(BasicMove('a7', 'a8', 'Q'))
        self.assertEqual(game.fen(), 'Q3k3/8/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1')

        try:
            game.move(BasicMove('e8', 'e7', 'Q'))
            self.fail('Should not accept non-promotion move with promotion data')
        except InvalidPromotionDataException:
            pass

    def test_castling(self):
        game = Game('r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1')

        self.assertSetEqual(game.valid_ends('e1'), self._squarify({'c1', 'd1', 'f1', 'g1'}))

        new_game = game.move(BasicMove('e1', 'c1'))
        self.assertEqual(new_game.fen(), 'r3k2r/pppppppp/8/8/8/8/PPPPPPPP/2KR3R b kq - 1 1')

        new_game = game.move(BasicMove('e1', 'g1'))
        self.assertEqual(new_game.fen(), 'r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R4RK1 b kq - 1 1')

    def test_castling_out_of_check(self):
        game = Game('4rk2/8/8/8/8/8/8/R3K2R w KQ - 0 1')

        self.assertSetEqual(game.board.check_status(), set("w"))
        self.assertNotIn(BoardSquare('c1'), game.valid_ends('e1'), 'Attempting to castle out of check')
        self.assertNotIn(BoardSquare('g1'), game.valid_ends('e1'), 'Attempting to castle out of check')
        self.assertSetEqual(game.valid_ends('e1'), self._squarify(['d2', 'f2', 'd1', 'f1']))

    def test_castling_through_check(self):
        game = Game('3rkr2/8/8/8/8/8/8/R3K2R w KQ - 0 1')

        self.assertSetEqual(game.board.check_status(), set())
        self.assertSetEqual(game.valid_ends('e1'), self._squarify(['e2']))

    def test_not_moving_into_check(self):
        game = Game('1k6/8/8/8/8/8/8/R1RK4 b - - 1 1')

        self.assertSetEqual(game.board.check_status(), set())

        self.assertSetEqual(game.valid_ends('b8'), self._squarify(['b7']))

    def test_must_leave_check(self):
        game = Game('r6r/k7/8/8/8/8/8/R3K2R b KQ - 1 1')

        self.assertSetEqual(game.board.check_status(), set(['b']))

        #Can't move out of check with either rook
        self.assertSetEqual(game.valid_ends('a8'), set())
        self.assertSetEqual(game.valid_ends('a8'), set())
        #Only 3 of 5 king moves possible
        self.assertSetEqual(game.valid_ends('a7'), self._squarify({'b8', 'b7', 'b6'}))


    def test_basic_check(self):
        #Game in check
        game = Game('rnbqkbnr/8/8/1B6/8/8/8/RNBQK1NR b KQkq - 1 1')

        self.assertSetEqual(game.board.check_status(), set(['b']))
        #Can't use Rook to get out of check
        self.assertSetEqual(game.valid_ends('a8'), set())
        #Only one place to move the Queen - in the way
        self.assertSetEqual(game.valid_ends('d8'), self._squarify(['d7']))

        #Make that move to be out of check
        game = game.move(BasicMove('d8', 'd7'))
        #Dummy move by white to get the turn back to black
        game = game.move(BasicMove('a1', 'a2'))
        #Now we can only move that Queen to things still in the way...
        self.assertSetEqual(game.valid_ends('d7'), self._squarify(['b5', 'c6']))


if __name__ == '__main__':
    unittest.main()
