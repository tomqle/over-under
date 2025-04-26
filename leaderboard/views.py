from django.db.models import Count
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
        print(f'\n----- entering {self.template_name} -----')

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

        players_scores = []
        for score in scores:
            players_scores.append(
                {
                    'player': score.player.name,
                    'score': f'{score.score:.1f}',
                    'second_chance': f'{score.second_chance:.1f}',
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
                'diff': f'{over_under_line.diff:.1f}'
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
        pick_agg = Pick.objects.filter(season=context['season']).select_related('team').values('team__name', 'over').annotate( total=Count('over'))

        pick_dict = {}
        for pick in pick_agg:
            team_name = pick['team__name']
            if team_name not in pick_dict.keys():
                pick_dict[team_name] = [0, 0]
            
            over_index = 0 if pick['over'] else 1
            pick_dict[team_name][over_index] = pick['total']

        ou_lines1 = []
        for ou_line in ou_lines:
            team_name = ou_line.team.name
            over_count = 0
            under_count = 0
            if team_name in pick_dict.keys():
                over_count = pick_dict[team_name][0]
                under_count = pick_dict[team_name][1]

            ou_lines1.append({
                'team_name': team_name,
                'line': ou_line.line,
                'diff': f'{ou_line.diff:.1f}',
                'over_count': over_count,
                'under_count': under_count
            })

        context['ou_lines'] = ou_lines1
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
            pick_set = picks.filter(player__name=score.player.name).select_related('team').order_by('-points')
            players_scores.append(
                {
                    'player': score.player.name,
                    'score': f'{score.score:.1f}',
                    'picks': [{
                        'team': pick.team,
                        'points': f'{pick.points: .1f}',
                        'over': 'O' if pick.over else 'U',
                        } for pick in pick_set],
                    'second_chance': f'{score.second_chance:.1f}',
                }
            )

        context['players_scores'] = players_scores
        context['url'] = 'rankings_extended'

        return context
