from django.conf.urls.defaults import *
from othello.views import connect, get_board, is_turn, move

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^connect', connect, name='connect'),
    url(r'^get_board', get_board, name='get_board'),
    url(r'^is_turn', is_turn, name='is_turn'),
    url(r'^move', move, name='move'),
    # Example:
    # (r'^OthelloServer/', include('OthelloServer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
