# Generated by Django 3.2.7 on 2021-09-11 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.league')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.league')),
            ],
        ),
        migrations.CreateModel(
            name='TeamRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('win_count', models.IntegerField()),
                ('lose_count', models.IntegerField()),
                ('tie_count', models.IntegerField()),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.team')),
            ],
        ),
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('over', models.BooleanField()),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.team')),
            ],
        ),
    ]
