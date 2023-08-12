import requests
import lxml.html as lh
from typing import List

class StandingsData:
    def __init__(self, source: str):
        self.source: str = source
    
    def get_season_standings(self, league_name: str, year: str) -> dict:
        pass

class StandingsDataScraper(StandingsData):
    def get_season_standings(self, league_name: str, year: str) -> dict:
        url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/{year}/group'
        #url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/2021/group/league'
        if league_name == 'NFL':
            url += '/league'
        if league_name == 'MLB':
            url += '/overall'
        print(url)

        page = requests.get(url)
        doc = lh.fromstring(page.content)

        table_elements = doc.xpath('//table')

        team_name_rows = self._get_team_name_rows(table_elements[0])
        team_standings_rows = self._get_team_standings_rows(table_elements[1])

        team_standings = []
        for i in range(0, len(team_name_rows)):
            print(i)
            if league_name == 'NFL':
                ties = self._get_nfl_team_tie(team_standings_rows[i])
                pct = self._get_nfl_team_pct(team_standings_rows[i])
            elif league_name == 'MLB':
                ties = 0
                pct = self._get_team_pct(team_standings_rows[i])

            team_abbr = self._get_nfl_team_abbr(team_name_rows[i])
            team_name = self._get_nfl_team_name(team_name_rows[i])
            wins = self._get_team_wins(team_standings_rows[i])
            loses = self._get_team_loses(team_standings_rows[i])


            if team_abbr == '':
                team_abbr = team_name
                team_name = self._get_team_name(team_name_rows[i])

            team_standings.append({
                'name': team_name,
                'abbr': team_abbr,
                'w': wins,
                'l': loses,
                't': ties,
                'pct': pct,
            })

        print('_get_season_standings()')
        print(team_standings)

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

class StandingsDataAPI(StandingsData):
    def __init__(self, source: str, token: str):
        self.token: str = token
        super().__init__(source)

    def get_season_standings(self, league: str, year: str) -> List:
        team_records: dict = {}
        json_body: List = self._get_response(league, year)
        for team_entry in json_body:
            team_record: dict = self._get_team_record(league, team_entry)
            team_name: str = team_record['name']
            if team_name not in team_records.keys():
                team_records[team_name] = team_record

        team_standings: List = list(team_records.values())
        print('_get_season_standings()')
        print(team_standings)

        return team_standings
    
    def _get_team_record(self, league: str, team_entry: dict) -> dict:
        team_name: str = ''
        wins: int = 0
        loses: int = 0
        ties: int = 0
        pct: float = 0

        if league == 'MLB':
            team_name = team_entry['team']['name']
            wins = team_entry['games']['win']['total']
            pct = team_entry['games']['win']['percentage']
            loses = team_entry['games']['lose']['total']

        if league == 'NFL':
            team_name = team_entry['team']['name']
            wins = team_entry['won']
            loses = team_entry['lost']
            ties = team_entry['ties']

        return {
            'name': team_name,
            'abbr': '',
            'w': wins,
            'l': loses,
            't': ties,
            'pct': pct,
        }

    def _get_baseurl(self, league) -> str:
        sport: str = ''
        if league == 'NFL':
            sport = 'american-football'
        elif league == 'MLB':
            sport = 'baseball'

        if self.source == 'API-Sports':
            return f'https://v1.{sport}.api-sports.io/'
        
        return None
    
    def _get_url(self, league: str, year: str) -> str:
        sport: str = ''
        if league == 'NFL':
            sport = 'american-football'
        elif league == 'MLB':
            sport = 'baseball'

        if self.source == 'API-Sports':
            return f'https://v1.{sport}.api-sports.io/standings?league=1&season={year}'
        
        return None
    
    def _get_response(self, league, year) -> dict:
        payload = {}
        json_body = {}
        baseurl = self._get_baseurl(league)
        if baseurl:
            headers = {
                'x-rapidapi-key': self.token,
                'x-rapidapi-host': baseurl
            }

            response = requests.request('GET', self._get_url(league, year), headers=headers, data=payload)
            json_body: List = []
            if league == 'NFL':
                json_body = response.json()['response']
            elif league == 'MLB':
                json_body = response.json()['response'][0]
                

        return json_body