# -*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django.utils import simplejson
from othello.tests import utils
from othello.models import INIT_BOARD


class ConnectTests(TestCase):
    def test_POST_returns_error(self):
        r = self.client.post(path='/connect')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'GET method should be used instead of '
                                     'POST')
        self.assertFalse('game' in d)

    def test_no_player1_provided(self):
        r = self.client.get(path='/connect?p2=john')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Incorrect parameters. It should be: '
                                     'p1=juan&p2=pedro')
        self.assertFalse('game' in d)

    def test_no_player2_provided(self):
        r = self.client.get(path='/connect?p1=john')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Incorrect parameters. It should be: '
                                     'p1=juan&p2=pedro')
        self.assertFalse('game' in d)

    def test_no_players_provided(self):
        r = self.client.get(path='/connect')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Incorrect parameters. It should be: '
                                     'p1=juan&p2=pedro')
        self.assertFalse('game' in d)

    def test_game_is_returned_ok(self):
        utils.create_game()
        r = self.client.get(path='/connect?p1=john&p2=peter')
        d = simplejson.loads(r.content)

        self.assertFalse('error' in d)
        self.assertEqual(d['game'], 'john-peter-1')


class GetBoardTests(TestCase):
    def test_POST_returns_error(self):
        r = self.client.post(path='/get_board')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'GET method should be used instead of '
                                     'POST')
        self.assertFalse('board' in d)

    def test_no_game_provided(self):
        r = self.client.get(path='/get_board')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'],
                         'Incorrect parameters. It should be: '
                         'game=juan-pedro-1')
        self.assertFalse('board' in d)

    def test_no_existing_game(self):
        r = self.client.get(path='/get_board?game=a-b-1')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Game a-b-1 not found')
        self.assertFalse('board' in d)

    def test_game_ok(self):
        utils.create_game()
        r = self.client.get(path='/get_board?game=john-peter-1')
        d = simplejson.loads(r.content)

        self.assertFalse('error' in d)
        self.assertTrue(d['board'], INIT_BOARD)


class IsTurnTests(TestCase):
    def test_POST_returns_error(self):
        r = self.client.post(path='/is_turn')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'GET method should be used instead of '
                                     'POST')
        self.assertFalse('status' in d)

    def test_game_not_started_yet(self):
        utils.create_game()
        r = self.client.get(path='/is_turn?game=john-peter-1&player=john')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'The game hasn\'t started yet. Make sure'
                                     ' both players have been connected')
        self.assertFalse('status' in d)

    def test_non_existing_game(self):
        utils.create_game()
        r = self.client.get(path='/is_turn?game=john-peter-2&player=john')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Game john-peter-2 not found')
        self.assertFalse('status' in d)

    def test_non_existing_player(self):
        utils.create_game(start_it=True)
        r = self.client.get(path='/is_turn?game=john-peter-1&player=oscar')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'The player oscar is not playing in this'
                                     ' game')
        self.assertFalse('status' in d)

    def test_false(self):
        utils.create_game(start_it=True)
        r = self.client.get(path='/is_turn?game=john-peter-1&player=john')
        d = simplejson.loads(r.content)

        self.assertFalse(d['status'])
        self.assertFalse('error' in d)

    def test_true(self):
        utils.create_game(start_it=True)
        r = self.client.get(path='/is_turn?game=john-peter-1&player=peter')
        d = simplejson.loads(r.content)

        self.assertTrue(d['status'])
        self.assertFalse('error' in d)


class MoveTests(TestCase):
    def test_GET_returns_error(self):
        r = self.client.get(path='/move')
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'POST method should be used instead of '
                                     'GET')
        self.assertEqual(d['status'], 'failed')

    def test_non_existing_player(self):
        utils.create_game()
        data = {'game': 'john-peter-1',
                'player': 'oscar',
                'move': '(3,2)'}
        r = self.client.post(path='/move', data=data)
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'The player oscar is not playing in this'
                                     ' game')
        self.assertEqual(d['status'], 'failed')

    def test_non_existing_game(self):
        utils.create_game()
        data = {'game': 'john-peter-3',
                'player': 'peter',
                'move': '(3,2)'}
        r = self.client.post(path='/move', data=data)
        d = simplejson.loads(r.content)

        self.assertEqual(d['error'], 'Game john-peter-3 not found')
        self.assertEqual(d['status'], 'failed')

    def test_ok(self):
        utils.create_game(start_it=True)
        data = {'game': 'john-peter-1',
                'player': 'peter',
                'move': '(3,2)'}
        r = self.client.post(path='/move', data=data)
        d = simplejson.loads(r.content)

        self.assertFalse('error' in d)
        self.assertEqual(d['status'], 'succeed')
