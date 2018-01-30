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

    def get_leagues(self):
        return [summoner_league.league for summoner_league in self.summonerleague_set.all()]

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
        time = datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M')
        return '%s (%s)' % (self.account.name, time)


class League(models.Model):
    league_id = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    tier = models.CharField(max_length=32)
    queue_type = models.CharField(max_length=64)
    rank = models.CharField(max_length=8)

    def __str__(self):
        return '%s %s (%s)' % (self.tier, self.rank, self.name)


class SummonerLeague(models.Model):
    league_points = models.SmallIntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    is_veteran = models.BooleanField()
    is_inactive = models.BooleanField()
    is_fresh_blood = models.BooleanField()
    is_hot_streak = models.BooleanField()
    account = models.ForeignKey(Account)
    league = models.ForeignKey(League)

    def __str__(self):
        return '%s - %s (%s %s)' % (self.account.name, self.league.name, self.league.tier, self.league.rank)

