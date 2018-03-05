from .models import Account, Champion, Match, League, SummonerLeague, MatchPlayer
from .api_external import RiotAPI
from django.utils import timezone
# from time import sleep

# TODO: rework this (_update_leagues, for example)... :)


class Updater:

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
                match = Match.objects.get_or_create(**filters)[0]
                # sleep(3)
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

        MatchPlayer.objects.get_or_create(
            account=account,
            match=match,
            champion=champion,
            role=player['timeline']['role'],
            lane=player['timeline']['lane']
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
