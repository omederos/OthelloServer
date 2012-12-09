from django.test.testcases import TestCase
import time
from othello.models import *
from othello.tests.utils import create_player, create_game


class GameTests(TestCase):
    def create_game(self, start_it=True):
        g = create_game()
        if start_it:
            g.start_game()
        return g

    def test_unicode(self):
        g = self.create_game(False)
        self.assertEqual(unicode(g), 'john-peter-1')

    def test_is_turn_game_not_started_yet(self):
        g = self.create_game(False)
        with self.assertRaises(Exception) as ex:
            g.is_turn('john')
        self.assertEqual(ex.exception.message, 'The game hasn\'t started yet.'
                                               ' Make sure both players have '
                                               'been connected')

    def test_is_turn_non_existing_player(self):
        g = self.create_game()
        with self.assertRaises(Exception) as ex:
            g.is_turn('oscar')
        self.assertEqual(ex.exception.message, 'The player oscar is not '
                                               'playing in this game')

    def test_is_turn_false(self):
        g = self.create_game()
        self.assertFalse(g.is_turn('john'))
        self.assertIsNone(g.timeout_is_turn)
        self.assertFalse(g.is_turn_already_called)

    def test_is_turn_true(self):
        g = self.create_game()
        self.assertTrue(g.is_turn('peter'))
        self.assertIsNotNone(g.timeout_is_turn)

    def test_is_turn_timeout_saved_only_once(self):
        g = self.create_game()
        g.is_turn('peter')
        self.assertTrue(g.is_turn_already_called)

        d = g.timeout_is_turn
        time.sleep(0.5)

        g.is_turn('peter')

        # Make sure the datetime stored was the very first one
        self.assertEqual(d, g.timeout_is_turn)


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
        self.assertFalse(g.game_started)

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
        self.assertFalse(g.game_started)

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
        self.assertFalse(g.game_started)

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

    def test_connect(self):
        game_id = Game.objects.connect('john', 'peter')
        GAME_ID = 'john-peter-1'
        self.assertEqual(game_id, GAME_ID)

        # Make sure the game hasn't started yet!
        g = Game.objects.get(id=1)
        self.assertEqual(g.game_started, False)

        # Second call. The remaining player is joining
        game_id = Game.objects.connect('john', 'peter')
        self.assertEqual(game_id, GAME_ID)

        # Make sure no new games are created
        self.assertEqual(Game.objects.count(), 1)
        g = Game.objects.get(id=1)

        # This game already started!
        self.assertEqual(g.game_started, True)
