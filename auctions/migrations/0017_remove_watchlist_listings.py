# Generated by Django 3.2 on 2021-05-24 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0016_watchlistitems'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='listings',
        ),
    ]
