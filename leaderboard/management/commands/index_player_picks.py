from django.core.management.base import BaseCommand
from logging import getLogger

from leaderboard.models import League, OverUnderLine, Pick, Player, Season, Team

import openpyxl

LOG = getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        if file_name:
            wb = openpyxl.load_workbook(file_name)
            picks_sheet = wb['Picks']
            lines_sheet = wb['Lines']

            player_picks = self._read_player_picks_from_excel(picks_sheet)
            self._bulk_create_player_picks_from_excel(player_picks)

            over_under_lines = self._read_over_under_line_from_excel(lines_sheet)
            self._bulk_create_over_under_lines(over_under_lines)


    def _read_player_picks_from_excel(self, sheet):
        player_picks = []
        league = League.objects.get(name='NFL')
        season = Season.objects.get(name='2021', league=league)

        teams_dict = {team.abbreviation: team for team in Team.objects.filter(league=league)}

        for row in range(2, sheet.max_row + 1):
            player_name = str(sheet['A' + str(row)].value)
            pick1 = str(sheet['B' + str(row)].value)
            over1 = True if str(sheet['C' + str(row)].value) == 'O' else False
            pick2 = str(sheet['D' + str(row)].value)
            over2 = True if str(sheet['E' + str(row)].value) == 'O' else False
            pick3 = str(sheet['F' + str(row)].value)
            over3 = True if str(sheet['G' + str(row)].value) == 'O' else False
            pick4 = str(sheet['H' + str(row)].value)
            over4 = True if str(sheet['I' + str(row)].value) == 'O' else False

            player, created = Player.objects.get_or_create(name=player_name)

            player_picks = player_picks + [
                Pick(player=player, season=season, team=teams_dict[pick1], over=over1),
                Pick(player=player, season=season, team=teams_dict[pick2], over=over2),
                Pick(player=player, season=season, team=teams_dict[pick3], over=over3),
                Pick(player=player, season=season, team=teams_dict[pick4], over=over4),
            ]

        return player_picks

    def _bulk_create_player_picks_from_excel(self, player_picks):
        Pick.objects.bulk_create(player_picks)

    def _read_over_under_line_from_excel(self, sheet):
        over_under_lines = []
        league = League.objects.get(name='NFL')
        season = Season.objects.get(name='2021', league=league)
        for row in range(2, sheet.max_row + 1):
            team_abbr = str(sheet['A' + str(row)].value)
            value = str(sheet['B' + str(row)].value)

            team = Team.objects.get(abbreviation=team_abbr, league=league)

            over_under_lines.append(OverUnderLine(team=team, line=value, season=season))

        print(over_under_lines)

        return over_under_lines

    def _bulk_create_over_under_lines(self, over_under_lines):
        OverUnderLine.objects.bulk_create(over_under_lines)

    #def _generate_key_name_output_workbook(self, keys_dict, file_name):
        #wb = openpyxl.Workbook()
        #sheet = wb['Sheet']

        #sheet['A1'] = 'name'
        #sheet['B1'] = 'id'
        #i = 2
        #for key_dict in keys_dict:
            #sheet['A' + str(i)] = key_dict['name']
            #sheet['B' + str(i)] = key_dict['id']
            #i += 1

        #wb.save(file_name)