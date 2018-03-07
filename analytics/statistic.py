from .models import Account, Champion, Match, League, SummonerLeague, MatchPlayer
from .api_external import RiotAPI
from django.utils import timezone
from django.db.models import Avg, Sum
from time import sleep

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
    def __init__(self, account):
        self._account = account

    def get_avg(self):
        filtered = MatchPlayer.objects.filter(account=self._account)
        kills = filtered.aggregate(Sum('kills'))
        assists = filtered.aggregate(Sum('assists'))
        deaths = filtered.aggregate(Sum('deaths'))
        avg = {
            'kills': {**filtered.aggregate(Avg('kills')), **kills},
            'deaths': {**filtered.aggregate(Avg('deaths')), **deaths},
            'assists': {**filtered.aggregate(Avg('assists')), **assists},
            'kda': {
                'kda__avg': (kills.get('kills__sum') + assists.get('assists__sum')) / deaths.get('deaths__sum')
            },
        }

        return avg
