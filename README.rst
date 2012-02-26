Chess
=====

Primitive Python chess engine.

Currently very much in development.

Examples
========

Basic usage::

	>>> from chess import Game
	>>> print Game().fen()
	rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Determining valid moves::

	>>> from chess import Game
	>>> game = Game()
	>>> game.valid_moves('a1')
	set([])
	>>> [str(move) for move in game.valid_moves('a2')]
	['(a2 -> a3)', '(a2 -> a4)']

https://github.com/doismellburning/chess
