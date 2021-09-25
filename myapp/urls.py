"""myapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from leaderboard.views import DefaultOverUnderLineView, DefaultPicksView, DefaultRankingsView, DefaultStandingsView, HomeView, OverUnderLineView, PicksView, RankingsView, StandingsView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('over_under_lines/', DefaultOverUnderLineView.as_view(), name='default_over_under_lines'),
    path('over_under_lines/<str:league>/<str:season>/', OverUnderLineView.as_view(), name='over_under_lines'),
    path('picks/', DefaultPicksView.as_view(), name='default_picks'),
    path('picks/<str:league>/<str:season>/', PicksView.as_view(), name='picks'),
    path('rankings/', DefaultRankingsView.as_view(), name='default_rankings'),
    path('rankings/<str:league>/<str:season>/', RankingsView.as_view(), name='rankings'),
    path('standings/', DefaultStandingsView.as_view(), name='default_standings'),
    path('standings/<str:league>/<str:season>/', StandingsView.as_view(), name='standings'),
]
