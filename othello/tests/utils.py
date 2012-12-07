from othello.models import Player

PLAYER_NAME = 'john'

def create_player(name=None):
    if name is None:
        name = PLAYER_NAME
    return Player.objects.create(name=name)
