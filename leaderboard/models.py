from django.db import models
from decimal import Decimal
from users.models import User
from datetime import datetime

# Create your models here.

class BaseModel(models.Model):
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Player(BaseModel):
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

class PlayerScore(BaseModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    objects = PlayerScoreManager()

    def __str__(self):
        return f'{self.player} {self.season} {self.score}'

    def calculate(self):
        picks = self.player.pick_set.filter(season=self.season).order_by('pk')
        running_score = 0

        print(f'player: {self.player}')

        for pick in picks:
            team = pick.team
            pick.calculate()
            pick.save()
            running_score += pick.points

        print(f'score: {running_score}')

        self.score = running_score

        return running_score
    
    @property
    def second_chance(self):
        picks = self.player.pick_set.filter(season=self.season).order_by('-pk')
        return self.score - picks[0].points

    class Meta:
        unique_together = (
            'player',
            'season',
        )

class Team(BaseModel):
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

class League(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    games_count = models.IntegerField()

    def __str__(self):
        return self.name

class Season(BaseModel):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    games_count = models.IntegerField()

    def __str__(self):
        return f'{self.league.name} {self.name}'

    class Meta:
        unique_together = (
            'league',
            'name',
        )

class TeamRecord(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    win_count = models.IntegerField()
    lose_count = models.IntegerField()
    tie_count = models.IntegerField()

    @property
    def win_pct(self):
        pct = self.win_count / float(self.win_count + self.lose_count + self.tie_count)
        return f'{pct:.3f}'

    @property
    def win_proj(self):
        games_played = self.win_count + self.lose_count + self.tie_count
        tie_point = float(self.tie_count) / 2.0
        projected_win_count = float(self.win_count + tie_point) * self.season.games_count / float(games_played)
        return projected_win_count

    def __str__(self):
        return f'{self.season.league.name} {self.season.name} {self.team.name}: {self.win_count}-{self.lose_count}-{self.tie_count}'
    
    class Meta:
        unique_together = (
            'team',
            'season',
        )

class Pick(BaseModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    over = models.BooleanField()
    pickorder = models.IntegerField(blank=True, null=True)
    points = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)

    def calculate(self):
        team_record = self.team.teamrecord_set.get(season=self.season)
        over_line = self.season.overunderline_set.get(team=self.team).line
        self.points = Decimal(team_record.win_proj) - over_line
        if not self.over:
            self.points *= -1
        print(f'points: { self.points }')

    def __str__(self):
        return f'{self.player}: {self.season} {self.team} <{"O" if self.over else "U"}>'

    class Meta:
        unique_together = (
            'player',
            'team',
            'season',
            'pickorder',
        )

class OverUnderLineManager(models.Manager):
    def update_score(self, season):
        over_under_lines = OverUnderLine.objects.filter(season=season)
        ou_lines_to_update = []

        for over_under_line in over_under_lines:
            over_under_line.calculate()
            ou_lines_to_update.append(over_under_line)

        self.bulk_update(ou_lines_to_update, ['diff'])

class OverUnderLine(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    line = models.DecimalField(max_digits=4, decimal_places=1)
    diff = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    objects = OverUnderLineManager()

    def __str__(self):
        return f'{self.season} {self.team} {self.line}'

    def calculate(self):
        team_record = TeamRecord.objects.get(team=self.team, season=self.season)
        games_played = team_record.win_count + team_record.lose_count + team_record.tie_count
        projected_win_count = team_record.win_count + (float(team_record.tie_count) / 2)
        if games_played != self.season.games_count:
            projected_win_count = float(team_record.win_count) * self.season.games_count / float(games_played)
        self.diff = Decimal(projected_win_count) - self.line

        return self.diff

    class Meta:
        unique_together = (
            'team',
            'season',
        )
