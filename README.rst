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
	>>> game.valid_moves('a1')
	set([])
	>>> [str(move) for move in game.valid_moves('a2')]
	['(a2 -> a3)', '(a2 -> a4)']

Tracking game state::

	>>> from chess import Game, BasicMove
	>>> game = Game()
	>>> game.fen()
	'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
	>>> game = game.move(BasicMove('a2', 'a4'))
	>>> game.fen()
	'rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1'


https://github.com/doismellburning/chess
