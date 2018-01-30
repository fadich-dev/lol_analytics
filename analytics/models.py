from django.db import models
import datetime

# Create your models here.


class Account(models.Model):
    name = models.CharField(max_length=255)
    server = models.CharField(max_length=32)
    account_id = models.IntegerField()
    summoner_id = models.IntegerField()
    icon_id = models.IntegerField()
    summoner_level = models.IntegerField()

    def __str__(self):
        return '%s (%s)' % (self.name, self.server)


class Champion(models.Model):
    champion_id = models.IntegerField()
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Match(models.Model):
    platform_id = models.CharField(max_length=32)
    game_id = models.BigIntegerField()
    champion = models.ManyToManyField(Champion)
    queue = models.IntegerField()
    season = models.BigIntegerField()
    timestamp = models.IntegerField()
    role = models.CharField(max_length=32)
    lane = models.CharField(max_length=32)
    account = models.ForeignKey(Account)

    def __str__(self):
        return '%s (%s)' % (self.account.name, datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M'))
