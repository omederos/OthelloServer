from django.test.testcases import TestCase
from othello.models import *
from othello.tests.utils import create_player, create_game

class GameTests(TestCase):
    def test_unicode(self):
        g = Game.objects.create(player1='john1', player2='john2')
        self.assertEqual(unicode(g), 'john1-john2-1')

class GameManagerTests(TestCase):
    def test_create_non_existing_players(self):
        g = Game.objects.create(player1='john1', player2='john2')

        # The game has to be created
        self.assertEqual(Game.objects.count(), 1)

        # The players have to be created
        self.assertEqual(Player.objects.count(), 2)
        self.assertTrue(Player.objects.get(name='john1'))
        self.assertTrue(Player.objects.get(name='john2'))

        g = Game.objects.all()[0]

        # Making sure the game is created correctly
        self.assertEqual(len(g.board), 64)
        self.assertTrue(g.is_ready_to_start())

    def test_create_only_player_1(self):
        g = Game.objects.create(player1='john1')

        # The game has to be created
        self.assertEqual(Game.objects.count(), 1)

        # The players have to be created
        self.assertEqual(Player.objects.count(), 1)
        self.assertTrue(Player.objects.get(name='john1'))

        g = Game.objects.all()[0]

        # Making sure the game is created correctly
        self.assertEqual(len(g.board), 64)
        self.assertFalse(g.is_ready_to_start())

    def test_create_both_players_existing(self):
        create_player(name='john1')
        create_player(name='john2')
        g = Game.objects.create(player1='john1', player2='john2')

        # The game has to be created
        self.assertEqual(Game.objects.count(), 1)

        # The players were already created
        self.assertEqual(Player.objects.count(), 2)
        self.assertTrue(Player.objects.get(name='john1'))
        self.assertTrue(Player.objects.get(name='john2'))

        g = Game.objects.all()[0]

        # Making sure the game is created correctly
        self.assertEqual(len(g.board), 64)
        self.assertTrue(g.is_ready_to_start())

    def test_get_by_id_existent(self):
        create_game()
        g = Game.objects.get_by_id('john-peter-1')
        self.assertTrue(g)
        self.assertEqual(g.player1.name, 'john')
        self.assertEqual(g.player2.name, 'peter')

    def test_get_by_id_game_id_does_not_match(self):
        create_game()
        with self.assertRaises(Exception) as ex:
            g = Game.objects.get_by_id('john-peter-10')
        self.assertEqual(ex.exception.message, 'Game john-peter-10 not found')

    def test_get_by_id_players_in_reverse_order(self):
        create_game()
        with self.assertRaises(Exception) as ex:
            g = Game.objects.get_by_id('peter-john-1')
        self.assertEqual(ex.exception.message, 'Game peter-john-1 not found')

    def test_get_by_id_players_do_not_match(self):
        create_game()
        with self.assertRaises(Exception) as ex:
            g = Game.objects.get_by_id('pepe-juan-1')
        self.assertEqual(ex.exception.message, 'Game pepe-juan-1 not found')
