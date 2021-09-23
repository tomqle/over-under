# Generated by Django 3.2.7 on 2021-09-11 16:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboard', '0003_auto_20210911_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverUnderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line', models.DecimalField(decimal_places=1, max_digits=3)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboard.team')),
            ],
        ),
    ]
