from othello.models import Player, Game

PLAYER1_NAME = 'john'
PLAYER2_NAME = 'peter'


def create_player(name=None):
    if name is None:
        name = PLAYER1_NAME
    return Player.objects.create(name=name)


def create_game(player1=None, player2=None, start_it=False):
    if player1 is None:
        player1 = create_player(name=PLAYER1_NAME)
    if player2 is None:
        player2 = create_player(name=PLAYER2_NAME)
    g = Game.objects.create(
        player1=player1.name,
        player2=player2.name,
    )
    if start_it:
        g.game_started = True
        g.save()
    return g
