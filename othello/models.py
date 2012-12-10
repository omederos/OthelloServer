from django.db import models
from datetime import datetime

INIT_BOARD = '0000000000000000000000000001200000021000000000000000000000000000'
TIMEOUT_IS_TURN = 15
TIMEOUT_TURN = 60
MAX_INVALID_MOVES = 3

BLANK = 0
WHITE = 1
BLACK = 2

COLORS_RELATIONSHIP = {WHITE: BLACK,
                       BLACK: WHITE,
                       BLANK: BLANK}


class Player(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class GameManager(models.Manager):
    def create(self, player1=None, player2=None, **kwargs):
        """
        Crea una juego. Si no existen los jugadores, tambien los crea

        """
        params = kwargs

        if player1 is not None:
            p1 = Player.objects.get_or_create(name=player1)[0]
            params.update({'player1': p1})
        if player2 is not None:
            p2 = Player.objects.get_or_create(name=player2)[0]
            params.update({'player2': p2})

        return super(GameManager, self).create(**params)

    def get_by_id(self, game_id):
        """
        Returns the game that has the specified ID

        Example of a game ID: john-peter-3
        """
        splitted = game_id.strip().split('-')
        if len(splitted) != 3:
            raise Exception('Invalid game identifier \'%s\'' % game_id)
        p1 = splitted[0]
        p2 = splitted[1]
        game = splitted[2]

        try:
            return self.get(player1__name=p1, player2__name=p2, id=game)
        except:
            raise Exception('Game %s not found' % game_id)

    def is_turn(self, game_id, player):
        g = self.get_by_id(game_id)
        return g.is_turn(player)

    def connect(self, p1, p2):
        """
        Connects the specified players to a game

        If the game already exists, it starts the game
        If the game does not exist, it creates a new one
        """
        try:
        # Getting a game that hasn't been started with the specified players
            g = Game.objects.get(player1__name=p1,
                player2__name=p2,
                game_started=False
            )

            # If the game already existed, then the other player is just
            # connecting to it
            g.start_game()
        except Game.DoesNotExist:
            # If the game does not exist, we create a new one
            g = Game.objects.create(player1=p1, player2=p2)

        return unicode(g)


class Game(models.Model):
    """
    An Othello game.

    Player1 play with WHITE discs and Player 2 with BLACK ones
    """
    player1 = models.ForeignKey(Player, verbose_name='Player 1', blank=True,
        null=True, related_name='games_being_first_player')
    player2 = models.ForeignKey(Player, verbose_name='Player 2', blank=True,
        null=True, related_name='games_being_second_player')
    player1_turn = models.BooleanField(verbose_name='Player 1\'s Turn')
    board = models.CharField(max_length=64)
    # Indica si el juego ya comenzo o no
    game_started = models.BooleanField()
    # Momento en el que se llamo a 'is_turn' por el jugador que le tocaba jugar
    timeout_is_turn = models.DateTimeField(null=True)
    # Momento en que le toco jugar al proximo jugador
    timeout_turn_change = models.DateTimeField(null=True)
    # Guarda la cantidad de movimientos invalidos realizados por cada jugador
    invalid_moves_player1 = models.IntegerField(default=0)
    invalid_moves_player2 = models.IntegerField(default=0)
    # Cantidad de fichas al finalizar el juego.
    # Indica la puntuacion final del juego (ej. 63-1, 32-32, etc.)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)

    # Indica si el jugador que le toca jugar ya llamo a 'is_turn'
    is_turn_already_called = models.BooleanField()

    winner = models.ForeignKey(Player, blank=True, null=True,
        related_name='games_where_won')

    # Use the custom Mananger we created
    objects = GameManager()

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        # If we are creating the model (instead of editing it)
        # TODO: Use post-save signal and check the 'created' flag
        if not self.pk:
            self.game_started = False
            self.player1_turn = False  # Black ones start playing
            self.board = INIT_BOARD

    def is_turn(self, player):
        """
        Returns True if it is caller's turn

        """
        # Check if the game already started. It could happen that not both
        # players have been connected
        if not self.game_started:
            raise Exception('The game hasn\'t started yet. Make sure both '
                            'players have been connected')

        result = self._is_turn(player)

        # If this is the first time the player calls 'is_turn'
        # and the caller is the one that plays now
        if result and not self.is_turn_already_called:
            # We save
            self.is_turn_already_called = True
            self.timeout_is_turn = datetime.now()
            self.save()

        return result

    def _is_turn(self, player):
        if player == self.player1.name:
            result = self.player1_turn
        elif player == self.player2.name:
            result = not self.player1_turn
        else:
            # If the name provided doesn't match with the name of the players
            # of this game
            raise Exception('The player %s is not playing in this game' %
                            player)
        return result

    def start_game(self):
        """
        Initialize the game.

        This method should be called when both players have been connected
        to the game correctly.
        """
        self.game_started = True
        self.timeout_turn_change = datetime.now()
        self.timeout_is_turn = self.timeout_turn_change
        self.save()

    def game_finished(self):
        return self.winner is not None

    def move(self, player, move):
        current_time = datetime.now()

        if player != self.player1.name and player != self.player2.name:
            raise Exception('The player %s is not playing in this game' %
                            player)

        # p = self.player1 if player == self.player1.name else self.player2
        if not self._is_turn(player):
            raise Exception('You must wait for your turn')

        try:
            point = eval(move)
        except:
            raise Exception('Invalid move format: %s' % move)

        # If the game already finished...
        if self.game_finished():
            raise Exception('This game already finished')

        # If the game hasn't been started yet
        if not self.game_started:
            raise Exception('The game hasn\'t started yet. Make sure'
                            ' both players have been connected')

        matrix = self._get_matrix()
        self.is_turn_already_called = False
        self.save()

        # If the player called 'is_turn' more than 15 secs ago
        if self.is_turn_already_called:
            timeout = (current_time - self.timeout_is_turn).seconds
            if timeout >= TIMEOUT_IS_TURN:
                # Turn over!
                self._change_turn(matrix, player)
                raise Exception('%s seconds ellapsed since you called '
                                '\'is_turn\'' % timeout)

        # If the player didn't called is turn but waited more than 60 secs
        timeout = (current_time - self.timeout_turn_change).seconds
        if timeout >= TIMEOUT_TURN:
            # Turn over!
            self._change_turn(matrix, player)
            raise Exception('%s seconds ellapsed since the other player '
                            'played, and you didn\'t call \'is_turn\'')

        # The player can play!
        self._move_piece(matrix, player, point)
        self._change_turn(matrix, player)

    def get_piece_color(self, player):
        return WHITE if player == self.player1.name else BLACK

    def _get_inverse_piece(self, color):
        return COLORS_RELATIONSHIP[color]

    dx = [-1, -1, -1, 0, 1, 1, 1, 0]
    dy = [-1, 0, 1, 1, 1, 0, -1, -1]

    def _has_any_move_options(self, color, matrix=None):
        try:
            self.get_possible_moves(color, matrix).next()
            return True
        except StopIteration:
            return False

    def get_possible_moves(self, color, matrix=None):
        if not matrix:
            matrix = self._get_matrix()
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell != BLANK:
                    continue
                c = (i, j)
                if self._is_cell_available(matrix, c, color):
                    yield c

    def _get_directions(self, matrix, move, color):
        """
        Enumerates all the directions where some pieces have to be flipped
        """
        x = move[0]
        y = move[1]

        other_color = self._get_inverse_piece(color)

        # Looking in 8 different directions
        for d in xrange(8):
            k = 0
            ok = True
            count = 0
            while 1:
                k += 1
                x_new = x + self.dx[d] * k
                y_new = y + self.dy[d] * k

                # If we reached the borders of the board
                if self._is_out_of_board((x_new, y_new)) or \
                   matrix[x_new][y_new] == BLANK:
                    ok = False
                    break
                # If we found the other piece we are looking for
                if matrix[x_new][y_new] == color:
                    ok = count > 0
                    break
                if matrix[x_new][y_new] == other_color:
                    count += 1

            if ok:
                yield d

    def _is_cell_available(self, matrix, cell, color):
        try:
            self._get_directions(matrix, cell, color).next()
            return True
        except StopIteration:
            return False

    def _is_out_of_board(self, cell):
        return cell[0] < 0 or cell[0] >= 8 or cell[1] < 0 or cell[1] >= 8

    def _change_turn(self, matrix, old_player):
        # Update the time
        self.timeout_turn_change = datetime.now()
        self.save()

        # Get the piece color of the player that made the last move
        color = self.get_piece_color(old_player)

        # If the next player cannot play, we don't do anything
        other_color = self._get_inverse_piece(color)
        if not self._has_any_move_options(other_color, matrix):
            return

        # If the next player can play, then we change the turn.
        self.player1_turn = not self.player1_turn
        self.save()

    def _set_invalid_move(self, player):
        if player == self.player1.name:
            self.invalid_moves_player1 += 1
        if player == self.player2.name:
            self.invalid_moves_player2 += 1

        self.save()

        # If the maximum number of invalid moves was reached
        if self.invalid_moves_player1 >= MAX_INVALID_MOVES or self\
        .invalid_moves_player2 >= MAX_INVALID_MOVES:
            self.score_player1 = 63 if self.invalid_moves_player1 < \
                                 MAX_INVALID_MOVES else 1
            self.score_player2 = 63 if self.invalid_moves_player2 < \
                                 MAX_INVALID_MOVES else 1
            self.winner = self.player1 if self.invalid_moves_player1 < \
                          MAX_INVALID_MOVES else self.player2
            self.save()

        self.save()

    def update_board(self, matrix, player, move):
        color = self.get_piece_color(player)
        directions = list(self._get_directions(matrix, move, color))
        other_color = self._get_inverse_piece(color)

        # Update the cell where the user played
        matrix[move[0]][move[1]] = color

        for d in directions:
            k = 0
            while 1:
                k += 1
                x_new = move[0] + self.dx[d] * k
                y_new = move[1] + self.dy[d] * k
                if matrix[x_new][y_new] == other_color:
                    matrix[x_new][y_new] = color
                else:
                    break

        # Update the board on db
        self._update_board_from_matrix(matrix)

    def _update_board_from_matrix(self, matrix):
        board = []
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                board.append(str(cell))
        self.board = "".join(board)
        self.save()

    def _move_piece(self, matrix, player, point):
        # If the move is invalid
        color = self.get_piece_color(player)
        if not self._is_cell_available(matrix, point, color):
            self._set_invalid_move(player)
            # The player loses his turn
            self._change_turn(matrix, player)
            raise Exception('Invalid move')

        self.update_board(matrix, player, point)

        self._check_if_game_finished(matrix)

    def _check_if_game_finished(self, matrix):
        white = 0
        black = 0
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell == WHITE:
                    white += 1
                if cell == BLACK:
                    black += 1

        # If the game finished
        if white == 0 or black == 0 or white + black == 64:
            # Store the score
            self.score_player1 = white
            self.score_player2 = black
            # Store the winner
            self.winner = self.player1 if white > black else self.player2
            self.save()

    def __unicode__(self):
        return '{0}-{1}-{2}'.format(
            unicode(self.player1),
            unicode(self.player2),
            self.id
        )

    def _get_matrix(self):
        N = 8
        matrix = []
        for i, x in enumerate(self.board):
            if i % N == 0:
                matrix.append([])
            matrix[-1].append(int(x))
        return matrix


class Pair(models.Model):
    player1 = models.ForeignKey(Player,
        related_name='pairs_being_first_player')
    player2 = models.ForeignKey(Player,
        related_name='pairs_being_second_player')
    game1 = models.ForeignKey(Player, related_name='pairs1', blank=True,
        null=True)
    game2 = models.ForeignKey(Player, related_name='pairs2', blank=True,
        null=True)
