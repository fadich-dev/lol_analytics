from .models import Account, Champion, Match, League, SummonerLeague, MatchPlayer
from .api_external import RiotAPI
from django.utils import timezone
from django.db.models import Avg, Sum
from collections import Counter


# TODO: rework this (_update_leagues, for example)... :)


class Updater(object):
    UPDATE_LIMIT = 60

    def __init__(self, account):
        """
        Collecting summoner data

        :param account: Account entity
        :type account: Account
        """
        self._account = account
        self._api = RiotAPI(self._account.region.name)

    def update_data(self):
        self._account.updated_at = timezone.now()
        self._account.save()
        self._update_leagues()
        self._update_matches()

    def is_updated(self):
        if not self._account.updated_at:
            return False

        return timezone.now().timestamp() - self._account.updated_at.timestamp() < self.UPDATE_LIMIT

    def get_last_update(self):
        return self._account.updated_at.timestamp()

    def get_next_update(self):
        diff = timezone.now().timestamp() - self._account.updated_at.timestamp()
        return (0, self.UPDATE_LIMIT - diff)[diff < self.UPDATE_LIMIT]

    def _update_matches(self):
        res = self._api.get_match_history(self._account.account_id)
        if res.status_code == 200:
            for api_match in res.json()['matches']:
                filters = {
                    'platform_id': api_match['platformId'],
                    'game_id': api_match['gameId'],
                    'queue': api_match['queue'],
                    'season': api_match['season'],
                    'timestamp': int(api_match['timestamp'] / 1000),
                    'region': self._account.region,
                }
                match = Match.objects.filter(**filters).first()
                if not match:
                    match = Match.objects.create(**filters)
                    # sleep(1)

                    # try:
                    self._update_match(match)
                    # except Exception as e:
                    #     pass

    def _update_match(self, match):
        res = self._api.get_match(match.game_id)
        if res.status_code == 200:
            info = res.json()
            players = info['participantIdentities']
            for player in players:
                participant_id = player['participantId']
                participant = info['participants'][participant_id - 1]
                self._update_match_player(match, {**player['player'], **participant})

    def _update_match_player(self, match, player):
        account = self._update_match_account(player, self._account.region)

        if MatchPlayer.objects.filter(account=account, match=match).first():
            return

        champion = Champion.objects.filter(champion_id=player['championId']).first()

        kills = player['stats'].get('kills', 0)
        deaths = player['stats'].get('deaths', 0)
        assists = player['stats'].get('assists', 0)
        kda = (kills + assists) / (deaths or 1)

        MatchPlayer.objects.create(
            account=account,
            match=match,
            champion=champion,
            role=player['timeline']['role'],
            lane=player['timeline']['lane'],

            win=player['stats'].get('win', False),
            kills=player['stats'].get('kills'),
            deaths=player['stats'].get('deaths'),
            assists=player['stats'].get('assists'),
            kda=kda,
            kda_perfect=not deaths,
            largest_multi_kill=player['stats'].get('largestMultiKill'),
            largest_killing_spree=player['stats'].get('largestKillingSpree'),
            killing_sprees=player['stats'].get('killingSprees'),
            double_kills=player['stats'].get('doubleKills'),
            triple_kills=player['stats'].get('tripleKills'),
            quadra_kills=player['stats'].get('quadraKills'),
            penta_kills=player['stats'].get('pentaKills'),
            first_blood_kill=player['stats'].get('firstBloodKill', False),
            first_blood_assist=player['stats'].get('firstBloodAssist', False),
            turret_kills=player['stats'].get('turretKills'),
            first_tower_kill=player['stats'].get('firstTowerKill', False),
            first_tower_assist=player['stats'].get('firstTowerAssist', False),
            inhibitor_kills=player['stats'].get('inhibitorKills'),
            first_inhibitor_kill=player['stats'].get('firstInhibitorKill', False),
            first_inhibitor_assist=player['stats'].get('firstInhibitorAssist', False),
            unreal_kills=player['stats'].get('unrealKills'),
            total_minions_killed=player['stats'].get('totalMinionsKilled'),
            neutral_minions_killed=player['stats'].get('neutralMinionsKilled'),
            neutral_minions_killed_enemy_jungle=player['stats'].get('neutralMinionsKilledEnemyJungle'),
            total_damage_dealt=player['stats'].get('totalDamageDealt'),
            total_damage_dealt_to_champions=player['stats'].get('totalDamageDealtToChampions'),
            physical_damage_dealt=player['stats'].get('physicalDamageDealt'),
            physical_damage_dealt_to_champions=player['stats'].get('physicalDamageDealtToChampions'),
            largest_critical_strike=player['stats'].get('largestCriticalStrike'),
            magic_damage_dealt=player['stats'].get('magicDamageDealt'),
            magic_damage_dealt_to_champions=player['stats'].get('magicDamageDealtToChampions'),
            true_damage_dealt=player['stats'].get('trueDamageDealt'),
            true_damage_dealt_to_champions=player['stats'].get('trueDamageDealtToChampions'),
            damage_dealt_to_turrets=player['stats'].get('damageDealtToTurrets'),
            damage_dealt_to_objectives=player['stats'].get('damageDealtToObjectives'),
            total_damage_taken=player['stats'].get('totalDamageTaken'),
            physical_damage_taken=player['stats'].get('physicalDamageTaken'),
            magical_damage_taken=player['stats'].get('magicalDamageTaken'),
            true_damage_taken=player['stats'].get('trueDamageTaken'),
            damage_self_mitigated=player['stats'].get('damageSelfMitigated'),
            total_heal=player['stats'].get('totalHeal'),
            total_units_healed=player['stats'].get('totalUnitsHealed'),
            vision_score=player['stats'].get('visionScore'),
            wards_placed=player['stats'].get('wardsPlaced'),
            wards_killed=player['stats'].get('wardsKilled'),
            vision_wards_bought_in_game=player['stats'].get('visionWardsBoughtInGame'),
            sight_wards_bought_in_game=player['stats'].get('sightWardsBoughtInGame'),
            total_time_crowd_control_dealt=player['stats'].get('totalTimeCrowdControlDealt'),
            longest_time_spent_living=player['stats'].get('longestTimeSpentLiving'),
            gold_spent=player['stats'].get('goldSpent'),
            gold_earned=player['stats'].get('goldEarned'),
            champ_level=player['stats'].get('champLevel'),
            time_ccing_others=player['stats'].get('timeCCingOthers'),
        )

    def _update_match_account(self, account, region):
        acc = Account.objects.filter(
            name=account['summonerName'],
            region=region
        ).first()

        if not acc:
            acc = Account.objects.create(
                name=account['summonerName'],
                region=region,
                account_id=account['currentAccountId'],
                summoner_id=account['summonerId'],
                icon_id=account['profileIcon']
            )

        return acc

    def _update_leagues(self):
        res = self._api.get_leagues(self._account.summoner_id)
        if res.status_code == 200:
            leagues = res.json()

            SummonerLeague.objects.filter(account=self._account).delete()
            for lg in leagues:
                league = League.objects.get_or_create(
                    league_id=lg['leagueId'],
                    tier=lg['tier'],
                    rank=lg['rank'],
                    name=lg['leagueName'],
                    queue_type=lg['queueType']
                )[0]

                SummonerLeague.objects.create(
                    league_points=lg['leaguePoints'],
                    wins=lg['wins'],
                    losses=lg['losses'],
                    is_veteran=lg['veteran'],
                    is_inactive=lg['inactive'],
                    is_fresh_blood=lg['freshBlood'],
                    is_hot_streak=lg['hotStreak'],
                    account=self._account,
                    league=league
                )


