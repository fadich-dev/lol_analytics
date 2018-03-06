from .models import Account, Champion, Match, League, SummonerLeague, MatchPlayer
from .api_external import RiotAPI
from django.utils import timezone
from time import sleep

# TODO: rework this (_update_leagues, for example)... :)


class Updater(object):

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

        return timezone.now().timestamp() - self._account.updated_at.timestamp() < 300

    def get_last_update(self):
        return self._account.updated_at.timestamp()

    def get_next_update(self):
        diff = timezone.now().timestamp() - self._account.updated_at.timestamp()
        return (0, 300 - diff)[diff < 300]

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
                    sleep(1)
                    self._update_match(match)

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
        champion = Champion.objects.filter(champion_id=player['championId']).first()

        if MatchPlayer.objects.filter(account=account, match=match).first():
            return

        MatchPlayer.objects.create(
            account=account,
            match=match,
            champion=champion,
            role=player['timeline']['role'],
            lane=player['timeline']['lane'],
            win=player['stats']['win'],
            kills=player['stats']['kills'],
            deaths=player['stats']['deaths'],
            assists=player['stats']['assists'],
            largest_multi_kill=player['stats']['largestMultiKill'],
            largest_killing_spree=player['stats']['largestKillingSpree'],
            killing_sprees=player['stats']['killingSprees'],
            double_kills=player['stats']['doubleKills'],
            triple_kills=player['stats']['tripleKills'],
            quadra_kills=player['stats']['quadraKills'],
            penta_kills=player['stats']['pentaKills'],
            first_blood_kill=player['stats']['firstBloodKill'],
            first_blood_assist=player['stats']['firstBloodAssist'],
            turret_kills=player['stats']['turretKills'],
            first_tower_kill=player['stats']['firstTowerKill'],
            first_tower_assist=player['stats']['firstTowerAssist'],
            inhibitor_kills=player['stats']['inhibitorKills'],
            first_inhibitor_kill=player['stats']['firstInhibitorKill'],
            first_inhibitor_assist=player['stats']['firstInhibitorAssist'],
            unreal_kills=player['stats']['unrealKills'],
            total_minions_killed=player['stats']['totalMinionsKilled'],
            neutral_minions_killed=player['stats']['neutralMinionsKilled'],
            neutral_minions_killed_enemy_jungle=player['stats']['neutralMinionsKilledEnemyJungle'],
            total_damage_dealt=player['stats']['totalDamageDealt'],
            total_damage_dealt_to_champions=player['stats']['totalDamageDealtToChampions'],
            physical_damage_dealt=player['stats']['physicalDamageDealt'],
            physical_damage_dealt_to_champions=player['stats']['physicalDamageDealtToChampions'],
            largest_critical_strike=player['stats']['largestCriticalStrike'],
            magic_damage_dealt=player['stats']['magicDamageDealt'],
            magic_damage_dealt_to_champions=player['stats']['magicDamageDealtToChampions'],
            true_damage_dealt=player['stats']['trueDamageDealt'],
            true_damage_dealt_to_champions=player['stats']['trueDamageDealtToChampions'],
            damage_dealt_to_turrets=player['stats']['damageDealtToTurrets'],
            damage_dealt_to_objectives=player['stats']['damageDealtToObjectives'],
            total_damage_taken=player['stats']['totalDamageTaken'],
            physical_damage_taken=player['stats']['physicalDamageTaken'],
            magical_damage_taken=player['stats']['magicalDamageTaken'],
            true_damage_taken=player['stats']['trueDamageTaken'],
            damage_self_mitigated=player['stats']['damageSelfMitigated'],
            total_heal=player['stats']['totalHeal'],
            total_units_healed=player['stats']['totalUnitsHealed'],
            vision_score=player['stats']['visionScore'],
            wards_placed=player['stats']['wardsPlaced'],
            wards_killed=player['stats']['wardsKilled'],
            vision_wards_bought_in_game=player['stats']['visionWardsBoughtInGame'],
            sight_wards_bought_in_game=player['stats']['sightWardsBoughtInGame'],
            total_time_crowd_control_dealt=player['stats']['totalTimeCrowdControlDealt'],
            longest_time_spent_living=player['stats']['longestTimeSpentLiving'],
            gold_spent=player['stats']['goldSpent'],
            gold_earned=player['stats']['goldEarned'],
            champ_level=player['stats']['champLevel'],
            time_ccing_others=player['stats']['timeCCingOthers'],
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
