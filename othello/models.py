from django.db import models

INIT_BOARD = '0000000000000000000000000001200000021000000000000000000000000000'


class Player(models.Model):
    name = models.CharField(max_length=50)


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
    game_started = models.BooleanField()
    winner = models.ForeignKey(Player, blank=True, null=True,
        related_name='games_where_won')

    # Use the custom Mananger we created
    objects = GameManager()

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.game_started = False
        self.game_finished = False
        self.board = INIT_BOARD

    def is_ready_to_start(self):
        return not self.game_started and self.player1 and self.player2

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
