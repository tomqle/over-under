from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect

from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, Season, Team, TeamRecord

# Create your views here.

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/rankings/NFL/2021/')

class RankingsView(TemplateView):

    template_name = "rankings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league = League.objects.get(name=kwargs['league'])
        season = Season.objects.get(name=kwargs['season'], league=league)
        player_scores = PlayerScore.objects.filter(season=season).select_related('player').order_by('-score')

        context['player_scores'] = player_scores

        return context

class StandingsView(TemplateView):

    template_name = "standings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league = League.objects.get(name=kwargs['league'])
        season = Season.objects.get(name=kwargs['season'], league=league)
        teams = Team.objects.filter(league=league)
        team_records = TeamRecord.objects.filter(season=season).select_related('team').order_by('-win_count')

        context['team_records'] = team_records

        return context