class Analyzer(object):
    _limit = 20
    _offset = 0

    def __init__(self, account, **kwargs):
        self._account = account
        self._filters = {'account': self._account, **kwargs}

    def set_limit(self, limit):
        self._limit = limit
        return self

    def set_offset(self, offset):
        self._offset = offset
        return self

    def get_full_analytics(self):
        return {
            **self.get_base_info(),
            **self.get_extra_info()
        }

    def get_base_info(self):
        avg = dict()
        filtered = MatchPlayer.objects.filter(**self._filters).order_by('-match__timestamp')[self._offset:self._limit]

        kills_sum = filtered.aggregate(Sum('kills')).get('kills__sum') or 0
        deaths_sum = filtered.aggregate(Sum('deaths')).get('deaths__sum') or 0
        assists_sum = filtered.aggregate(Sum('assists')).get('assists__sum') or 0

        # Match info
        avg['matches__sum'] = filtered.count()
        avg['wins__sum'] = MatchPlayer.objects.filter(win=True, **self._filters)[self._offset:self._limit].count()
        avg['loses__sum'] = avg['matches__sum'] - avg['wins__sum']
        avg['wins__avg'] = avg['wins__sum'] / (avg['matches__sum'] or 1)
        avg['loses__avg'] = avg['loses__sum'] / (avg['matches__sum'] or 1)

        # KDA info
        avg['kills__sum'] = kills_sum
        avg['deaths__sum'] = deaths_sum
        avg['assists__sum'] = assists_sum
        avg['kills__avg'] = filtered.aggregate(Avg('kills'))\
            .get('kills__avg')
        avg['deaths__avg'] = filtered.aggregate(Avg('deaths'))\
            .get('deaths__avg')
        avg['assists__avg'] = filtered.aggregate(Avg('assists'))\
            .get('assists__avg')
        avg['kda__avg'] = (kills_sum + assists_sum) / (deaths_sum or 1)
        avg['kda__perfect'] = not avg.get('deaths__sum')

        # Additional kills info
        avg['largest_multi_kill__avg'] = filtered.aggregate(Avg('largest_multi_kill'))\
            .get('largest_multi_kill__avg')
        avg['largest_killing_spree__avg'] = filtered.aggregate(Avg('largest_killing_spree'))\
            .get('largest_killing_spree__avg')
        avg['killing_sprees__avg'] = filtered.aggregate(Avg('killing_sprees'))\
            .get('killing_sprees__avg')
        avg['double_kills__avg'] = filtered.aggregate(Avg('double_kills'))\
            .get('double_kills__avg')
        avg['triple_kills__avg'] = filtered.aggregate(Avg('triple_kills'))\
            .get('triple_kills__avg')
        avg['quadra_kills__avg'] = filtered.aggregate(Avg('quadra_kills'))\
            .get('quadra_kills__avg')
        avg['penta_kills__avg'] = filtered.aggregate(Avg('penta_kills'))\
            .get('penta_kills__avg')
        avg['double_kills__sum'] = filtered.aggregate(Sum('double_kills'))\
            .get('double_kills__sum')
        avg['triple_kills__sum'] = filtered.aggregate(Sum('triple_kills'))\
            .get('triple_kills__sum')
        avg['quadra_kills__sum'] = filtered.aggregate(Sum('quadra_kills'))\
            .get('quadra_kills__sum')
        avg['penta_kills__sum'] = filtered.aggregate(Sum('penta_kills'))\
            .get('penta_kills__sum')
        avg['turret_kills__avg'] = filtered.aggregate(Avg('turret_kills'))\
            .get('turret_kills__avg')
        avg['inhibitor_kills__avg'] = filtered.aggregate(Avg('inhibitor_kills'))\
            .get('inhibitor_kills__avg')
        avg['unreal_kills__avg'] = filtered.aggregate(Avg('unreal_kills'))\
            .get('unreal_kills__avg')
        avg['total_minions_killed__avg'] = filtered.aggregate(Avg('total_minions_killed'))\
            .get('total_minions_killed__avg')
        avg['neutral_minions_killed__avg'] = filtered.aggregate(Avg('neutral_minions_killed'))\
            .get('neutral_minions_killed__avg')
        avg['neutral_minions_killed_enemy_jungle__avg'] = filtered.aggregate(Avg('neutral_minions_killed_enemy_jungle'))\
            .get('neutral_minions_killed_enemy_jungle__avg')

        # Damage info
        avg['total_damage_dealt__avg'] = filtered.aggregate(Avg('total_damage_dealt'))\
            .get('total_damage_dealt__avg')
        avg['total_damage_dealt_to_champions__avg'] = filtered.aggregate(Avg('total_damage_dealt_to_champions'))\
            .get('total_damage_dealt_to_champions__avg')
        avg['physical_damage_dealt__avg'] = filtered.aggregate(Avg('physical_damage_dealt'))\
            .get('physical_damage_dealt__avg')
        avg['physical_damage_dealt_to_champions__avg'] = filtered.aggregate(Avg('physical_damage_dealt_to_champions'))\
            .get('physical_damage_dealt_to_champions__avg')
        avg['largest_critical_strike__avg'] = filtered.aggregate(Avg('largest_critical_strike'))\
            .get('largest_critical_strike__avg')
        avg['magic_damage_dealt__avg'] = filtered.aggregate(Avg('magic_damage_dealt'))\
            .get('magic_damage_dealt__avg')
        avg['magic_damage_dealt_to_champions__avg'] = filtered.aggregate(Avg('magic_damage_dealt_to_champions'))\
            .get('magic_damage_dealt_to_champions__avg')
        avg['true_damage_dealt__avg'] = filtered.aggregate(Avg('true_damage_dealt'))\
            .get('true_damage_dealt__avg')
        avg['true_damage_dealt_to_champions__avg'] = filtered.aggregate(Avg('true_damage_dealt_to_champions'))\
            .get('true_damage_dealt_to_champions__avg')
        avg['damage_dealt_to_turrets__avg'] = filtered.aggregate(Avg('damage_dealt_to_turrets'))\
            .get('damage_dealt_to_turrets__avg')
        avg['damage_dealt_to_objectives__avg'] = filtered.aggregate(Avg('damage_dealt_to_objectives'))\
            .get('damage_dealt_to_objectives__avg')
        avg['total_damage_taken__avg'] = filtered.aggregate(Avg('total_damage_taken'))\
            .get('total_damage_taken__avg')
        avg['physical_damage_taken__avg'] = filtered.aggregate(Avg('physical_damage_taken'))\
            .get('physical_damage_taken__avg')
        avg['magical_damage_taken__avg'] = filtered.aggregate(Avg('magical_damage_taken'))\
            .get('magical_damage_taken__avg')
        avg['true_damage_taken__avg'] = filtered.aggregate(Avg('true_damage_taken'))\
            .get('true_damage_taken__avg')
        avg['damage_self_mitigated__avg'] = filtered.aggregate(Avg('damage_self_mitigated'))\
            .get('damage_self_mitigated__avg')
        avg['total_heal__avg'] = filtered.aggregate(Avg('total_heal'))\
            .get('total_heal__avg')
        avg['total_units_healed__avg'] = filtered.aggregate(Avg('total_units_healed'))\
            .get('total_units_healed__avg')

        # Common info
        avg['vision_score__avg'] = filtered.aggregate(Avg('vision_score'))\
            .get('vision_score__avg')
        avg['wards_placed__avg'] = filtered.aggregate(Avg('wards_placed'))\
            .get('wards_placed__avg')
        avg['wards_killed__avg'] = filtered.aggregate(Avg('wards_killed'))\
            .get('wards_killed__avg')
        avg['vision_wards_bought_in_game__avg'] = filtered.aggregate(Avg('vision_wards_bought_in_game'))\
            .get('vision_wards_bought_in_game__avg')
        avg['sight_wards_bought_in_game__avg'] = filtered.aggregate(Avg('sight_wards_bought_in_game'))\
            .get('sight_wards_bought_in_game__avg')
        avg['total_time_crowd_control_dealt__avg'] = filtered.aggregate(Avg('total_time_crowd_control_dealt'))\
            .get('total_time_crowd_control_dealt__avg')
        avg['longest_time_spent_living__avg'] = filtered.aggregate(Avg('longest_time_spent_living'))\
            .get('longest_time_spent_living__avg')
        avg['gold_spent__avg'] = filtered.aggregate(Avg('gold_spent'))\
            .get('gold_spent__avg')
        avg['gold_earned__avg'] = filtered.aggregate(Avg('gold_earned'))\
            .get('gold_earned__avg')
        avg['champ_level__avg'] = filtered.aggregate(Avg('champ_level'))\
            .get('champ_level__avg')
        avg['time_ccing_others__avg'] = filtered.aggregate(Avg('time_ccing_others'))\
            .get('time_ccing_others__avg')

        return avg

    def get_extra_info(self):
        extra = dict()
        filters = {'matchplayer__{k}'.format(k=key): val for key, val in self._filters.items()}
        matches = Match.objects.filter(**filters).order_by('-timestamp')[self._offset:self._limit]

        win_against_champs = list()
        lose_against_champs = list()

        for match in matches:
            cur = match.matchplayer_set.filter(account=self._account).first()
            list_to = win_against_champs if cur.win else lose_against_champs
            list_to += [info.champion.name for info in match.matchplayer_set.filter(win=not cur.win).all()]

        extra['win_against_champs'] = dict(Counter(win_against_champs).most_common(5))
        extra['lose_against_champs'] = dict(Counter(lose_against_champs).most_common(5))

        return extra