from django.db import models

from leaderboard.models import League, Player, Season, Team


class Week(models):
    league = models.ForeignKey(League, null=True, blank=True, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, null=True, blank=True, on_delete=models.CASCADE)
    number = models.IntegerField()
    start_date = models.DateField()
    jackpot_value = models.DecimalField(max_digits=10, decimal_places=3, default=360.0)
    jackpot_winner = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)
    assist_value = models.DecimalField(max_digits=10, decimal_places=3, default=40.0)
    assist_winner = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)


class Game(models):
    league = models.ForeignKey(League, null=True, blank=True, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, null=True, blank=True, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE)
    score1 = models.IntegerField
    score2 = models.IntegerField


class WeekPick(models):
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)
    league = models.ForeignKey(League, null=True, blank=True, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, null=True, blank=True, on_delete=models.CASCADE)


class JackpotScore(models):
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)
    league = models.ForeignKey(League, null=True, blank=True, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, null=True, blank=True, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)

