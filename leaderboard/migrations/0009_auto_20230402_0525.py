# Generated by Django 3.2.7 on 2023-04-02 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0008_overunderline_diff'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='games_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='season',
            name='games_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
