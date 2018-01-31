from .models import Account, Champion, Match, League, SummonerLeague
from .api import RiotAPI
from django.utils import timezone


class Updater:

    def __init__(self, account):
        """
        Collecting summoner data

        :param account: Account entity
        :type account: Account
        """
        self._account = account
        self._api = RiotAPI(self._account.server)

    def update_data(self):
        self._update_matches()
        self._account.updated_at = timezone.now()
        self._account.save()

    def is_updated(self):
        if not self._account.updated_at:
            return False

        return timezone.now().timestamp() - self._account.updated_at.timestamp() < 600

    def _update_matches(self):
        res = self._api.get_match_history(self._account.account_id)
        if res.status_code == 200:
            for match in res.json()['matches']:
                if self._account.match_set \
                        .filter(platform_id=match['platformId'], game_id=match['gameId'], queue=match['queue']).count():
                    continue

                champ = Champion.objects.get(champion_id=match['champion'])
                mtch = Match.objects.create(
                    platform_id=match['platformId'],
                    game_id=match['gameId'],
                    queue=match['queue'],
                    season=match['season'],
                    timestamp=int(match['timestamp'] / 1000),
                    role=match['role'],
                    lane=match['lane'],
                    account=self._account
                )
                mtch.champions.add(champ)

    def _update_leagues(self):
        res = self._api.get_leagues(self._account.summoner_id)
        if res.status_code == 200:
            for lg in res.json():
                if self._account.summonerleague_set.filter(league_id=lg['leagueId']).count():
                    continue

                league = League.objects.create(
                    league_id=lg['leagueId'],
                    name=lg['leagueName'],
                    tier=lg['tier'],
                    queue_type=lg['queueType'],
                    rank=lg['rank']
                )

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
