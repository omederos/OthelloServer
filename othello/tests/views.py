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

        self.assertEqual(d['error'], 'Incorrect parameters. It should be: '
                                     'game=juan-pedro-1'
        )
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
