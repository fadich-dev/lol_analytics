from django.db import models
import datetime

# Create your models here.


class Region(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region)
    account_id = models.IntegerField()
    summoner_id = models.IntegerField()
    icon_id = models.IntegerField(null=True)
    summoner_level = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)

    def get_leagues(self):
        return [summoner_league.league for summoner_league in self.summonerleague_set.all()]

    def get_matches(self):
        return [match_player.match for match_player in self.matchplayer_set.all()]

    def __str__(self):
        return '%s (%s)' % (self.name, self.region.name)


class Champion(models.Model):
    champion_id = models.IntegerField()
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Match(models.Model):
    platform_id = models.CharField(max_length=32)
    game_id = models.BigIntegerField()
    queue = models.IntegerField()
    season = models.BigIntegerField()
    timestamp = models.IntegerField()
    region = models.ForeignKey(Region)

    def __str__(self):
        return '%s, %s (%s)' % (
            self.region.name,
            self.get_time(),
            ', '.join(['{0} - {1}'.format(p.account.name, p.champion.name) for p in self.matchplayer_set.all()])
        )

    def get_time(self):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M')


class MatchPlayer(models.Model):
    account = models.ForeignKey(Account)
    match = models.ForeignKey(Match)
    champion = models.ForeignKey(Champion)

    role = models.CharField(max_length=32)
    lane = models.CharField(max_length=32)
    win = models.BooleanField(default=False)

    kills = models.SmallIntegerField(null=True)
    deaths = models.SmallIntegerField(null=True)
    assists = models.SmallIntegerField(null=True)
    largest_multi_kill = models.SmallIntegerField(null=True)
    largest_killing_spree = models.SmallIntegerField(null=True)
    killing_sprees = models.SmallIntegerField(null=True)
    double_kills = models.SmallIntegerField(null=True)
    triple_kills = models.SmallIntegerField(null=True)
    quadra_kills = models.SmallIntegerField(null=True)
    penta_kills = models.SmallIntegerField(null=True)
    first_blood_kill = models.BooleanField(default=False)
    first_blood_assist = models.BooleanField(default=False)
    turret_kills = models.SmallIntegerField(null=True)
    first_tower_kill = models.BooleanField(default=False)
    first_tower_assist = models.BooleanField(default=False)
    inhibitor_kills = models.SmallIntegerField(null=True)
    first_inhibitor_kill = models.BooleanField(default=False)
    first_inhibitor_assist = models.BooleanField(default=False)
    unreal_kills = models.SmallIntegerField(null=True)

    total_minions_killed = models.SmallIntegerField(null=True)
    neutral_minions_killed = models.SmallIntegerField(null=True)
    neutral_minions_killed_enemy_jungle = models.SmallIntegerField(null=True)

    total_damage_dealt = models.IntegerField(null=True)
    total_damage_dealt_to_champions = models.IntegerField(null=True)
    physical_damage_dealt = models.IntegerField(null=True)
    physical_damage_dealt_to_champions = models.IntegerField(null=True)
    largest_critical_strike = models.SmallIntegerField(null=True)
    magic_damage_dealt = models.IntegerField(null=True)
    magic_damage_dealt_to_champions = models.IntegerField(null=True)
    true_damage_dealt = models.IntegerField(null=True)
    true_damage_dealt_to_champions = models.IntegerField(null=True)
    damage_dealt_to_turrets = models.IntegerField(null=True)
    damage_dealt_to_objectives = models.IntegerField(null=True)

    total_damage_taken = models.IntegerField(null=True)
    physical_damage_taken = models.IntegerField(null=True)
    magical_damage_taken = models.IntegerField(null=True)
    true_damage_taken = models.IntegerField(null=True)
    damage_self_mitigated = models.IntegerField(null=True)
    total_heal = models.IntegerField(null=True)
    total_units_healed = models.SmallIntegerField(null=True)

    vision_score = models.SmallIntegerField(null=True)
    wards_placed = models.SmallIntegerField(null=True)
    wards_killed = models.SmallIntegerField(null=True)
    vision_wards_bought_in_game = models.SmallIntegerField(null=True)
    sight_wards_bought_in_game = models.SmallIntegerField(null=True)

    total_time_crowd_control_dealt = models.SmallIntegerField(null=True)
    longest_time_spent_living = models.SmallIntegerField(null=True)

    gold_spent = models.IntegerField(null=True)
    gold_earned = models.IntegerField(null=True)
    champ_level = models.SmallIntegerField(null=True)
    time_ccing_others = models.SmallIntegerField(null=True)

    def __str__(self):
        return '{a} - {c}, {ln} ({t})'.format(
            a=self.account.name,
            c=self.champion.name,
            t=self.match.get_time(),
            ln=self.lane.title()
        )


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

