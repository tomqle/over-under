# Generated by Django 5.1.7 on 2025-04-11 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0011_league_created_at_league_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='overunderline',
            name='line',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
