from django.db import models
from decimal import Decimal
from users.models import User

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class PlayerScoreManager(models.Manager):
    def update_score(self, season):
        scores = self.filter(season=season)
        scores_to_update = []

        for score in scores:
            previous_score = score.score
            if score.calculate() != previous_score:
                scores_to_update.append(score)

        self.bulk_update(scores_to_update, ['score'])

class PlayerScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    objects = PlayerScoreManager()

    def calculate(self):
        picks = self.player.pick_set.all()
        running_score = 0

        for pick in picks:
            team = pick.team
            team_record = team.teamrecord_set.get(season=self.season)
            games_played = team_record.win_count + team_record.lose_count + team_record.tie_count
            projected_win_count = float(team_record.win_count) * 16.0 / float(games_played)
            over_line = self.season.overunderline_set.get(team=team).line
            points = Decimal(projected_win_count) - over_line
            print(f'points: {points}')
            if pick.over:
                running_score += points
            else:
                running_score -= points

        print(f'score: {running_score}')

        self.score = running_score

        return running_score

    class Meta:
        unique_together = (
            'player',
            'season',
        )

class Team(models.Model):
    league = models.ForeignKey('League', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            'league',
            'name',
        )

class League(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Season(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.league.name} {self.name}'

    class Meta:
        unique_together = (
            'league',
            'name',
        )

class TeamRecord(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    win_count = models.IntegerField()
    lose_count = models.IntegerField()
    tie_count = models.IntegerField()

    def __str__(self):
        return f'{self.team.name}: {self.win_count}-{self.lose_count}-{self.tie_count}'
    
    class Meta:
        unique_together = (
            'team',
            'season',
        )

class Pick(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    over = models.BooleanField()

    class Meta:
        unique_together = (
            'player',
            'team',
            'season',
        )

class OverUnderLine(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    line = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        unique_together = (
            'team',
            'season',
        )
