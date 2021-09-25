from django.contrib import admin

from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, Season, Team, TeamRecord

# Register your models here.

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    pass

@admin.register(OverUnderLine)
class OverUnderLineAdmin(admin.ModelAdmin):
    pass

@admin.register(Pick)
class PickAdmin(admin.ModelAdmin):
    pass

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass

@admin.register(PlayerScore)
class PlayerScoreAdmin(admin.ModelAdmin):
    pass

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(TeamRecord)
class TeamRecordAdmin(admin.ModelAdmin):
    pass
