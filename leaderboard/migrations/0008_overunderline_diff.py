# Generated by Django 3.2.7 on 2021-12-30 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0007_alter_playerscore_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='overunderline',
            name='diff',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=10),
        ),
    ]