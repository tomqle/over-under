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

        team_standings = []

        if(self.source == 'espn'):
            url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/{year}/group'
            #url = f'https://www.espn.com/{league_name.lower()}/standings/_/season/2021/group/league'
            if league_name != None and league_name.upper() == 'NFL':
                url += '/league'
            if league_name != None and league_name == 'MLB':
                url += '/overall'
            print(url)

            page = requests.get(url)
            doc = lh.fromstring(page.content)

            table_elements = doc.xpath('//table')

            team_name_rows = self._get_team_name_rows(table_elements[0])
            team_standings_rows = self._get_team_standings_rows(table_elements[1])

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

        elif(self.source == 'sports-reference'):
            url = ''

            if league_name != None and league_name.upper() == 'NFL':
                url = f'https://www.pro-football-reference.com/years/{year}/'
            elif league_name != None and league_name.upper() == 'MLB':
                url = f'https://www.baseball-reference.com/leagues/majors/{year}-standings.shtml'


            page = requests.get(url)
            doc = lh.fromstring(page.content)
            standings_html = doc.xpath('//table')


            if league_name != None and league_name.upper() == 'NFL':
                COLUMN_TEAM_NAME = 0
                COLUMN_WIN = 1
                COLUMN_LOSE = 2
                COLUMN_PCT = 3
                COLUMN_TIE = 99
                for standings_tbl in standings_html:
                    standings_header = standings_tbl.getchildren()[2].getchildren()[0]
                    if standings_header[3].text_content() == 'T':
                        COLUMN_TIE = 3
                        COLUMN_PCT = 4

                    for standings_row in standings_tbl.getchildren()[3].getchildren():
                        if len(standings_row.getchildren()) > 1:
                            team_name = standings_row.getchildren()[COLUMN_TEAM_NAME].text_content()
                            wins = standings_row.getchildren()[COLUMN_WIN].text_content()
                            loses = standings_row.getchildren()[COLUMN_LOSE].text_content()
                            pct = standings_row.getchildren()[COLUMN_PCT].text_content()
                            tie = standings_row.getchildren()[COLUMN_TIE].text_content() if COLUMN_TIE == 3 else 0


                            team_standings.append({
                                'name': team_name,
                                'abbr': '',
                                'w': wins,
                                'l': loses,
                                't': tie,
                                'pct': pct,
                            })

            elif league_name != None and league_name.upper() == 'MLB':
                COLUMN_TEAM_NAME = 0
                COLUMN_WIN = 1
                COLUMN_LOSE = 2
                COLUMN_PCT = 3
                for standings_tbl in standings_html:
                    for i in range(5):
                        team_name = standings_tbl.getchildren()[3].getchildren()[i].getchildren()[COLUMN_TEAM_NAME].text_content()
                        wins = standings_tbl.getchildren()[3].getchildren()[i].getchildren()[COLUMN_WIN].text_content()
                        loses = standings_tbl.getchildren()[3].getchildren()[i].getchildren()[COLUMN_LOSE].text_content()
                        pct = standings_tbl.getchildren()[3].getchildren()[i].getchildren()[COLUMN_PCT].text_content()

                        team_standings.append({
                            'name': team_name,
                            'abbr': '',
                            'w': wins,
                            'l': loses,
                            't': 0,
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