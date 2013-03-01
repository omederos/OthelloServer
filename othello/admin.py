# -*- coding: utf-8 -*-

from django.contrib import admin
from othello.models import (Game, Player)


class GameInline1(admin.StackedInline):
    model = Game
    fk_name = 'player1'
    max_num = 0
    fields = ('score_player1', 'score_player2', 'winner')
    extra = 0
    verbose_name_plural = 'Games being 1st player'


class GameInline2(admin.StackedInline):
    model = Game
    fk_name = 'player2'
    fields = ('score_player1', 'score_player2', 'winner')
    max_num = 0
    extra = 0
    verbose_name_plural = 'Games being 2nd player'


class PlayerAdmin(admin.ModelAdmin):
    inlines = [GameInline1, GameInline2]


class GameAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'game_started', 'score_player1',
                    'score_player2', 'winner')


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
