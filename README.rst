Chess
=====

Primitive Python chess engine.

Currently very much in development.

Examples
========

Basic usage::

	>>> from chess import Game
	>>> Game().fen()
	'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

Determining valid moves::

	>>> from chess import Game
	>>> game = Game()
	>>> game.valid_ends('a1')
	set([])
	>>> [str(square) for square in game.valid_ends('a2')]
	['a3', 'a4']

Tracking game state::

	>>> from chess import Game, BasicMove
	>>> game = Game()
	>>> game.fen()
	'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
	>>> game = game.move(BasicMove('a2', 'a4'))
	>>> game.fen()
	'rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1'

Checkmate::

	>>> from chess import Game, BasicMove
	>>> game = Game()
	>>> game.is_checkmate()
	False
	>>> # Fool's mate...
	>>> game = game.move(BasicMove('f2', 'f3'))
	>>> game = game.move(BasicMove('e7', 'e5'))
	>>> game = game.move(BasicMove('g2', 'g4'))
	>>> game = game.move(BasicMove('d8', 'h4'))
	>>> game.is_checkmate()
	True

https://github.com/doismellburning/chess
