# Create your views here
from django.http import HttpResponse
from django.utils import simplejson
from othello.models import Game


def connect(request):
    if request.method != 'GET':
        return ajax_response(error='GET method should be used instead of POST')
    if not 'p1' in request.GET or not 'p2' in request.GET:
        return ajax_response(
            error='Incorrect parameters. It should be: p1=juan&p2=pedro'
        )
    p1 = request.GET['p1']
    p2 = request.GET['p2']
    try:
        game_id = Game.objects.connect(p1, p2)
    except Exception, e:
        return ajax_response(error=e.message)

    return ajax_response(game=game_id)


def get_board(request):
    if request.method != 'GET':
        return ajax_response(error='GET method should be used instead of POST')
    if not 'game' in request.GET:
        return ajax_response(
            error='Incorrect parameters. It should be: game=juan-pedro-1'
        )
    try:
        g = Game.objects.get_by_id(request.GET['game'])
    except Exception, e:
        return ajax_response(error=e.message)

    return ajax_response(board=g.board)


def is_turn(request):
    if request.method != 'GET':
        return ajax_response(error='GET method should be used instead of POST')
    if not 'game' in request.GET or not 'player' in request.GET:
        return ajax_response(
            error='Incorrect parameters. It should be: ' \
                  'game=juan-pedro-1&player=pedro'
        )

    try:
        result = Game.objects.is_turn(request.GET['game'],
            request.GET['player'])
        return ajax_response(status=result)
    except Exception, e:
        return ajax_response(error=e.message)


def ajax_response(error=None, **kwargs):
    d = kwargs
    if error:
        d['error'] = error
    response = simplejson.dumps(d)
    return HttpResponse(response, mimetype='application/json')
