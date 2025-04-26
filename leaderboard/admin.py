from django.contrib import admin

from leaderboard.models import League, OverUnderLine, Pick, Player, PlayerScore, Season, Team, TeamRecord

# Register your models here.

class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    readonly_fields = ['name', 'games_count']
    ordering = ['-name']

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    #list_display = ('name', 'created_at', 'updated_at', )
    readonly_fields = ['created_at', 'updated_at']

    inlines = [
        SeasonInline,
    ]

@admin.register(OverUnderLine)
class OverUnderLineAdmin(admin.ModelAdmin):
    list_display = ('season', 'team__name', 'line', 'diff', 'created_at', 'updated_at', )
    list_display_links = ('team__name', )
    list_filter = ['season__league__name', 'season__name', 'team__name']
    search_fields = ['team__name', 'season__name', 'season__league__name']
    readonly_fields = ['diff', 'created_at', 'updated_at']
    ordering = ['season__league__name', '-season__name', 'line']

@admin.register(Pick)
class PickAdmin(admin.ModelAdmin):
    list_display = ('player__name', 'team__name', 'season', 'over', 'created_at', 'updated_at', )
    list_display_links = ('player__name', )
    list_filter = ['season__league', 'season', 'team__name', 'player__name']
    search_fields = ['season__name', 'season__league__name', 'team__name', 'player__name']
    readonly_fields = ['points', 'created_at', 'updated_at']
    ordering = ['season__league__name', '-season__name', 'player__name']

class PlayerPickInline(admin.TabularInline):
    model = Pick
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['season__league__name', '-season__name', 'player__name']

class PlayerScoreInline(admin.TabularInline):
    model = PlayerScore
    extra = 0
    readonly_fields = ['score', 'created_at', 'updated_at']
    ordering = ['season__league__name', '-season__name', 'score']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', )
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    inlines = [
        PlayerScoreInline,
        PlayerPickInline,
    ]

@admin.register(PlayerScore)
class PlayerScoreAdmin(admin.ModelAdmin):
    list_display = ('player__name', 'season', 'score', )
    list_display_links = ('player__name', )
    list_filter = ['season__league__name', 'season__name', 'player__name']
    search_fields = ['season__league__name', 'season__name', 'player__name']
    readonly_fields = ['score']
    ordering = ['season__league__name', '-season__name', 'score']

class OverUnderLineInline(admin.TabularInline):
    model = OverUnderLine
    extra = 0
    readonly_fields = ['team', 'line', 'diff']
    ordering = ['-season__name', '-line']

class TeamRecordInline(admin.TabularInline):
    model = TeamRecord
    extra = 0
    readonly_fields = ['win_count', 'lose_count', 'tie_count']
    ordering = ['-season__name', '-win_count']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('league__name', 'name', 'games_count', 'created_at', 'updated_at')
    list_display_links = ('name', )
    list_filter = ['league__name', 'name']
    search_fields = ['name', 'league__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['league__name', '-name']

    inlines = [
        OverUnderLineInline,
        TeamRecordInline,
    ]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('league', 'name', 'abbreviation', 'created_at', 'updated_at', )
    list_display_links = ('name', 'abbreviation', )
    list_filter = ['league__name']
    search_fields = ['name', 'abbreviation', 'league__name']
    readonly_fields = ['league', 'created_at', 'updated_at']
    ordering = ['league__name', 'name']

    inlines = [
        TeamRecordInline,
        OverUnderLineInline,
    ]

@admin.register(TeamRecord)
class TeamRecordAdmin(admin.ModelAdmin):
    list_display = ('season', 'team', 'win_count', 'lose_count', 'tie_count', 'created_at', 'updated_at', )
    list_display_links = ('team', )
    list_filter = ['season__league__name', 'season__name']
    search_fields = ['team__name', 'season__name', 'season__league__name']
    readonly_fields = ['team', 'season', 'win_count', 'lose_count', 'tie_count', 'created_at', 'updated_at']
    ordering = ['-season', '-win_count']
