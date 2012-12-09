from django.db import models
from datetime import datetime

INIT_BOARD = '0000000000000000000000000001200000021000000000000000000000000000'


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
            self.game_finished = False
            self.player1_turn = False # Black ones start playing
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

        if player == self.player1.name:
            result = self.player1_turn
        elif player == self.player2.name:
            result = not self.player1_turn
        else:
            # If the name provided doesn't match with the name of the players
            # of this game
            raise Exception('The player %s is not playing in this game' %
                            player)

        # If this is the first time the player calls 'is_turn'
        # and the caller is the one that plays now
        if result and not self.is_turn_already_called:
            # We save
            self.is_turn_already_called = True
            self.timeout_is_turn = datetime.now()
            self.save()

        return result

    def start_game(self):
        """
        Initialize the game.

        This method should be called when both players have been connected
        to the game correctly.
        """
        self.game_started = True
        self.save()

    def has_finished(self):
        return self.winner is not None

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
            matrix[-1].append(x)
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
