from django.db import models

INIT_BOARD = '0000000000000000000000000001200000021000000000000000000000000000'


class Player(models.Model):
    name = models.CharField(max_length=50)


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
    game_ready_to_start = models.BooleanField()
    winner = models.ForeignKey(Player, blank=True, null=True,
        related_name='games_where_won')

    board_matrix = None

    def __init__(self):
        super(Game, self).__init__(self)
        self.board = INIT_BOARD
        self.save()


class Pair(models.Model):
    player1 = models.ForeignKey(Player,
        related_name='pairs_being_first_player')
    player2 = models.ForeignKey(Player,
        related_name='pairs_being_second_player')
    game1 = models.ForeignKey(Player, related_name='pairs1', blank=True,
        null=True)
    game2 = models.ForeignKey(Player, related_name='pairs2', blank=True,
        null=True)
