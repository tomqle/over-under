# Create your tasks here

from celery import shared_task
from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, PlayerScoreManager, Season, Team, TeamRecord

import requests
import lxml.html as lh

@shared_task
def get_nfl_2021_standings():
    return get_season_standings('NFL', '2021')

def get_season_standings(league_name, year):
    standings = _get_season_standings(league_name, year)

    _bulk_create_league_teams(standings, league_name)

    team_objs_dict = {team_obj.name:team_obj for team_obj in Team.objects.all()}
    _bulk_update_league_team_records(standings, team_objs_dict, league_name, year)

    season = Season.objects.get(name=year, league=League.objects.get(name=league_name))
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

            team_records_to_update.append(team_record_to_update)
        
    TeamRecord.objects.bulk_create(team_records_to_create)
    TeamRecord.objects.bulk_update(team_records_to_update, ['win_count', 'lose_count'])

def _get_season_standings(league_name, year):
    #url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/{year}/group/league'
    url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/2021/group/league'
    page = requests.get(url)
    doc = lh.fromstring(page.content)

    table_elements = doc.xpath('//table')

    team_name_rows = _get_team_name_rows(table_elements[0])
    team_standings_rows = _get_team_standings_rows(table_elements[1])

    team_standings = []
    for i in range(0, len(team_name_rows)):
        team_abbr = _get_nfl_team_abbr(team_name_rows[i])
        team_name = _get_nfl_team_name(team_name_rows[i])
        wins = _get_team_wins(team_standings_rows[i])
        loses = _get_team_loses(team_standings_rows[i])
        ties = _get_nfl_team_tie(team_standings_rows[i])
        pct = _get_nfl_team_pct(team_standings_rows[i])

        if team_abbr == '':
            team_abbr = team_name
            team_name = _get_team_name(team_name_rows[i])

        team_standings.append({
            'name': team_name,
            'abbr': team_abbr,
            'w': wins,
            'l': loses,
            't': ties,
            'pct': pct,
        })

    return team_standings



def _get_team_name_rows(html_table):
    return html_table.getchildren()[2].getchildren()

def _get_team_standings_rows(html_table):
    return html_table.getchildren()[5].getchildren()

def _get_nfl_team_abbr(html_tr):
    return html_tr.getchildren()[0].getchildren()[0].getchildren()[1].getchildren()[0].text_content()

def _get_team_abbr(html_tr):
    return html_tr.getchildren()[0].getchildren()[0].getchildren()[2].getchildren()[0].text_content()

def _get_nfl_team_name(html_tr):
    return html_tr.getchildren()[0].getchildren()[0].getchildren()[2].getchildren()[0].text_content()

def _get_team_name(html_tr):
    return html_tr.getchildren()[0].getchildren()[0].getchildren()[3].getchildren()[0].text_content()

def _get_team_wins(html_tr):
    return html_tr.getchildren()[0].getchildren()[0].text_content()

def _get_team_loses(html_tr):
    return html_tr.getchildren()[1].getchildren()[0].text_content()

def _get_nfl_team_tie(html_tr):
    return html_tr.getchildren()[2].getchildren()[0].text_content()

def _get_nfl_team_pct(html_tr):
    return html_tr.getchildren()[3].getchildren()[0].text_content()

def _get_team_pct(html_tr):
    return html_tr.getchildren()[2].getchildren()[0].text_content()
