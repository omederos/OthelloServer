from django.test.testcases import TestCase
import time
from othello.models import *
from othello.tests.utils import create_player, create_game


class GameTests(TestCase):
    def create(self, start_it=True, board=None):
        g = create_game()
        if start_it:
            g.start_game()
        if board:
            g.board = board
            g.save()
        return g

    def test_get_piece_color(self):
        g = create_game()
        self.assertEqual(g.get_piece_color('john'), WHITE)
        self.assertEqual(g.get_piece_color('peter'), BLACK)

    def test_unicode(self):
        g = self.create(False)
        self.assertEqual(unicode(g), 'john-peter-1')

    def test_is_turn_game_not_started_yet(self):
        g = self.create(False)
        with self.assertRaises(Exception) as ex:
            g.is_turn('john')
        self.assertEqual(ex.exception.message, 'The game hasn\'t started yet.'
                                               ' Make sure both players have '
                                               'been connected')

    def test_is_turn_non_existing_player(self):
        g = self.create()
        with self.assertRaises(Exception) as ex:
            g.is_turn('oscar')
        self.assertEqual(ex.exception.message, 'The player oscar is not '
                                               'playing in this game')

    def test_is_turn_false(self):
        g = self.create()
        timeout_is_turn = g.timeout_is_turn
        result = g.is_turn('john')
        self.assertFalse(result[0])
        self.assertEqual(result[1], g.board)
        self.assertEqual(g.timeout_is_turn, timeout_is_turn)
        self.assertFalse(g.is_turn_already_called)

    def test_is_turn_true(self):
        g = self.create()
        result = g.is_turn('peter')
        self.assertTrue(result[0])
        self.assertEqual(result[1], g.board)
        self.assertIsNotNone(g.timeout_is_turn)

    def test_is_turn_timeout_saved_only_once(self):
        g = self.create()
        g.is_turn('peter')
        self.assertTrue(g.is_turn_already_called)

        d = g.timeout_is_turn
        time.sleep(0.5)

        g.is_turn('peter')

        # Make sure the datetime stored was the very first one
        self.assertEqual(d, g.timeout_is_turn)

    def test_get_possible_moves_1(self):
        b = '1111011100210200000122200001200000022200002002000200000000000000'
        g = self.create(board=b)
        moves = g.get_possible_moves(BLACK)
        self.assertEqual(4, len(list(moves)))
        moves = g.get_possible_moves(WHITE)
        self.assertEqual(8, len(list(moves)))

    def test_get_possible_moves_2(self):
        g = self.create()
        moves = g.get_possible_moves(BLACK)
        self.assertEqual(4, len(list(moves)))
        moves = g.get_possible_moves(WHITE)
        self.assertEqual(4, len(list(moves)))

    def test_get_possible_moves(self):
        b = '0222222100000000000000000000000000000000000000000000000000000000'
        g = self.create(board=b)
        moves = g.get_possible_moves(BLACK)
        self.assertEqual(0, len(list(moves)))
        moves = g.get_possible_moves(WHITE)
        self.assertEqual(1, len(list(moves)))

    def test_update_board_one_line_horizontal(self):
        b = '0222222100000000000000000000000000000000000000000000000000000000'
        g = self.create(board=b)
        g.update_board(g._get_matrix(), 'john', (0, 0))
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '1111111100000000000000000000000000000000000000000000000000000000'
        )

    def test_update_board_one_line_vertical(self):
        b = '0000000000000000000000000000100000001000000020000000000000000000'
        g = self.create(board=b)
        g.update_board(g._get_matrix(), 'peter', (2, 4))
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0000000000000000000020000000200000002000000020000000000000000000'
        )

    def test_update_board_one_line_diagonal(self):
        b = '0000000000000000000100000000200000000200000000000000000000000000'
        g = self.create(board=b)
        g.update_board(g._get_matrix(), 'john', (5, 6))
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0000000000000000000100000000100000000100000000100000000000000000'
        )

    def test_update_board_vertical_both_sides(self):
        b = '0000000000010000000200000000000000020000000100000000000000000000'
        g = self.create(board=b)
        g.update_board(g._get_matrix(), 'john', (3, 3))
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0000000000010000000100000001000000010000000100000000000000000000'
        )

    def test_update_board_3_directions(self):
        b = '0000000000010000000200002210222100020000000100000000000000000000'
        g = self.create(board=b)
        g.update_board(g._get_matrix(), 'john', (3, 3))
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0000000000010000000100002211111100010000000100000000000000000000'
        )

    def test_move_ok(self):
        g = self.create()
        self.assertFalse(g.player1_turn)
        g.move('peter', '(3,2)')
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0000000000000000000000000022200000021000000000000000000000000000'
        )
        self.assertTrue(g.player1_turn)

    def test_move_game_not_started(self):
        g = self.create(start_it=False)
        with self.assertRaises(Exception) as ex:
            g.move('peter', '(3,2)')
        self.assertEqual(
            ex.exception.message,
            'The game hasn\'t started yet. Make sure both players have been '
            'connected')

    def test_move_game_already_finished(self):
        g = self.create()
        g.winner = g.player1
        g.save()
        with self.assertRaises(Exception) as ex:
            g.move('peter', '(3,2)')
        self.assertEqual(ex.exception.message, 'This game already finished')

    def test_move_non_existing_player(self):
        g = self.create()
        with self.assertRaises(Exception) as ex:
            g.move('oscar', '(3,2)')
        self.assertEqual(ex.exception.message, 'The player oscar is not '
                                               'playing in this game')

    def test_move_not_in_the_turn(self):
        g = self.create()
        with self.assertRaises(Exception) as ex:
            g.move('john', '(3,5)')
        self.assertEqual(ex.exception.message, 'You must wait for your turn')

    def test_move_invalid_first_one(self):
        g = self.create()
        with self.assertRaises(Exception) as ex:
            g.move('peter', '(0,0)')
        self.assertEqual(ex.exception.message, 'Invalid move')
        g = Game.objects.get(id=1)
        self.assertEqual(g.invalid_moves_player1, 0)
        self.assertEqual(g.invalid_moves_player2, 1)

        # Make sure it loses his turn
        self.assertTrue(g.player1_turn)

    def test_move_invalid_third_one(self):
        g = self.create()
        for i in xrange(3):
            try:
                g.player1_turn = False
                g.save()
                g.move('peter', '(0,0)')
            except:
                pass
        g = Game.objects.get(id=1)
        self.assertEqual(g.invalid_moves_player1, 0)
        self.assertEqual(g.invalid_moves_player2, 3)

        self.assertEqual(g.winner, g.player1)
        self.assertTrue(g.game_finished())

        self.assertEqual(g.score_player1, 63)
        self.assertEqual(g.score_player2, 1)

    def test_move_ok_keeps_playing(self):
        b = '0002020200222220001201220001222000021222002021200200222020002200'
        g = self.create(board=b)
        g.move('peter', '(1,1)')
        g = Game.objects.get(id=1)
        self.assertEqual(
            g.board,
            '0002020202222220002201220002222000022222002022200200222020002200'
        )
        self.assertFalse(g.player1_turn)

    def test_move_timeout_turn_change_is_updated(self):
        g = self.create()
        timeout = g.timeout_turn_change
        g.move('peter', '(3,2)')
        g = Game.objects.get(id=1)
        self.assertTrue(g.timeout_turn_change > timeout)

    def test_move_game_finished_without_all_pieces(self):
        b = '0221000000000000000000000000000000000000000000000000000000001000'
        g = self.create(board=b)
        g.move('peter', '(0,4)')
        g = Game.objects.get(id=1)
        self.assertTrue(g.game_finished())
        self.assertNotEqual(g.score_player1, 0)
        self.assertNotEqual(g.score_player2, 0)


class GameManagerTests(TestCase):
    def test_create_non_existing_players(self):
        Game.objects.create(player1='john1', player2='john2')

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
        Game.objects.create(player1='john1')

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
        Game.objects.create(player1='john1', player2='john2')

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
            Game.objects.get_by_id('john-peter-10')
        self.assertEqual(ex.exception.message, 'Game john-peter-10 not found')

    def test_get_by_id_players_in_reverse_order(self):
        create_game()
        with self.assertRaises(Exception) as ex:
            Game.objects.get_by_id('peter-john-1')
        self.assertEqual(ex.exception.message, 'Game peter-john-1 not found')

    def test_get_by_id_players_do_not_match(self):
        create_game()
        with self.assertRaises(Exception) as ex:
            Game.objects.get_by_id('pepe-juan-1')
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
