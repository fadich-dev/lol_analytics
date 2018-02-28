from .models import Account, Champion, Match, League, SummonerLeague, MatchPlayer
from .api_external import RiotAPI
from django.utils import timezone

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
        self._update_matches()
        self._update_leagues()

    def is_updated(self):
        if not self._account.updated_at:
            return False

        return timezone.now().timestamp() - self._account.updated_at.timestamp() < 600

    def get_last_update(self):
        return self._account.updated_at.timestamp()

    def get_next_update(self):
        diff = timezone.now().timestamp() - self._account.updated_at.timestamp()
        return (0, 600 - diff)[diff < 600]

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
                champ = Champion.objects.get(champion_id=api_match['champion'])
                match = Match.objects.get_or_create(**filters)[0]
                MatchPlayer.objects.get_or_create(
                    account=self._account,
                    match=match,
                    champion=champ,
                    role=api_match['role'],
                    lane=api_match['lane']
                )

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
