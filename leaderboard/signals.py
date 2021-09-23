from django.db.models.signals import post_save
from django.dispatch import receiver
from leaderboard.models import Player, PlayerScore, TeamRecord

#@receiver(post_save, sender=TeamRecord)
#def update_player_score(sender, instance, **kwargs):
    #print('hi, from update_player_score signal')
