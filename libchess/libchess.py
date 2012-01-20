import copy

class InvalidSquareException(Exception):
    pass

#TODO Replace this with something better...
#TODO Piece and colour objects?
def colour_of_piece(piece):
    if piece >= "A" and piece <= "Z":
        return "w"
    if piece >= "a" and piece <= "z":
        return "b"

class BoardSquare(object):
    def __init__(self, file, rank): #TODO Consider changing this to just take "e5"?
        if rank < 1 or rank > 8:
            raise InvalidSquareException('"%d" is not a valid rank' % rank)
        if file < "a" or file > "h":
            raise InvalidSquareException('"%s" is not a valid file' % file)
        self.rank = rank
        self.file = file

    def to_board_coordinates(self):
        fst = 8 - self.rank
        snd = ord(self.file) - ord('a')
        return (fst, snd)

    def __str__(self):
        return "%s%d" % (self.file, self.rank)

    def delta(self, file_delta, rank_delta):
        try:
            new_square = BoardSquare(chr(ord(self.file) + file_delta), self.rank + rank_delta)
            return new_square
        except InvalidSquareException:
            #Boom, tried to move beyond limits
            return None

    def __eq__(self, other):
        return self.rank == other.rank and self.file == other.file


class CastlingState(object):
    def __init__(self):
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True

    def __str__(self):
        str = ""

        if self.white_kingside:
            str += "K"

        if self.white_queenside:
            str += "Q"

        if self.black_kingside:
            str += "k"

        if self.black_queenside:
            str += "q"

        if not len(str):
            str = "-"

        return str

class BasicMove(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return "(%s -> %s)" % (self.start, self.end)

class Board(object):
    def __init__(self, squares=None):
        if squares is None:
            self.squares = [[None for i in xrange(8)] for j in xrange(8)]
            self.squares[0] = list('rnbqkbnr')
            self.squares[1] = ['p' for i in xrange(8)]
            self.squares[6] = ['P' for i in xrange(8)]
            self.squares[7] = list('RNBQKBNR')
        else:
            assert(len(squares) == 8)
            for rank_or_file_I_forget in squares:
                assert(len(rank_or_file_I_forget) == 8)
            self.squares = squares

    def __str__(self):
        rows = list()
        for row in self.squares:
            row_str = ''
            empty_count = 0
            for square in row:
                if square == None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += "%d" % empty_count
                        empty_count = 0
                    row_str += square
            if empty_count > 0:
                row_str += "%d" % empty_count
            rows.append(row_str)

        return "/".join(rows)

    def piece_at_board_square(self, board_square):
        coords = board_square.to_board_coordinates()
        return self.squares[coords[0]][coords[1]]

    def check_status(self):
        #Return b or w or None
        raise NotImplementedError()

    def board_from_move(self, move):
        new_board_squares = copy.deepcopy(self.squares)

        #TODO Move this into a board.move()?
        start_coords = move.start.to_board_coordinates()
        end_coords = move.end.to_board_coordinates()
        new_board_squares[end_coords[0]][end_coords[1]] = new_board_squares[start_coords[0]][start_coords[1]]
        new_board_squares[start_coords[0]][start_coords[1]] = None

        return Board(new_board_squares)


class Chess(object):
	
    def __init__(self, fen=None):
        self.board = Board()
        self.active = "w" #TODO Better
        self.castling = CastlingState()
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1

        if fen:
            raise NotImplementedError()

    def fen(self):
        en_passant_str = self.en_passant or "-"
        return '%s %s %s %s %d %d' % (self.board, self.active, self.castling, en_passant_str, self.halfmove, self.fullmove)

    def is_move_valid(self, move):
        return self.valid_moves(move.start()).contains(move)

    def valid_moves(self, start):
        piece = self.board.piece_at_board_square(start)

        assert(piece != None)

        color = colour_of_piece(piece)

        assert(self.active == color)

        # Generate moves
        moves = list()
        if piece == 'r' or piece == 'R':
            #TODO Figure out what loop I want for this?
            moves.extend(self.generate_moves(color, start, 0, +1, 8))
            moves.extend(self.generate_moves(color, start, 0, -1, 8))
            moves.extend(self.generate_moves(color, start, +1, 0, 8))
            moves.extend(self.generate_moves(color, start, -1, 0, 8))
        elif piece == 'p' or piece == 'P':
            starting_rank = False
            rank_delta = 0
            if piece == 'p':
                rank_delta = -1
                if start.rank == 7:
                    starting_rank = True
            if piece == 'P':
                rank_delta = 1
                if start.rank == 2:
                    starting_rank = True
            moves.extend(self.generate_moves(color, start, rank_delta, 0, 1, False))

            if starting_rank:
                moves.extend(self.generate_moves(color, start, 2 * rank_delta, 0, 1, False))

            #TODO Capturing moves...
        else:
            raise NotImplementedError()

        # Generate potential boards
        move_boards = zip(moves, map(self.board.board_from_move, moves))

        # Determine check, prune
        valid_moves = [move_board[0] for move_board in move_boards if move_board[1].check_status() != self.active]

        return valid_moves

    def generate_moves(self, color, start, rank_delta, file_delta, limit, can_take=True):
        moves = []
        position = start
        for i in xrange(limit):
            position = position.delta(rank_delta, file_delta)
            if position is None:
                break

            end_piece = self.board.piece_at_board_square(position)

            if end_piece is None:
                moves.append(position)
            else:
                if can_take and colour_of_piece(end_piece) != color:
                    moves.append(position)
                break

        return moves

    def move(self, move):
        assert(self.is_move_valid(move))

        raise NotImplementedError()

    def display_move(self, move):
        assert(self.is_move_valid(move))

        raise NotImplementedError()

    def __str__(self):
        return self.fen()