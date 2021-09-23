from django.apps import AppConfig
from django.db.models import signals

class LeaderboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaderboard'

    #def ready(self):
        #import leaderboard.signals
