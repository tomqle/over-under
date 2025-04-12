# Create your tasks here

from django.conf import settings

from django.db.models import Max
from django.db.models.query import QuerySet

from celery import shared_task
from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, PlayerScoreManager, Season, Team, TeamRecord
from leaderboard.datasource.standings_data import StandingsData, StandingsDataAPI, StandingsDataScraper

import os
import requests
import lxml.html as lh
from typing import List

@shared_task
def get_season_standings_auto():
    season_year = Season.objects.aggregate(Max('name')).get('name__max')
    league_name = ''
    
    if Season.objects.filter(name=season_year, league=League.objects.get(name='NFL')).count() > 0:
        league_name = 'NFL'
    elif Season.objects.filter(name=season_year, league=League.objects.get(name='MLB')).count() > 0:
        league_name = 'MLB'

    print('get_season_standings(' + league_name + ', ' + season_year + ')')

    if league_name == '':
        return None
    
    return get_season_standings(league_name, season_year)

@shared_task
def get_nfl_2022_standings():
    return get_season_standings('NFL', '2022')

@shared_task
def get_nfl_2021_standings():
    return get_season_standings('NFL', '2021')

def get_season_standings(league, year):
    if getattr(settings, 'STANDINGS_METHOD', 'scrape') == 'api':
        token: str = getattr(settings, 'API_SPORTS_TOKEN', None)
        data_source: StandingsData = StandingsDataAPI(getattr(settings, 'STANDINGS_SOURCE', 'API-Sports'), token)
    elif getattr(settings, 'STANDINGS_METHOD', 'scrape') == 'scrape':
        data_source: StandingsData = StandingsDataScraper(getattr(settings, 'STANDINGS_SOURCE', 'sports-reference'))

    standings = data_source.get_season_standings(league, year)
    for s in standings:
        _fill_team_abbr(s)

    #_bulk_create_league_teams(standings, league)

    team_objs_dict = {team_obj.name:team_obj for team_obj in Team.objects.all()}
    _bulk_update_league_team_records(standings, team_objs_dict, league, year)

    season = Season.objects.get(name=year, league=League.objects.get(name=league))
    PlayerScore.objects.update_score(season=season)

    OverUnderLine.objects.update_score(season)

    print(standings)

    return standings

def _bulk_create_league_teams(standings, league_name):
    league, created = League.objects.get_or_create(name=league_name)
    teams_to_create = []
    teams_to_update = []
    for team_dict in standings:
        if not Team.objects.filter(name=team_dict['name']):
            teams_to_create.append(Team(name=team_dict['name'], abbreviation=team_dict['abbr'], league=league))
        #else:
            #team_to_update = Team.objects.filter(name=team_dict['name'])[0]
            #team_to_update.abbreviation = team_dict['abbr']
            #teams_to_update.append(team_to_update)

    Team.objects.bulk_create(teams_to_create)
    #Team.objects.bulk_update(teams_to_update, ['abbreviation'])

def _bulk_update_league_team_records(standings, team_objs_dict, league_name, year):
    season, created = Season.objects.get_or_create(name=year, league=League.objects.get(name=league_name))
    team_records_to_create = []
    team_records_to_update = []
    for team_dict in standings:
        if team_dict['name'] in team_objs_dict.keys():
            if not TeamRecord.objects.filter(team=team_objs_dict[team_dict['name']], season=season):
                team_records_to_create.append(
                    TeamRecord(
                        team=team_objs_dict[team_dict['name']],
                        season=season,
                        win_count=team_dict['w'],
                        lose_count=team_dict['l'],
                        tie_count=team_dict['t'],
                    )
                )
            else:
                team_record_to_update = TeamRecord.objects.get(team=team_objs_dict[team_dict['name']], season=season)

                team_record_to_update.win_count = team_dict['w']
                team_record_to_update.lose_count = team_dict['l']
                team_record_to_update.tie_count = team_dict['t']

                team_records_to_update.append(team_record_to_update)
        
    print('_bulk_update_league_team_records()')
    print(team_records_to_create)

    TeamRecord.objects.bulk_create(team_records_to_create)
    TeamRecord.objects.bulk_update(team_records_to_update, ['win_count', 'lose_count', 'tie_count'])

def _fill_team_abbr(team_entry: dict):
    if team_entry['abbr'] == '':
        teams: QuerySet = Team.objects.filter(name=team_entry['name'])
        if len(teams) > 0:
            team_entry['abbr'] = teams[0].abbreviation
