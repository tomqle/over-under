from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.db.models import Max

from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, Season, Team, TeamRecord

# Create your views here.

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/rankings/')

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league = League.objects.get(name=kwargs['league'])
        season = Season.objects.get(name=kwargs['season'], league=league)
        seasons = Season.objects.all().order_by('-name', '-league__name')

        context['league'] = league
        context['season'] = season
        context['seasons'] = seasons

        return context

class DefaultRankingsView(View):
    def get(self, request, *args, **kwargs):
        season_year = Season.objects.aggregate(Max('name')).get('name__max')
        league_name = ''
        if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
            league_name = 'NFL/'
        elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
            league_name = 'MLB/'

        return HttpResponseRedirect('/rankings/' + league_name + season_year )

class LeaguesView(TemplateView):
    template_name = "leagues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['leagues'] = League.objects.all()

        return context

class SeasonsView(TemplateView):
    template_name = "seasons.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league = League.objects.get(name=kwargs['league'])
        seasons = Season.objects.filter(league=league)

        context['league'] = league
        context['seasons'] = seasons

        return context

class RankingsView(BaseView):

    template_name = "rankings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scores = PlayerScore.objects.filter(season=context['season']).select_related('player').order_by('-score')
        picks = Pick.objects.filter(season=context['season']).select_related('player')

        players_scores = []
        for score in scores:
            pick_set = picks.filter(player__name=score.player.name).select_related('team').order_by('pk')
            players_scores.append(
                {
                    'player': score.player.name,
                    'score': score.score,
                    'picks': pick_set,
                    'second_chance': score.second_chance,
                }
            )

        context['players_scores'] = players_scores
        context['url'] = 'rankings'

        return context

class DefaultStandingsView(View):
    def get(self, request, *args, **kwargs):
        season_year = Season.objects.aggregate(Max('name')).get('name__max')
        league_name = ''
        if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
            league_name = 'NFL/'
        elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
            league_name = 'MLB/'

        return HttpResponseRedirect('/standings/' + league_name + season_year )

class StandingsView(BaseView):

    template_name = "standings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team_records = TeamRecord.objects.filter(season=context['season']).select_related('team').order_by('-win_count')
        over_under_lines = OverUnderLine.objects.filter(season=context['season'])

        team_records1 = []
        for team_record in team_records:
            over_under_lines1 = over_under_lines.filter(team=team_record.team)
            over_under_line = None
            if len(over_under_lines1) < 1:
                over_under_line = OverUnderLine(line=0)
            else:
                over_under_line = over_under_lines1[0]

            team_records1.append({
                'team_name': team_record.team.name,
                'win_count': team_record.win_count,
                'lose_count': team_record.lose_count,
                'tie_count': team_record.tie_count,
                'win_pct': team_record.win_pct,
                'win_proj': f'{over_under_line.line + over_under_line.diff:.1f}',
                'line': over_under_line.line,
                'diff': over_under_line.diff
            })

        context['team_records'] = team_records1
        context['url'] = 'standings'

        return context

class DefaultOverUnderLineView(View):
    def get(self, request, *args, **kwargs):
        season_year = Season.objects.aggregate(Max('name')).get('name__max')
        league_name = ''
        if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
            league_name = 'NFL/'
        elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
            league_name = 'MLB/'

        return HttpResponseRedirect('/over_under_lines/' + league_name + season_year )

class OverUnderLineView(BaseView):
    template_name = "ou_line.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ou_lines = OverUnderLine.objects.filter(season=context['season']).select_related('team').order_by('-line')

        context['ou_lines'] = ou_lines
        context['url'] = 'over_under_lines'

        return context

class DefaultPicksView(View):
    def get(self, request, *args, **kwargs):
        season_year = Season.objects.aggregate(Max('name')).get('name__max')
        league_name = ''
        if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
            league_name = 'NFL/'
        elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
            league_name = 'MLB/'

        return HttpResponseRedirect('/picks/' + league_name + season_year )

class PicksView(BaseView):
    template_name = "picks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scores = PlayerScore.objects.filter(season=context['season']).select_related('player').order_by('-score')
        #players = Player.objects.filter(pick__season=season).distinct()
        picks = Pick.objects.filter(season=context['season']).select_related('player')

        players_picks = []
        for score in scores:
            pick_set = picks.filter(player__name=score.player.name).select_related('team').order_by('pk')
            players_picks.append(
                {
                    'player': score.player.name,
                    'score': score.score,
                    'picks': pick_set,
                }
            )

        context['players_picks'] = players_picks
        context['url'] = 'picks'

        return context

class DefaultRankingsExtendedView(View):
    def get(self, request, *args, **kwargs):
        season_year = Season.objects.aggregate(Max('name')).get('name__max')
        league_name = ''
        if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
            league_name = 'NFL/'
        elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
            league_name = 'MLB/'

        return HttpResponseRedirect('/rankings_extended/' + league_name + season_year )

class RankingsExtendedView(BaseView):
    template_name = "rankings_extended.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scores = PlayerScore.objects.filter(season=context['season']).select_related('player').order_by('-score')
        #players = Player.objects.filter(pick__season=season).distinct()
        picks = Pick.objects.filter(season=context['season']).select_related('player')

        players_scores = []
        for score in scores:
            pick_set = picks.filter(player__name=score.player.name).select_related('team').order_by('pk')
            players_scores.append(
                {
                    'player': score.player.name,
                    'score': score.score,
                    'picks': pick_set,
                    'second_chance': score.second_chance,
                }
            )

        context['players_scores'] = players_scores
        context['url'] = 'rankings_extended'

        return context
