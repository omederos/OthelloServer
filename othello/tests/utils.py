from othello.models import Player, Game

PLAYER_NAME = 'john'

def create_player(name=None):
    if name is None:
        name = PLAYER_NAME
    return Player.objects.create(name=name)


def create_game(player1=None, player2=None):
    if player1 is None:
        player1 = create_player(name='john')
    if player2 is None:
        player2 = create_player(name='peter')
    return Game.objects.create(
        player1=player1.name,
        player2=player2.name
    )
